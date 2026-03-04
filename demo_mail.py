#!/usr/bin/env python3
"""Interactive demo of mail functionality"""

from icli.mail import MailModule

def demo_mail():
    """Demonstrate mail functionality interactively"""
    print("=== iCloud CLI - Mail Demo ===\n")
    
    mail = MailModule()
    
    print("This demo shows the mail functionality with mock data.\n")
    print("You'll see:")
    print("1. List of unread emails with quick overview")
    print("2. Option to read an email in detail")
    print("3. Email detail view with full content")
    print("4. Options to manage the email (mark as read, etc.)\n")
    
    print("Starting demo...\n")
    
    # Simulate a typical user flow
    print("=== Step 1: List unread emails ===\n")
    
    # We'll use a simple approach - just call the method and let it handle input
    # For demo purposes, we'll simulate reading the first email and marking as read
    import sys
    
    # Save original stdin
    original_stdin = sys.stdin
    
    try:
        # Simulate user choosing email 1, then option 4 (mark as read), then option 5 (back)
        demo_input = "1\n4\n5\nq\n"
        sys.stdin = __import__('io').StringIO(demo_input)
        
        mail.list_emails()
        
    except EOFError:
        pass
    finally:
        sys.stdin = original_stdin
    
    print("\n=== Demo completed! ===")
    print("\nThe mail module now provides:")
    print("✓ Quick overview of unread emails with sender, subject, date, and preview")
    print("✓ Detailed view of individual emails")
    print("✓ Options to manage emails (reply, forward, delete, mark as read)")
    print("✓ Send email functionality")
    print("\nNext steps would be to:")
    print("1. Connect to actual iCloud mail API")
    print("2. Implement real email fetching and sending")
    print("3. Add authentication")
    print("4. Add more email management features")

if __name__ == "__main__":
    demo_mail()