"""Tests for icli.reminders — smoke tests that require no live CalDAV connection."""

import unittest
from unittest.mock import MagicMock, patch


class TestRemindersModuleImport(unittest.TestCase):
    def test_module_importable(self):
        from icli import reminders  # noqa: F401

    def test_class_exists(self):
        from icli.reminders import RemindersModule
        self.assertTrue(callable(RemindersModule))

    def test_caldav_auth_error_exists(self):
        from icli.reminders import _CalDAVAuthError
        self.assertTrue(issubclass(_CalDAVAuthError, RuntimeError))

    def test_parse_vtodo_helper(self):
        from icli.reminders import _parse_vtodo
        self.assertTrue(callable(_parse_vtodo))


class TestRemindersModuleMethods(unittest.TestCase):
    def setUp(self):
        from icli.reminders import RemindersModule
        mock_auth = MagicMock()
        mock_auth.is_authenticated.return_value = True
        mock_auth.apple_id = "test@icloud.com"
        self.rm = RemindersModule(mock_auth)

    def test_has_list_reminder_lists(self):
        self.assertTrue(callable(self.rm.list_reminder_lists))

    def test_has_list_reminders(self):
        self.assertTrue(callable(self.rm.list_reminders))

    def test_has_browse_reminders(self):
        self.assertTrue(callable(self.rm.browse_reminders))

    def test_has_browse_lists(self):
        self.assertTrue(callable(self.rm.browse_lists))

    def test_disconnect_resets_state(self):
        self.rm._client = "dummy"
        self.rm._principal = "dummy"
        self.rm.disconnect()
        self.assertIsNone(self.rm._client)
        self.assertIsNone(self.rm._principal)

    def test_get_password_env_mail(self):
        import os
        with patch.dict(os.environ, {"ICLOUD_MAIL_PASSWORD": "secret"}):
            self.assertEqual(self.rm._get_password(), "secret")

    def test_get_password_env_icloud(self):
        import os
        with patch.dict(os.environ, {"ICLOUD_MAIL_PASSWORD": "", "ICLOUD_PASSWORD": "fallback"}):
            self.assertEqual(self.rm._get_password(), "fallback")


class TestParseVTODO(unittest.TestCase):
    """Unit tests for the VTODO parser using synthetic iCalendar data."""

    BASIC_TODO = b"""BEGIN:VCALENDAR\r\nVERSION:2.0\r\nBEGIN:VTODO\r\nUID:abc-123\r\nSUMMARY:Buy groceries\r\nSTATUS:NEEDS-ACTION\r\nEND:VTODO\r\nEND:VCALENDAR\r\n"""

    COMPLETED_TODO = b"""BEGIN:VCALENDAR\r\nVERSION:2.0\r\nBEGIN:VTODO\r\nUID:def-456\r\nSUMMARY:Done task\r\nSTATUS:COMPLETED\r\nEND:VTODO\r\nEND:VCALENDAR\r\n"""

    TODO_WITH_DUE = b"""BEGIN:VCALENDAR\r\nVERSION:2.0\r\nBEGIN:VTODO\r\nUID:ghi-789\r\nSUMMARY:Pay bills\r\nSTATUS:NEEDS-ACTION\r\nDUE;VALUE=DATE:20261231\r\nPRIORITY:1\r\nEND:VTODO\r\nEND:VCALENDAR\r\n"""

    def test_basic_pending(self):
        from icli.reminders import _parse_vtodo
        result = _parse_vtodo(self.BASIC_TODO, "Test List")
        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "Buy groceries")
        self.assertEqual(result["status"], "NEEDS-ACTION")
        self.assertFalse(result["completed"])
        self.assertEqual(result["list_name"], "Test List")

    def test_completed(self):
        from icli.reminders import _parse_vtodo
        result = _parse_vtodo(self.COMPLETED_TODO, "Test List")
        self.assertIsNotNone(result)
        self.assertTrue(result["completed"])

    def test_due_date_and_priority(self):
        from icli.reminders import _parse_vtodo
        result = _parse_vtodo(self.TODO_WITH_DUE, "Bills")
        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "Pay bills")
        self.assertEqual(result["priority"], 1)
        self.assertIn("2026-12-31", result["due"])

    def test_invalid_ical_returns_none(self):
        from icli.reminders import _parse_vtodo
        result = _parse_vtodo(b"not valid ical data !!!", "List")
        self.assertIsNone(result)

    def test_no_vtodo_component_returns_none(self):
        vevent_data = (
            b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\n"
            b"BEGIN:VEVENT\r\nUID:x\r\nSUMMARY:Meeting\r\nEND:VEVENT\r\n"
            b"END:VCALENDAR\r\n"
        )
        from icli.reminders import _parse_vtodo
        result = _parse_vtodo(vevent_data, "List")
        self.assertIsNone(result)


class TestAPIReminders(unittest.TestCase):
    """Smoke tests for ICloudAPI reminders methods."""

    def test_api_has_list_reminder_lists(self):
        from icli.api import ICloudAPI
        self.assertTrue(callable(ICloudAPI.list_reminder_lists))

    def test_api_has_list_reminders(self):
        from icli.api import ICloudAPI
        self.assertTrue(callable(ICloudAPI.list_reminders))

    def test_api_requires_auth_for_reminders(self):
        from icli.api import ICloudAPI
        api = ICloudAPI()
        with self.assertRaises(RuntimeError):
            api.list_reminders()

    def test_api_requires_auth_for_lists(self):
        from icli.api import ICloudAPI
        api = ICloudAPI()
        with self.assertRaises(RuntimeError):
            api.list_reminder_lists()


class TestICloudCLIHasReminders(unittest.TestCase):
    def test_icl_has_reminders_attribute(self):
        from icli import iCloudCLI
        cli = iCloudCLI()
        self.assertTrue(hasattr(cli, "reminders"))
        from icli.reminders import RemindersModule
        self.assertIsInstance(cli.reminders, RemindersModule)


if __name__ == "__main__":
    unittest.main()
