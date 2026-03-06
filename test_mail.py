#!/usr/bin/env python3
"""Test script for mail functionality"""

import io
import sys
import email as email_lib
import imaplib
from unittest.mock import MagicMock, patch

from icli.mail import MailModule


def test_mail_unauthenticated():
    """list_emails() without auth prints the right message and stops."""
    print("1. Testing list_emails() when not authenticated:")
    print("-" * 50)
    mail = MailModule()  # no auth
    captured = io.StringIO()
    with patch('sys.stdout', captured):
        mail.list_emails()
    out = captured.getvalue()
    assert "Not authenticated" in out or "No unread emails" in out, (
        f"Unexpected output: {out!r}"
    )
    print("   ✓ Unauthenticated case handled correctly")


def test_mail_imap_fallback():
    """When pyicloud has no mail service, emails are loaded via IMAP."""
    print("\n2. Testing IMAP fallback when pyicloud lacks mail service:")
    print("-" * 50)

    # Build a minimal RFC 822 message
    raw_msg = (
        b"From: sender@example.com\r\n"
        b"Subject: Hello IMAP\r\n"
        b"Date: Fri, 06 Mar 2026 12:00:00 +0000\r\n"
        b"Content-Type: text/plain\r\n\r\n"
        b"This is the email body."
    )

    # Mock auth: authenticated, no pyicloud mail service
    mock_auth = MagicMock()
    mock_auth.is_authenticated.return_value = True
    mock_auth.apple_id = "user@icloud.com"
    mock_auth.check_session_activity.return_value = True
    mock_auth.get_mail_service.return_value = None  # pyicloud has no mail

    # Mock IMAP4_SSL connection
    mock_conn = MagicMock()
    mock_conn.search.return_value = ('OK', [b'1'])
    mock_conn.fetch.return_value = ('OK', [(b'1 (RFC822 {N})', raw_msg)])

    mail = MailModule(auth=mock_auth)

    with patch('icli.mail._keyring', None, create=True), \
         patch('icli.mail._KEYRING_AVAILABLE', False), \
         patch('icli.mail.imaplib.IMAP4_SSL', return_value=mock_conn), \
         patch('icli.mail.getpass.getpass', return_value='app-specific-pw'), \
         patch('builtins.input', return_value='q'):
        mail.list_emails()

    assert len(mail.unread_emails) == 1
    em = mail.unread_emails[0]
    assert em['from'] == 'sender@example.com'
    assert em['subject'] == 'Hello IMAP'
    assert 'email body' in em['body']
    print("   ✓ IMAP fallback loaded emails correctly")


def test_mail_imap_login_failure():
    """A bad app-specific password clears the cache and shows a helpful message."""
    print("\n3. Testing IMAP login failure handling:")
    print("-" * 50)

    mock_auth = MagicMock()
    mock_auth.is_authenticated.return_value = True
    mock_auth.apple_id = "user@icloud.com"
    mock_auth.check_session_activity.return_value = True
    mock_auth.get_mail_service.return_value = None

    mock_conn = MagicMock()
    mock_conn.login.side_effect = imaplib.IMAP4.error("Login failed")

    mail = MailModule(auth=mock_auth)
    cleared = []

    with patch('icli.mail._KEYRING_AVAILABLE', False), \
         patch('icli.mail.imaplib.IMAP4_SSL', return_value=mock_conn), \
         patch('icli.mail.getpass.getpass', return_value='bad-pw') as _gp, \
         patch.object(mail, '_clear_imap_password', side_effect=cleared.append):

        captured = io.StringIO()
        with patch('sys.stdout', captured):
            mail._load_emails_via_imap()

    out = captured.getvalue()
    assert "Login failed" in out or "app-specific password" in out, (
        f"Unexpected output: {out!r}"
    )
    assert cleared  # _clear_imap_password was called
    print("   ✓ Login failure handled correctly")


def test_send_email_disabled():
    """send_email() is disabled in read-only mode."""
    print("\n4. Testing send_email() is disabled:")
    print("-" * 50)
    mail = MailModule()
    result = mail.send_email("test@example.com", "Test Subject", "Body")
    assert result is False
    print("   ✓ send_email() correctly disabled")


def test_mail_functionality():
    """Run all mail tests."""
    print("=== Testing Mail Functionality ===\n")
    test_mail_unauthenticated()
    test_mail_imap_fallback()
    test_mail_imap_login_failure()
    test_send_email_disabled()
    print("\n✓ Mail functionality test completed!")


if __name__ == "__main__":
    test_mail_functionality()