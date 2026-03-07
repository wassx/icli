#!/usr/bin/env python3
"""Smoke tests for the mail module (import and structure only — no IMAP connection)."""

from icli.mail import MailModule


def test_import():
    """MailModule can be imported and instantiated without auth."""
    mail = MailModule()
    assert mail.auth is None
    assert mail._conn is None


def test_methods_exist():
    """Public API surface check."""
    mail = MailModule()
    for name in ("list_folders", "list_emails", "get_email",
                 "show_inbox", "browse_folders", "disconnect"):
        assert callable(getattr(mail, name, None)), f"Missing method: {name}"


def test_decode_header_plain():
    assert MailModule._decode_header("Hello World") == "Hello World"


def test_decode_header_empty():
    assert MailModule._decode_header("") == ""
    assert MailModule._decode_header(None) == ""


def test_format_size():
    assert MailModule._format_size(500) == "500.0 B"
    assert MailModule._format_size(1024) == "1.0 KB"
    assert MailModule._format_size(1048576) == "1.0 MB"


if __name__ == "__main__":
    test_import()
    test_methods_exist()
    test_decode_header_plain()
    test_decode_header_empty()
    test_format_size()
    print("✓ All mail smoke tests passed!")