"""Non-interactive, JSON-serialisable API for iCloud CLI.

All public methods return plain Python dicts / lists that can be passed
directly to ``json.dumps()``.  They raise ``RuntimeError`` or ``ValueError``
on failure and never call ``input()`` or print to stdout.

Typical scripting flow
----------------------
>>> from icli.api import ICloudAPI
>>> api = ICloudAPI()
>>> api.authenticate()                     # resumes from keyring
>>> api.list_calendars()
[{'id': 1, 'name': 'Work', ...}, ...]
>>> api.list_events(calendar_name='Work', days=7)
[{'title': 'Standup', 'start': '2026-03-09T09:00:00', ...}, ...]
>>> api.list_files(path='/')
[{'name': 'Documents', 'type': 'folder', ...}, ...]
>>> api.search_files(query='report', file_type='pdf')
[{'name': 'Q1 report.pdf', 'path': '/Documents/Q1 report.pdf', ...}, ...]
"""

import time


class ICloudAPI:
    """High-level iCloud API suitable for agents and shell scripts."""

    def __init__(self):
        from icli.auth import iCloudAuth
        from icli.drive import DriveModule
        from icli.calendar import CalendarModule
        from icli.mail import MailModule

        self.auth = iCloudAuth()
        self._drive = DriveModule(self.auth)
        self._calendar = CalendarModule(self.auth)
        self._mail = MailModule(self.auth)

    # ── Authentication ────────────────────────────────────────────────────────

    def authenticate(self, apple_id=None, password=None):
        """Authenticate non-interactively.

        Resolution order:
          1. ``apple_id`` / ``password`` keyword arguments
          2. ``ICLOUD_APPLE_ID`` / ``ICLOUD_PASSWORD`` environment variables
          3. Saved keyring entry → silent resume without any prompts

        Raises ``RuntimeError`` when authentication cannot complete without
        human interaction (e.g. first-time 2FA accounts).  Run
        ``python main.py auth login`` interactively once to store credentials
        in the system keyring; all subsequent calls will resume silently.
        """
        import os

        apple_id = apple_id or os.environ.get("ICLOUD_APPLE_ID")
        password = password or os.environ.get("ICLOUD_PASSWORD")

        # Silent keyring resume — preferred path for agents
        if self.auth.try_resume_session():
            return self.auth_status()

        # Look up keyring password when only apple_id is given
        if apple_id and not password:
            try:
                from icli.auth import KEYRING_AVAILABLE
                if KEYRING_AVAILABLE:
                    import keyring as _kr
                    password = _kr.get_password("iCloudCLI", apple_id)
            except Exception:
                pass

        if not apple_id or not password:
            raise RuntimeError(
                "Not authenticated and no credentials available. "
                "Run 'python main.py auth login' once interactively to save "
                "credentials to the system keyring, or supply --apple-id / "
                "--password (or ICLOUD_APPLE_ID / ICLOUD_PASSWORD env vars)."
            )

        ok = self.auth.login(apple_id=apple_id, password=password, use_keyring=True)
        if not ok:
            raise RuntimeError(
                "Authentication failed. Check credentials, or use "
                "'python main.py auth login' for interactive 2FA login."
            )
        return self.auth_status()

    def auth_status(self):
        """Return current authentication state.

        Returns dict with keys:
          authenticated (bool), apple_id (str|None), access (str|None),
          session_expires_in_seconds (int)  — only when authenticated
        """
        a = self.auth
        result = {
            "authenticated": a.is_authenticated(),
            "apple_id": a.apple_id,
            "access": "read-only" if a.is_authenticated() else None,
        }
        if a.session_expiry:
            remaining = max(0, a.session_expiry - time.time())
            result["session_expires_in_seconds"] = int(remaining)
        return result

    def logout(self):
        """Clear the session and remove saved keyring credentials.

        Returns ``{"ok": True, "message": "Logged out"}``.
        """
        self.auth.logout()
        return {"ok": True, "message": "Logged out"}

    # ── Calendar ──────────────────────────────────────────────────────────────

    def list_calendars(self):
        """Return all iCloud calendars as a list of dicts.

        Each dict: id (int), name (str), color (str), default (bool)
        """
        svc = self._require_calendar_service()
        calendars = svc.get_calendars(as_objs=True) or []
        return [
            {
                "id": i + 1,
                "name": c.title,
                "color": c.color,
                "default": bool(getattr(c, "is_default", False)),
            }
            for i, c in enumerate(calendars)
        ]

    def list_events(self, calendar_name=None, days=14):
        """Return upcoming events as a list of dicts.

        Args:
            calendar_name: Optional partial calendar name to filter by.
            days:          Look-ahead window in days (default 14).

        Each event dict: title, start (ISO str), end (ISO str), all_day,
        recurring, location, calendar
        """
        from datetime import datetime, timedelta

        svc = self._require_calendar_service()
        today = datetime.today()
        end = today + timedelta(days=days)

        target_guid = None
        if calendar_name:
            cals = svc.get_calendars(as_objs=True) or []
            matches = [c for c in cals if calendar_name.lower() in c.title.lower()]
            if not matches:
                raise ValueError(f"Calendar '{calendar_name}' not found")
            target_guid = matches[0].guid

        events = svc.get_events(from_dt=today, to_dt=end, as_objs=True) or []
        if target_guid:
            events = [e for e in events if getattr(e, "pguid", None) == target_guid]

        events.sort(key=lambda e: (e.start_date or datetime.min))
        return [_serialize_event(e) for e in events]

    # ── Drive ─────────────────────────────────────────────────────────────────

    def list_files(self, path="/"):
        """Return the contents of an iCloud Drive directory as a list of dicts.

        Args:
            path: Absolute iCloud Drive path (default ``/``).

        Each item dict: name, type (``file``|``folder``), path, size_bytes,
        size (human-readable string)
        """
        svc = self._require_drive_service()
        node = _traverse_path(svc, path)
        children = node.get_children() or []
        result = []
        for child in children:
            size = 0
            if hasattr(child, "data") and child.data:
                size = child.data.get("size", 0) or 0
            result.append(
                {
                    "name": child.name,
                    "type": child.type,
                    "path": f"{path.rstrip('/')}/{child.name}",
                    "size_bytes": size,
                    "size": _fmt_size(size),
                }
            )
        return result

    def search_files(self, query="", file_type=None, min_size=None, max_size=None):
        """Search iCloud Drive and return matching files as a list of dicts.

        Args:
            query:     Text to match in filenames (empty = match all).
            file_type: File extension filter, e.g. ``'pdf'``.
            min_size:  Minimum size in bytes.
            max_size:  Maximum size in bytes.

        Each item dict: name, path, size_bytes, size, type, extension
        """
        self._require_auth()
        raw = self._drive.search_files(
            query=query,
            file_type=file_type,
            min_size=min_size,
            max_size=max_size,
        )
        return [_clean_file(f) for f in raw]

    def download_file(self, remote_path, local_path=None):
        """Download a file from iCloud Drive to a local path.

        Args:
            remote_path: Absolute iCloud Drive path, e.g. ``'/Documents/report.pdf'``.
            local_path:  Local destination file or directory.  Defaults to the
                         file's original name in the current working directory.

        Returns dict with keys:
          ok (bool), local_path (str), size_bytes (int), size (str)

        On failure the dict has ``ok=False`` and an ``error`` key instead.
        """
        self._require_auth()
        return self._drive.download_file(remote_path, local_path)

    # ── Mail ──────────────────────────────────────────────────────────────────

    def list_mail_folders(self):
        """Return a list of mailbox folder names.

        Returns a list of strings, e.g. ``['INBOX', 'Sent Messages', 'Drafts', ...]``.
        """
        self._require_auth()
        return self._mail.list_folders()

    def list_emails(self, folder="INBOX", limit=20):
        """Fetch the latest *limit* email headers from *folder*.

        Returns a list of dicts (newest first):
          uid, subject, from_name, from_address, date, date_iso, seen
        """
        self._require_auth()
        return self._mail.list_emails(folder=folder, limit=limit)

    def get_email(self, uid, folder="INBOX"):
        """Fetch the full content of one email by UID.

        Returns a dict with:
          uid, subject, from_name, from_address, to, date, date_iso,
          body_text, body_html, attachments
        """
        self._require_auth()
        return self._mail.get_email(uid=uid, folder=folder)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _require_auth(self):
        if not self.auth.is_authenticated():
            raise RuntimeError(
                "Not authenticated. Run 'python main.py auth login' first."
            )

    def _require_calendar_service(self):
        self._require_auth()
        self.auth.check_session_activity()
        svc = self.auth.get_calendar_service()
        if not svc:
            raise RuntimeError("Calendar service unavailable")
        return svc

    def _require_drive_service(self):
        self._require_auth()
        self.auth.check_session_activity()
        svc = self.auth.get_drive_service()
        if not svc:
            raise RuntimeError("Drive service unavailable")
        return svc


# ── Serialisation helpers ─────────────────────────────────────────────────────

def _serialize_event(e):
    """Convert a pyicloud EventObject to a plain serialisable dict."""

    def _d(v):
        if v is None:
            return None
        # Apple 7-element date array  [YYYYMMDD, YYYY, MM, DD, HH, MM, ...]
        if isinstance(v, list) and len(v) >= 6:
            return f"{v[1]:04d}-{v[2]:02d}-{v[3]:02d}T{v[4]:02d}:{v[5]:02d}:00"
        if hasattr(v, "isoformat"):
            return v.isoformat()
        return str(v)

    return {
        "title": getattr(e, "title", None) or "Untitled",
        "start": _d(getattr(e, "start_date", None)),
        "end": _d(getattr(e, "end_date", None)),
        "all_day": bool(getattr(e, "all_day", False)),
        "recurring": bool(getattr(e, "recurrence_master", False)),
        "location": getattr(e, "location", None),
        "calendar": getattr(getattr(e, "calendar", None), "title", None),
    }


def _clean_file(f):
    """Strip non-serialisable node / object keys from a file info dict."""
    if not f:
        return {}
    return {
        k: v
        for k, v in f.items()
        if k not in ("node", "object") and not callable(v)
    }


def _traverse_path(drive_service, path):
    """Walk iCloud Drive from root to *path* and return that node.

    Raises ``ValueError`` if any path segment is not found.
    """
    if path in ("/", ""):
        return drive_service.root
    parts = [p for p in path.split("/") if p]
    node = drive_service.root
    for i, part in enumerate(parts):
        children = node.get_children()
        found = next((c for c in children if c.name == part), None)
        if not found:
            seg = "/" + "/".join(parts[: i + 1])
            raise ValueError(f"Path not found: {seg}")
        node = found
    return node


def _fmt_size(b):
    if not b:
        return "0 B"
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"
