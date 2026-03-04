#!/usr/bin/env python3
"""
Debug authentication issues
"""

from icli import iCloudCLI

def debug_authentication():
    """Debug authentication issues"""
    print("=== Debugging Authentication ===\n")
    
    cli = iCloudCLI()
    
    # Check current state
    print("1. Current Authentication State:")
    print(f"   is_authenticated(): {cli.auth.is_authenticated()}")
    print(f"   apple_id: {cli.auth.apple_id}")
    print(f"   service: {cli.auth.service is not None}")
    print(f"   session_token: {cli.auth.session_token}")
    print(f"   session_expiry: {cli.auth.session_expiry}")
    print()
    
    # Check if pyicloud is available
    print("2. Dependency Check:")
    try:
        from pyicloud import PyiCloudService
        print("   ✅ pyicloud is available")
        print(f"   Version: {getattr(PyiCloudService, '__version__', 'unknown')}")
    except ImportError:
        print("   ❌ pyicloud is NOT available")
        print("   Please install: pip install pyicloud")
    print()
    
    # Check keyring
    try:
        import keyring
        print("   ✅ keyring is available")
    except ImportError:
        print("   ❌ keyring is NOT available")
        print("   Please install: pip install keyring")
    print()
    
    # Try to resume session if credentials are saved
    print("3. Trying to Resume Saved Session:")
    if hasattr(cli.auth, 'try_resume_session'):
        result = cli.auth.try_resume_session()
        print(f"   Session resume result: {result}")
        print(f"   Now authenticated: {cli.auth.is_authenticated()}")
    else:
        print("   try_resume_session method not available")
    print()
    
    # Check mail service connection
    print("4. Mail Service Check:")
    mail_service = cli.auth.get_mail_service()
    print(f"   Mail service: {mail_service is not None}")
    print(f"   Service type: {type(mail_service)}")
    print()
    
    # Try to load real emails
    print("5. Attempting to Load Real Emails:")
    cli.mail._use_real_data = True
    email_count_before = len(cli.mail.unread_emails)
    
    try:
        cli.mail._load_real_emails()
        email_count_after = len(cli.mail.unread_emails)
        print(f"   Emails before: {email_count_before}")
        print(f"   Emails after: {email_count_after}")
        print(f"   Using real data: {email_count_after > 0 and cli.mail.unread_emails[0].get('id') != 1}")  # Check if not mock data
    except Exception as e:
        print(f"   Error loading emails: {str(e)}")
    print()
    
    # Check if mock data is being used
    print("6. Data Source Analysis:")
    if cli.mail.unread_emails:
        first_email = cli.mail.unread_emails[0]
        is_mock = first_email.get('id') == 1 and 'Amazon' in first_email.get('from', '')
        print(f"   Data appears to be mock: {is_mock}")
        print(f"   First email from: {first_email.get('from', 'Unknown')}")
    else:
        print("   No emails loaded")
    print()
    
    print("🔍 Debug Complete")
    print("\nTroubleshooting Steps:")
    if not cli.auth.is_authenticated():
        print("1. Authentication failed - try logging in again")
    else:
        print("1. Authentication successful but using mock data")
        print("2. Check if pyicloud can connect to Apple servers")
        print("3. Verify your Apple ID credentials")
        print("4. Check for 2FA requirements")

if __name__ == "__main__":
    debug_authentication()