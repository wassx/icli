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