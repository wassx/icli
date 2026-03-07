#!/usr/bin/env python3
"""
Quickstart script for iCloud CLI - demonstrates functionality without interactive input
"""

from icli import iCloudCLI

def quickstart():
    """Demonstrate iCloud CLI functionality in a non-interactive way"""
    print("🚀 iCloud CLI Quickstart Demo")
    print("=" * 40)
    
    cli = iCloudCLI()
    
    # Demo mail functionality
    print("\n📧 Mail Module (Read-Only):")
    print("-" * 30)
    
    # Show email list
    print(f"Found {len(cli.mail.unread_emails)} unread emails")
    
    if cli.mail.unread_emails:
        email = cli.mail.unread_emails[0]
        print(f"\nFirst email preview:")
        print(f"  From: {email['from']}")
        print(f"  Subject: {email['subject']}")
        print(f"  Date: {email['date']}")
        print(f"  Preview: {email['preview']}")
    
    # Test send email (should be disabled)
    print(f"\n📧 Testing email sending:")
    result = cli.mail.send_email("test@example.com", "Test", "Test body")
    print(f"  Send result: {'❌ Disabled' if not result else '✅ Sent'}")
    
    # Demo calendar functionality
    print(f"\n📅 Calendar Module:")
    print("-" * 30)
    print("  ✅ Ready for implementation")
    cli.calendar.list_events()
    
    # Demo drive functionality
    print(f"\n💾 iCloud Drive Module:")
    print("-" * 30)
    print("  ✅ Ready for implementation")
    cli.drive.list_files()
    
    print(f"\n🎉 Quickstart completed!")
    print(f"\nTo use the interactive CLI, run:")
    print(f"  python main.py")
    print(f"\nFor read-only demo:")
    print(f"  python demo_readonly.py")

if __name__ == "__main__":
    quickstart()