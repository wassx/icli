"""Mail module for iCloud CLI"""

import imaplib
import email as email_lib
import getpass

ICLOUD_IMAP_HOST = "imap.mail.me.com"
ICLOUD_IMAP_PORT = 993

try:
    import keyring as _keyring
    _KEYRING_AVAILABLE = True
except ImportError:
    _KEYRING_AVAILABLE = False


class MailModule:
    def __init__(self, auth=None):
        self.auth = auth
        self.unread_emails = []
        self._use_real_data = True  # Always use real data (demo mode removed)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_imap_password(self, apple_id):
        """Return the IMAP app-specific password, prompting the user if needed."""
        if _KEYRING_AVAILABLE:
            try:
                saved = _keyring.get_password("iCloudCLI_imap", apple_id)
                if saved:
                    return saved
            except Exception:
                pass

        print("\n📬 iCloud Mail requires an app-specific password for IMAP access.")
        print("   Generate one at: appleid.apple.com → Security → App-Specific Passwords")
        try:
            imap_password = getpass.getpass("   Enter app-specific password: ").strip()
        except Exception:
            imap_password = input("   Enter app-specific password: ").strip()

        if not imap_password:
            print("❌ Password cannot be empty")
            return None

        if _KEYRING_AVAILABLE:
            try:
                _keyring.set_password("iCloudCLI_imap", apple_id, imap_password)
            except Exception:
                pass

        return imap_password

    def _clear_imap_password(self, apple_id):
        """Remove a cached IMAP password from the keyring."""
        if _KEYRING_AVAILABLE:
            try:
                _keyring.delete_password("iCloudCLI_imap", apple_id)
            except Exception:
                pass

    def _extract_body(self, parsed_msg):
        """Extract plain-text body from a parsed email message."""
        body = ""
        if parsed_msg.is_multipart():
            for part in parsed_msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode(
                            part.get_content_charset() or "utf-8", errors="replace"
                        )
                    except Exception:
                        pass
                    break
        else:
            try:
                body = parsed_msg.get_payload(decode=True).decode(
                    parsed_msg.get_content_charset() or "utf-8", errors="replace"
                )
            except Exception:
                pass
        return body

    # ------------------------------------------------------------------
    # Loading emails
    # ------------------------------------------------------------------

    def _load_emails_via_pyicloud(self, mail_service):
        """Load emails using a pyicloud mail service object (future support)."""
        try:
            inbox = mail_service.inbox
            self.unread_emails = []

            for email in inbox:
                if not email.read:
                    self.unread_emails.append({
                        "id": email.id,
                        "from": email.sender,
                        "subject": email.subject,
                        "date": email.date.strftime("%Y-%m-%d %H:%M:%S"),
                        "preview": email.preview,
                        "body": email.plain_text_body if hasattr(email, 'plain_text_body') else ""
                    })
        except AttributeError as e:
            print(f"❌ Mail service API has changed: {str(e)}")
            print("   Please check your pyicloud version and update if needed")

    def _load_emails_via_imap(self):
        """Load unread emails from iCloud using IMAP."""
        apple_id = self.auth.apple_id
        if not apple_id:
            print("❌ Apple ID not available")
            return

        imap_password = self._get_imap_password(apple_id)
        if not imap_password:
            return

        try:
            print("📬 Connecting to iCloud Mail...")
            conn = imaplib.IMAP4_SSL(ICLOUD_IMAP_HOST, ICLOUD_IMAP_PORT)
            conn.login(apple_id, imap_password)
            conn.select("INBOX")

            status, messages = conn.search(None, 'UNSEEN')
            if status != 'OK' or not messages[0]:
                conn.logout()
                return

            self.unread_emails = []
            for msg_id in messages[0].split()[:50]:  # cap at 50 to avoid slow fetches
                status, msg_data = conn.fetch(msg_id, '(RFC822)')
                if status != 'OK':
                    continue
                parsed = email_lib.message_from_bytes(msg_data[0][1])
                body = self._extract_body(parsed)
                self.unread_emails.append({
                    "id": msg_id.decode(),
                    "from": parsed.get("From", "Unknown"),
                    "subject": parsed.get("Subject", "(No Subject)"),
                    "date": parsed.get("Date", "Unknown"),
                    "preview": body[:100] if body else "",
                    "body": body
                })

            conn.logout()
            if self.unread_emails:
                print(f"Loaded {len(self.unread_emails)} unread emails from iCloud")

        except imaplib.IMAP4.error as e:
            error_msg = str(e).lower()
            if any(kw in error_msg for kw in ('login failed', 'authentication failed', 'invalid credentials')):
                print("❌ Login failed. Please check your app-specific password.")
                print("   Generate one at: appleid.apple.com → Security → App-Specific Passwords")
                self._clear_imap_password(apple_id)
            else:
                print(f"❌ IMAP error: {str(e)}")
        except Exception as e:
            print(f"❌ Error loading emails: {str(e)}")
            print("   Please check your internet connection and try again.")

    def _load_real_emails(self):
        """Load real emails from iCloud."""
        if not self.auth or not self.auth.is_authenticated():
            print("❌ Not authenticated. Please log in to access your iCloud data.")
            return

        try:
            mail_service = self.auth.get_mail_service()
            if mail_service:
                # Use pyicloud mail service if the library ever adds support
                self._load_emails_via_pyicloud(mail_service)
            else:
                # pyicloud doesn't expose iCloud Mail; fall back to IMAP
                self._load_emails_via_imap()
        except Exception as e:
            print(f"❌ Error loading real emails: {str(e)}")
            print("   Please check your internet connection and try again.")

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def list_emails(self):
        """List unread emails with quick overview"""
        # Check session activity first
        if self.auth:
            self.auth.check_session_activity()

        # Load real data if enabled
        if self._use_real_data:
            self._load_real_emails()

        if not self.unread_emails:
            print("No unread emails.")
            return

        print(f"\nYou have {len(self.unread_emails)} unread emails:\n")
        print("=" * 80)

        for i, email in enumerate(self.unread_emails, 1):
            print(f"{i}. FROM: {email['from']}")
            print(f"   SUBJECT: {email['subject']}")
            print(f"   DATE: {email['date']}")
            print(f"   PREVIEW: {email['preview']}")
            print("-" * 80)

        # Offer to read an email in detail
        self._offer_read_email()

    def _offer_read_email(self):
        """Offer to read a specific email in detail"""
        if not self.unread_emails:
            return

        choice = input("\nEnter email number to read in detail (or 'q' to quit): ").strip()

        if choice.lower() == 'q':
            return

        try:
            email_index = int(choice) - 1
            if 0 <= email_index < len(self.unread_emails):
                self.read_email_detail(email_index)
            else:
                print("Invalid email number.")
        except ValueError:
            print("Invalid input. Please enter a number or 'q' to quit.")

    def read_email_detail(self, email_index):
        """Read a specific email in detail"""
        if email_index < 0 or email_index >= len(self.unread_emails):
            print("Invalid email index.")
            return

        email = self.unread_emails[email_index]

        print("\n" + "=" * 80)
        print("EMAIL DETAIL")
        print("=" * 80)
        print(f"FROM: {email['from']}")
        print(f"SUBJECT: {email['subject']}")
        print(f"DATE: {email['date']}")
        print("\n" + "-" * 80)
        print("BODY:")
        print(email['body'])
        print("=" * 80)

        # Offer options after reading
        self._offer_email_options(email_index)

    def _offer_email_options(self, email_index):
        """Offer options after reading an email - READ-ONLY mode"""
        print("\nOptions (Read-Only Mode):")
        print("1. Mark as read")
        print("2. Back to email list")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            print("Email marked as read")
            # Remove from unread list
            del self.unread_emails[email_index]
        elif choice == "2":
            return
        else:
            print("Invalid choice")

        # Go back to email list if there are still emails
        if self.unread_emails:
            self.list_emails()

    def send_email(self, to, subject, body):
        """Send an email - DISABLED for read-only mode"""
        print("❌ Email sending is disabled in read-only mode")
        return False
