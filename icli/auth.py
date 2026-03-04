"""
Authentication module for iCloud CLI
Handles Apple ID authentication and session management
"""

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    
try:
    from pyicloud import PyiCloudService
    from pyicloud.exceptions import PyiCloudFailedLoginException
    PYICLOUD_AVAILABLE = True
except ImportError:
    PYICLOUD_AVAILABLE = False
    
    # Mock classes for when pyicloud is not available
    class PyiCloudService:
        def __init__(self, apple_id, password):
            self.requires_2fa = False
            self.is_trusted_session = False
            print("⚠️  pyicloud not installed. Using mock authentication.")
    
    class PyiCloudFailedLoginException(Exception):
        pass

class iCloudAuth:
    """Handle authentication with iCloud services"""
    
    def __init__(self):
        self.service = None
        self.authenticated = False
        self.apple_id = None
    
    def login(self, apple_id=None, password=None, use_keyring=True):
        """Authenticate with iCloud with improved UX"""
        try:
            # Check if we already have credentials in keyring
            if use_keyring and apple_id and KEYRING_AVAILABLE:
                password = keyring.get_service("iCloudCLI", apple_id)
                if password:
                    print("🔑 Found saved credentials. Logging in...")
                else:
                    print("No saved password found in keyring")
            
            # Get Apple ID
            if not apple_id:
                print("\n📧 Apple ID:")
                apple_id = input("   Enter your Apple ID email: ").strip()
                if not apple_id:
                    print("❌ Apple ID cannot be empty")
                    return False
                if "@" not in apple_id:
                    print("❌ Please enter a valid email address")
                    return False
            
            # Get password
            if not password:
                print("\n🔒 Password:")
                password = input("   Enter your password: ").strip()
                if not password:
                    print("❌ Password cannot be empty")
                    return False
                if len(password) < 4:
                    print("❌ Password too short")
                    return False
            
            print("\n🔄 Connecting to iCloud...")
            print("   This may take a few seconds...")
            
            self.service = PyiCloudService(apple_id, password)
            
            if self.service.requires_2fa:
                print("\n🔐 Two-Factor Authentication Required")
                print("   A verification code has been sent to your trusted devices")
                print("   Check your iPhone, iPad, or Mac for the notification")
                
                while True:
                    code = input("   Enter 6-digit verification code: ").strip()
                    if len(code) != 6 or not code.isdigit():
                        print("   ❌ Please enter a valid 6-digit code")
                        continue
                    
                    if self.service.validate_2fa_code(code):
                        print("   ✅ Two-factor authentication successful")
                        break
                    else:
                        print("   ❌ Invalid verification code. Please try again.")
                        continue
                
                # Check if session is trusted
                if not self.service.is_trusted_session:
                    print("\n⚠️  Session not trusted")
                    print("   Some features may be limited until you trust this device")
                    print("   You can trust this device in your iCloud security settings")
            
            self.apple_id = apple_id
            self.authenticated = True
            
            # Save to keyring for future use
            if use_keyring and KEYRING_AVAILABLE:
                keyring.set_password("iCloudCLI", apple_id, password)
                print("\n🔑 Credentials saved securely in system keyring")
            else:
                print("\n📝 Credentials not saved (keyring not available)")
            
            print("\n🎉 Authentication Successful!")
            print("   You now have secure access to your iCloud data")
            print("   All modules will load real data from your iCloud account")
            print("   Remember: This CLI operates in read-only mode")
            
            return True
            
        except PyiCloudFailedLoginException:
            print("❌ Authentication failed. Check your credentials.")
            return False
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def logout(self):
        """Logout from iCloud"""
        if self.service:
            # Clear keyring
            if self.apple_id and KEYRING_AVAILABLE:
                keyring.delete_password("iCloudCLI", self.apple_id)
            
            self.service = None
            self.authenticated = False
            self.apple_id = None
            print("Logged out successfully")
        else:
            print("Not logged in")
    
    def get_mail_service(self):
        """Get mail service if authenticated"""
        if not self.authenticated or not self.service:
            return None
        return self.service.mail
    
    def get_calendar_service(self):
        """Get calendar service if authenticated"""
        if not self.authenticated or not self.service:
            return None
        return self.service.calendar
    
    def get_drive_service(self):
        """Get drive service if authenticated"""
        if not self.authenticated or not self.service:
            return None
        return self.service.drive
    
    def is_authenticated(self):
        """Check authentication status"""
        return self.authenticated and self.service is not None