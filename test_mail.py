#!/usr/bin/env python3
"""Test script for mail functionality"""

from icli.mail import MailModule

def test_mail_functionality():
    """Test the mail module functionality"""
    print("=== Testing Mail Functionality ===\n")
    
    mail = MailModule()
    
    # Test listing emails
    print("1. Testing list_emails() with mock data:")
    print("-" * 50)
    
    # We'll simulate user input for testing
    import io
    import sys
    
    # Test case 1: List emails and read first one
    test_input_1 = "1\n4\n5\n"
    print(f"Simulating input: {repr(test_input_1)}")
    
    # Save original stdin
    original_stdin = sys.stdin
    try:
        sys.stdin = io.StringIO(test_input_1)
        mail.list_emails()
    except EOFError:
        pass  # Expected when using StringIO
    finally:
        sys.stdin = original_stdin
    
    print("\n2. Testing send_email():")
    print("-" * 50)
    mail.send_email("test@example.com", "Test Subject", "This is a test email body.")
    
    print("\n✓ Mail functionality test completed!")

if __name__ == "__main__":
    test_mail_functionality()