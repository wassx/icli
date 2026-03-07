"""Mail module for iCloud CLI — iCloud Mail via IMAP"""

import imaplib
import email
import email.header
import email.utils
import logging
import re
from datetime import datetime
from icli.utils import separator, Spinner

logger = logging.getLogger(__name__)


class IMAPAuthError(RuntimeError):
    """Raised when IMAP login fails due to bad credentials."""
    pass


class MailModule:
    """Read-only access to iCloud Mail via IMAP.

    Uses ``imap.mail.me.com:993`` with an app-specific password.
    The password is looked up from (in order):
      1. ``ICLOUD_MAIL_PASSWORD`` env var
      2. ``ICLOUD_PASSWORD`` env var
      3. Keyring service ``iCloudCLI-Mail``
      4. Keyring service ``iCloudCLI`` (shared with pyicloud auth)
    If none is found, interactive mode prompts the user to enter one.
    """

    IMAP_HOST = "imap.mail.me.com"
    IMAP_PORT = 993
    KEYRING_SERVICE = "iCloudCLI-Mail"

    def __init__(self, auth=None):
        self.auth = auth
        self._conn = None

    # ── Connection management ─────────────────────────────────────────────────

    def _connect(self):
        """Open an IMAP4_SSL connection if not already connected."""
        if self._conn is not None:
            try:
                self._conn.noop()
                return self._conn
            except Exception:
                self._conn = None

        if not self.auth or not self.auth.is_authenticated():
            raise RuntimeError("Not authenticated — run 'icli auth login' first")

        apple_id = self.auth.apple_id
        password = self._get_password()

        if not password:
            raise RuntimeError(
                "No mail password found.  iCloud Mail requires a dedicated "
                "app-specific password for IMAP access.\n"
                "   1. Go to https://appleid.apple.com → Sign-In & Security → App-Specific Passwords\n"
                "   2. Generate a new password labelled 'iCLI Mail'\n"
                "   3. Run 'icli' → iCloud Mail to enter it, or set ICLOUD_MAIL_PASSWORD env var"
            )

        conn = imaplib.IMAP4_SSL(self.IMAP_HOST, self.IMAP_PORT)
        try:
            status, _ = conn.login(apple_id, password)
        except imaplib.IMAP4.error as e:
            raise IMAPAuthError(f"IMAP authentication failed: {e}") from e
        if status != "OK":
            raise IMAPAuthError("IMAP login failed")
        self._conn = conn
        return conn

    def _get_password(self):
        """Retrieve the mail-specific password from keyring or environment."""
        import os

        # Mail-specific env var first
        pw = os.environ.get("ICLOUD_MAIL_PASSWORD")
        if pw:
            return pw

        # Fall back to general password env var
        pw = os.environ.get("ICLOUD_PASSWORD")
        if pw:
            return pw

        # Try mail-specific keyring entry
        try:
            import keyring
            pw = keyring.get_password(self.KEYRING_SERVICE, self.auth.apple_id)
            if pw:
                return pw
        except Exception:
            pass

        # Fall back to general keyring entry (may work if same app-specific pw)
        try:
            import keyring
            pw = keyring.get_password("iCloudCLI", self.auth.apple_id)
        except Exception:
            pw = None
        return pw

    def _save_password(self, password):
        """Save the mail password to keyring."""
        try:
            import keyring
            keyring.set_password(self.KEYRING_SERVICE, self.auth.apple_id, password)
            return True
        except Exception:
            return False

    def _prompt_and_save_password(self):
        """Interactively prompt for the mail app-specific password."""
        import getpass

        print("\n🔑 iCloud Mail requires a dedicated app-specific password.")
        print("   This may be the same one you used for login, or a new one.")
        print("   Generate one at: https://appleid.apple.com")
        print("   → Sign-In & Security → App-Specific Passwords")
        print()

        pw = getpass.getpass("   Enter app-specific password for Mail: ").strip()
        if not pw:
            return None

        # Test the password before saving
        try:
            conn = imaplib.IMAP4_SSL(self.IMAP_HOST, self.IMAP_PORT)
            status, _ = conn.login(self.auth.apple_id, pw)
            conn.logout()
            if status == "OK":
                if self._save_password(pw):
                    print("   ✅ Password verified and saved to keyring.")
                else:
                    print("   ✅ Password verified (could not save to keyring — will ask again next time).")
                return pw
            else:
                print("   ❌ Authentication failed. Check the password.")
                return None
        except imaplib.IMAP4.error as e:
            print(f"   ❌ Authentication failed: {e}")
            return None
        except Exception as e:
            print(f"   ❌ Connection error: {e}")
            return None

    def disconnect(self):
        """Close the IMAP connection."""
        if self._conn:
            try:
                self._conn.logout()
            except Exception:
                pass
            self._conn = None

    # ── Public API (non-interactive) ──────────────────────────────────────────

    def list_folders(self):
        """Return a list of mailbox folder names."""
        conn = self._connect()
        status, data = conn.list()
        if status != "OK":
            return []

        folders = []
        for item in data:
            if isinstance(item, bytes):
                # Parse: (\\HasNoChildren) "/" "INBOX"
                match = re.search(rb'"([^"]+)"\s*$', item)
                if match:
                    folders.append(match.group(1).decode("utf-8"))
                else:
                    # Fallback: last word
                    parts = item.decode("utf-8", errors="replace").split()
                    if parts:
                        folders.append(parts[-1].strip('"'))
        return sorted(folders)

    def list_emails(self, folder="INBOX", limit=20):
        """Fetch the latest *limit* email headers from *folder*.

        Returns a list of dicts (newest first):
          uid, subject, from_name, from_address, date, date_iso, seen
        """
        conn = self._connect()
        status, _ = conn.select(f'"{folder}"', readonly=True)
        if status != "OK":
            raise RuntimeError(f"Cannot open folder: {folder}")

        # Search for all messages
        status, msg_nums = conn.search(None, "ALL")
        if status != "OK" or not msg_nums[0]:
            return []

        ids = msg_nums[0].split()
        # Take the last N (most recent)
        ids = ids[-limit:]
        ids.reverse()  # newest first

        results = []
        # Fetch headers in one batch
        id_range = b",".join(ids)
        status, fetch_data = conn.fetch(id_range, "(UID FLAGS BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
        if status != "OK":
            return []

        i = 0
        while i < len(fetch_data):
            item = fetch_data[i]
            if isinstance(item, tuple) and len(item) == 2:
                meta_line = item[0].decode("utf-8", errors="replace")
                header_bytes = item[1]

                # Parse UID
                uid_match = re.search(r"UID (\d+)", meta_line)
                uid = uid_match.group(1) if uid_match else None

                # Parse FLAGS for seen/unseen
                seen = b"\\Seen" in item[0]

                # Parse header
                msg = email.message_from_bytes(header_bytes)
                subject = self._decode_header(msg.get("Subject", ""))
                from_raw = msg.get("From", "")
                from_name, from_addr = email.utils.parseaddr(from_raw)
                from_name = self._decode_header(from_name) or from_addr
                date_raw = msg.get("Date", "")
                date_parsed = email.utils.parsedate_to_datetime(date_raw) if date_raw else None

                results.append({
                    "uid": uid,
                    "subject": subject,
                    "from_name": from_name,
                    "from_address": from_addr,
                    "date": date_parsed.strftime("%Y-%m-%d %H:%M") if date_parsed else "",
                    "date_iso": date_parsed.isoformat() if date_parsed else "",
                    "seen": seen,
                })
            i += 1

        return results

    def get_email(self, uid, folder="INBOX"):
        """Fetch the full content of one email by UID.

        Returns a dict:
          uid, subject, from_name, from_address, to, date, date_iso,
          body_text, body_html, attachments (list of {filename, size})
        """
        conn = self._connect()
        status, _ = conn.select(f'"{folder}"', readonly=True)
        if status != "OK":
            raise RuntimeError(f"Cannot open folder: {folder}")

        status, data = conn.uid("FETCH", uid, "(BODY.PEEK[])")
        if status != "OK" or not data or data[0] is None:
            raise ValueError(f"Email UID {uid} not found in {folder}")

        raw = data[0][1] if isinstance(data[0], tuple) else data[0]
        msg = email.message_from_bytes(raw)

        subject = self._decode_header(msg.get("Subject", ""))
        from_name, from_addr = email.utils.parseaddr(msg.get("From", ""))
        from_name = self._decode_header(from_name) or from_addr
        to_raw = msg.get("To", "")
        date_raw = msg.get("Date", "")
        date_parsed = email.utils.parsedate_to_datetime(date_raw) if date_raw else None

        body_text = ""
        body_html = ""
        attachments = []

        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition", ""))

            if "attachment" in disposition:
                filename = part.get_filename() or "unnamed"
                filename = self._decode_header(filename)
                payload = part.get_payload(decode=True)
                attachments.append({
                    "filename": filename,
                    "size": len(payload) if payload else 0,
                    "content_type": content_type,
                })
            elif content_type == "text/plain" and not body_text:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    body_text = payload.decode(charset, errors="replace")
            elif content_type == "text/html" and not body_html:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    body_html = payload.decode(charset, errors="replace")

        return {
            "uid": uid,
            "subject": subject,
            "from_name": from_name,
            "from_address": from_addr,
            "to": to_raw,
            "date": date_parsed.strftime("%Y-%m-%d %H:%M") if date_parsed else "",
            "date_iso": date_parsed.isoformat() if date_parsed else "",
            "body_text": body_text,
            "body_html": body_html,
            "attachments": attachments,
        }

    # ── Interactive UI ────────────────────────────────────────────────────────

    def show_inbox(self):
        """Interactive inbox browser."""
        if not self.auth or not self.auth.is_authenticated():
            print("❌ Not authenticated. Please log in first.")
            return

        self.auth.check_session_activity()

        print("\n=== iCloud Mail ===")
        print("📧 Loading your inbox...")

        try:
            try:
                with Spinner("Connecting to iCloud Mail"):
                    emails = self.list_emails(folder="INBOX", limit=20)
            except IMAPAuthError:
                # Stored password didn't work — prompt for a new one
                pw = self._prompt_and_save_password()
                if not pw:
                    return
                self._conn = None
                with Spinner("Connecting to iCloud Mail"):
                    emails = self.list_emails(folder="INBOX", limit=20)

            if not emails:
                print("📭 Your inbox is empty.")
                return

            self._display_email_list(emails)

            while True:
                choice = input(
                    f"\nEnter email number (1-{len(emails)}) to read, "
                    "r=refresh, b/q=back: "
                ).strip().lower()

                if choice in ("b", "q"):
                    break
                elif choice == "r":
                    with Spinner("Refreshing inbox"):
                        emails = self.list_emails(folder="INBOX", limit=20)
                    self._display_email_list(emails)
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(emails):
                        self._display_full_email(emails[idx])
                    else:
                        print(f"❌ Invalid number. Enter 1-{len(emails)}.")
                else:
                    print("❌ Invalid input.")

        except RuntimeError as e:
            print(f"❌ {e}")
        except Exception as e:
            logger.debug("Mail error: %s", e, exc_info=True)
            print(f"❌ Could not connect to iCloud Mail: {e}")
        finally:
            self.disconnect()

    def browse_folders(self):
        """Interactive folder browser."""
        if not self.auth or not self.auth.is_authenticated():
            print("❌ Not authenticated. Please log in first.")
            return

        self.auth.check_session_activity()

        try:
            try:
                with Spinner("Loading mail folders"):
                    folders = self.list_folders()
            except IMAPAuthError:
                pw = self._prompt_and_save_password()
                if not pw:
                    return
                self._conn = None
                with Spinner("Loading mail folders"):
                    folders = self.list_folders()

            if not folders:
                print("❌ No folders found.")
                return

            print(f"\n📁 Mail Folders ({len(folders)}):")
            print(separator("-"))
            for i, name in enumerate(folders, 1):
                print(f"  {i:2d}. 📁 {name}")

            choice = input(
                f"\nEnter folder number (1-{len(folders)}) to browse, "
                "or b=back: "
            ).strip().lower()

            if choice == "b":
                return

            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(folders):
                    folder = folders[idx]
                    with Spinner(f"Loading {folder}"):
                        emails = self.list_emails(folder=folder, limit=20)

                    if not emails:
                        print(f"📭 {folder} is empty.")
                        return

                    self._display_email_list(emails, folder_name=folder)

                    while True:
                        inner = input(
                            f"\nEnter email number (1-{len(emails)}) to read, "
                            "b=back: "
                        ).strip().lower()
                        if inner == "b":
                            break
                        elif inner.isdigit():
                            ei = int(inner) - 1
                            if 0 <= ei < len(emails):
                                self._display_full_email(emails[ei], folder=folder)
                            else:
                                print(f"❌ Invalid number. Enter 1-{len(emails)}.")
                        else:
                            print("❌ Invalid input.")
                else:
                    print(f"❌ Invalid number. Enter 1-{len(folders)}.")

        except RuntimeError as e:
            print(f"❌ {e}")
        except Exception as e:
            logger.debug("Mail error: %s", e, exc_info=True)
            print(f"❌ Could not connect to iCloud Mail: {e}")
        finally:
            self.disconnect()

    # ── Display helpers ───────────────────────────────────────────────────────

    def _display_email_list(self, emails, folder_name="Inbox"):
        """Print a formatted email listing."""
        print(f"\n📧 {folder_name} — {len(emails)} most recent:")
        print(separator("-"))
        for i, e in enumerate(emails, 1):
            star = "★" if not e["seen"] else " "
            date = e["date"][:10] if e["date"] else "          "
            sender = e["from_name"][:25].ljust(25)
            subj = e["subject"][:50] or "(no subject)"
            print(f" {i:2d}. {star} {date}  {sender} {subj}")

    def _display_full_email(self, email_summary, folder="INBOX"):
        """Fetch and display a full email."""
        uid = email_summary.get("uid")
        if not uid:
            print("❌ Cannot read this email (no UID)")
            return

        try:
            with Spinner("Loading email"):
                full = self.get_email(uid, folder=folder)

            print(f"\n{separator('=')}")
            print(f"From:    {full['from_name']} <{full['from_address']}>")
            print(f"To:      {self._decode_header(full['to'])}")
            print(f"Date:    {full['date']}")
            print(f"Subject: {full['subject']}")
            if full["attachments"]:
                att_list = ", ".join(
                    f"{a['filename']} ({self._format_size(a['size'])})"
                    for a in full["attachments"]
                )
                print(f"Attach:  {att_list}")
            print(separator("-"))

            body = full["body_text"]
            if not body and full["body_html"]:
                body = self._strip_html(full["body_html"])
            if not body:
                body = "(no text content)"
            print(body.strip())
            print(separator("-"))

        except Exception as e:
            logger.debug("Error reading email: %s", e, exc_info=True)
            print(f"❌ Could not read email: {e}")

    # ── Utilities ─────────────────────────────────────────────────────────────

    @staticmethod
    def _decode_header(value):
        """Decode an RFC 2047 encoded header into a plain string."""
        if not value:
            return ""
        parts = email.header.decode_header(value)
        decoded = []
        for data, charset in parts:
            if isinstance(data, bytes):
                decoded.append(data.decode(charset or "utf-8", errors="replace"))
            else:
                decoded.append(data)
        return " ".join(decoded)

    @staticmethod
    def _format_size(size_bytes):
        """Human-readable file size."""
        for unit in ("B", "KB", "MB", "GB"):
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    @staticmethod
    def _strip_html(html):
        """Convert HTML to readable plain text (best-effort)."""
        import html as html_mod

        text = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.S | re.I)
        text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.S | re.I)
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
        text = re.sub(r"</(p|div|tr|li|h[1-6])>", "\n", text, flags=re.I)
        text = re.sub(r"<[^>]+>", "", text)
        text = html_mod.unescape(text)
        # Collapse runs of blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
