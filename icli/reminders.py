"""Reminders module for iCloud CLI — iCloud Reminders via CalDAV / VTODO"""

import logging
import warnings
from datetime import datetime, date

from icalendar import Calendar as iCal
from icli.utils import separator, Spinner

logger = logging.getLogger(__name__)

CALDAV_URL = "https://caldav.icloud.com"
KEYRING_SERVICE = "iCloudCLI-Mail"  # Same app-specific password as Mail


class RemindersModule:
    """Read-only access to iCloud Reminders via CalDAV.

    Uses the same app-specific password as the mail module
    (stored under the ``iCloudCLI-Mail`` keyring service or
    ``ICLOUD_MAIL_PASSWORD`` / ``ICLOUD_PASSWORD`` env vars).
    """

    def __init__(self, auth=None):
        self.auth = auth
        self._client = None
        self._principal = None

    # ── Connection ────────────────────────────────────────────────────────────

    def _connect(self):
        if self._principal is not None:
            return self._principal

        if not self.auth or not self.auth.is_authenticated():
            raise RuntimeError("Not authenticated — run 'icli auth login' first")

        pw = self._get_password()
        if not pw:
            raise RuntimeError(
                "No CalDAV password found.  iCloud Reminders requires an "
                "app-specific password.\n"
                "   1. Go to https://appleid.apple.com → Sign-In & Security → App-Specific Passwords\n"
                "   2. Generate a new password labelled 'iCLI'\n"
                "   3. Run 'icli' → iCloud Reminders to enter it, or set ICLOUD_MAIL_PASSWORD"
            )

        try:
            import caldav
        except ImportError:
            raise RuntimeError(
                "caldav library not installed.  Run: pip install caldav"
            )

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                client = caldav.DAVClient(
                    url=CALDAV_URL,
                    username=self.auth.apple_id,
                    password=pw,
                )
                principal = client.principal()
            except Exception as e:
                if "401" in str(e) or "Unauthorized" in str(e) or "AuthorizationError" in str(e):
                    raise _CalDAVAuthError(f"CalDAV authentication failed: {e}") from e
                raise RuntimeError(f"CalDAV connection failed: {e}") from e

        self._client = client
        self._principal = principal
        return principal

    def _get_password(self):
        import os
        pw = os.environ.get("ICLOUD_MAIL_PASSWORD")
        if pw:
            return pw
        pw = os.environ.get("ICLOUD_PASSWORD")
        if pw:
            return pw
        try:
            import keyring
            pw = keyring.get_password(KEYRING_SERVICE, self.auth.apple_id)
            if pw:
                return pw
        except Exception:
            pass
        try:
            import keyring
            pw = keyring.get_password("iCloudCLI", self.auth.apple_id)
        except Exception:
            pw = None
        return pw

    def _save_password(self, password):
        try:
            import keyring
            keyring.set_password(KEYRING_SERVICE, self.auth.apple_id, password)
            return True
        except Exception:
            return False

    def _prompt_and_save_password(self):
        import getpass
        import caldav

        print("\n🔑 iCloud Reminders requires an app-specific password.")
        print("   This is the same one used for iCloud Mail.")
        print("   Generate one at: https://appleid.apple.com")
        print("   → Sign-In & Security → App-Specific Passwords")
        print()
        pw = getpass.getpass("   Enter app-specific password: ").strip()
        if not pw:
            return None
        # Verify
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                client = caldav.DAVClient(url=CALDAV_URL, username=self.auth.apple_id, password=pw)
                client.principal()
            if self._save_password(pw):
                print("   ✅ Password verified and saved to keyring.")
            else:
                print("   ✅ Password verified (could not save to keyring).")
            return pw
        except Exception as e:
            print(f"   ❌ Authentication failed: {e}")
            return None

    def disconnect(self):
        self._client = None
        self._principal = None

    # ── Public API (non-interactive) ──────────────────────────────────────────

    def list_reminder_lists(self):
        """Return all Reminders lists as a list of dicts.

        Each dict: name (str), uid (str), count (int)
        """
        principal = self._connect()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cals = principal.calendars()

        result = []
        for cal in cals:
            comps = cal.get_supported_components() or []
            if "VTODO" not in comps:
                continue
            name = cal.get_display_name() or "Unnamed"
            result.append({"name": name, "uid": str(cal.url), "_cal": cal})
        return result

    def list_reminders(self, list_name=None, include_completed=False):
        """Return tasks from one or all reminder lists.

        Args:
            list_name:          Filter to this list name (case-insensitive substring).
            include_completed:  Include completed tasks (default False).

        Each task dict: uid, title, list_name, status, completed, due (ISO str | None),
        priority (0–9, 0=none), notes
        """
        lists = self.list_reminder_lists()
        if list_name:
            lists = [l for l in lists if list_name.lower() in l["name"].lower()]
            if not lists:
                raise ValueError(f"Reminder list '{list_name}' not found")

        tasks = []
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for lst in lists:
                cal = lst["_cal"]
                col = cal.objects()
                for obj in col:
                    try:
                        obj.load()
                        parsed = _parse_vtodo(obj.data, lst["name"])
                        if parsed is None:
                            continue
                        if not include_completed and parsed["completed"]:
                            continue
                        tasks.append(parsed)
                    except Exception as e:
                        logger.debug("Error parsing task: %s", e)

        tasks.sort(key=lambda t: (t["due"] or "9999", t["priority"] == 0, t["title"]))
        return tasks

    # ── Interactive UI ────────────────────────────────────────────────────────

    def browse_reminders(self):
        """Interactive reminders browser."""
        if not self.auth or not self.auth.is_authenticated():
            print("❌ Not authenticated. Please log in first.")
            return

        self.auth.check_session_activity()

        try:
            try:
                with Spinner("Loading reminders"):
                    lists = self.list_reminder_lists()
                    tasks = self.list_reminders()
            except _CalDAVAuthError:
                pw = self._prompt_and_save_password()
                if not pw:
                    return
                self.disconnect()
                with Spinner("Loading reminders"):
                    lists = self.list_reminder_lists()
                    tasks = self.list_reminders()

            if not tasks:
                print("\n📋 No pending reminders.")
                return

            self._display_task_list(tasks)

            while True:
                choice = input(
                    f"\nEnter task number (1-{len(tasks)}) for details, "
                    "r=refresh, b/q=back: "
                ).strip().lower()

                if choice in ("b", "q"):
                    break
                elif choice == "r":
                    self.disconnect()
                    with Spinner("Refreshing"):
                        lists = self.list_reminder_lists()
                        tasks = self.list_reminders()
                    self._display_task_list(tasks)
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(tasks):
                        self._display_task_detail(tasks[idx])
                    else:
                        print(f"❌ Invalid number. Enter 1-{len(tasks)}.")
                else:
                    print("❌ Invalid input.")

        except RuntimeError as e:
            print(f"❌ {e}")
        except Exception as e:
            logger.debug("Reminders error: %s", e, exc_info=True)
            print(f"❌ Could not load reminders: {e}")
        finally:
            self.disconnect()

    def browse_lists(self):
        """Interactive list browser — pick a list, then browse its tasks."""
        if not self.auth or not self.auth.is_authenticated():
            print("❌ Not authenticated. Please log in first.")
            return

        self.auth.check_session_activity()

        try:
            try:
                with Spinner("Loading reminder lists"):
                    lists = self.list_reminder_lists()
            except _CalDAVAuthError:
                pw = self._prompt_and_save_password()
                if not pw:
                    return
                self.disconnect()
                with Spinner("Loading reminder lists"):
                    lists = self.list_reminder_lists()

            if not lists:
                print("❌ No reminder lists found.")
                return

            print(f"\n📋 Reminder Lists ({len(lists)}):")
            print(separator("-"))
            for i, lst in enumerate(lists, 1):
                print(f"  {i:2d}. 📝 {lst['name']}")

            choice = input(
                f"\nEnter list number (1-{len(lists)}) to browse, "
                "or b=back: "
            ).strip().lower()

            if choice == "b":
                return

            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(lists):
                    lst = lists[idx]
                    with Spinner(f"Loading {lst['name']}"):
                        tasks = self.list_reminders(
                            list_name=lst["name"], include_completed=True
                        )

                    if not tasks:
                        print(f"📋 {lst['name']} has no tasks.")
                        return

                    self._display_task_list(tasks, list_name=lst["name"])

                    while True:
                        inner = input(
                            f"\nEnter task number (1-{len(tasks)}) for details, "
                            "b=back: "
                        ).strip().lower()
                        if inner == "b":
                            break
                        elif inner.isdigit():
                            i = int(inner) - 1
                            if 0 <= i < len(tasks):
                                self._display_task_detail(tasks[i])
                            else:
                                print(f"❌ Invalid number. Enter 1-{len(tasks)}.")
                        else:
                            print("❌ Invalid input.")
                else:
                    print(f"❌ Invalid number. Enter 1-{len(lists)}.")

        except RuntimeError as e:
            print(f"❌ {e}")
        except Exception as e:
            logger.debug("Reminders error: %s", e, exc_info=True)
            print(f"❌ Could not load reminder lists: {e}")
        finally:
            self.disconnect()

    # ── Display helpers ───────────────────────────────────────────────────────

    def _display_task_list(self, tasks, list_name="All lists"):
        print(f"\n📋 {list_name} — {len(tasks)} task(s):")
        print(separator("-"))
        for i, t in enumerate(tasks, 1):
            done = "✅" if t["completed"] else "⬜"
            due = f"  📅 {t['due'][:10]}" if t.get("due") else ""
            prio = "  ❗" if t.get("priority", 0) in (1, 2, 3, 4, 5) else ""
            list_tag = f"  [{t['list_name']}]" if list_name == "All lists" else ""
            print(f" {i:2d}. {done} {t['title']}{prio}{due}{list_tag}")

    def _display_task_detail(self, task):
        print(f"\n{separator('=')}")
        status = "✅ Completed" if task["completed"] else "⬜ Pending"
        print(f"Title:    {task['title']}")
        print(f"Status:   {status}")
        print(f"List:     {task['list_name']}")
        if task.get("due"):
            print(f"Due:      {task['due']}")
        if task.get("priority") and task["priority"] > 0:
            labels = {1: "High", 2: "High", 3: "High", 4: "High", 5: "Medium",
                      6: "Low", 7: "Low", 8: "Low", 9: "Low"}
            print(f"Priority: {labels.get(task['priority'], str(task['priority']))}")
        if task.get("notes"):
            print(separator("-"))
            print(task["notes"].strip())
        print(separator("-"))


# ── Private helpers ───────────────────────────────────────────────────────────

class _CalDAVAuthError(RuntimeError):
    pass


def _parse_vtodo(ical_data, list_name):
    """Parse a VTODO iCalendar component into a plain dict."""
    try:
        cal = iCal.from_ical(ical_data)
    except Exception:
        return None

    for comp in cal.walk():
        if comp.name != "VTODO":
            continue

        uid = str(comp.get("UID", ""))
        title = str(comp.get("SUMMARY", "(no title)"))
        status = str(comp.get("STATUS", "NEEDS-ACTION")).upper()
        completed = status == "COMPLETED"
        priority = int(comp.get("PRIORITY", 0) or 0)
        notes = str(comp.get("DESCRIPTION", "") or "")

        due_raw = comp.get("DUE")
        due_str = None
        if due_raw is not None:
            val = due_raw.dt if hasattr(due_raw, "dt") else due_raw
            if isinstance(val, datetime):
                due_str = val.isoformat()
            elif isinstance(val, date):
                due_str = val.isoformat()
            else:
                due_str = str(val)

        return {
            "uid": uid,
            "title": title,
            "list_name": list_name,
            "status": status,
            "completed": completed,
            "due": due_str,
            "priority": priority,
            "notes": notes,
        }

    return None
