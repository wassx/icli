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
        """Authenticate with iCloud"""
        try:
            if use_keyring and apple_id and KEYRING_AVAILABLE:
                # Try to get password from keyring
                password = keyring.get_service("iCloudCLI", apple_id)
                if not password:
                    print("No saved password found in keyring")
                    return False
            
            if not apple_id:
                apple_id = input("Enter your Apple ID: ").strip()
            
            if not password:
                password = input("Enter your password: ").strip()
            
            print("Authenticating with iCloud...")
            self.service = PyiCloudService(apple_id, password)
            
            if self.service.requires_2fa:
                print("Two-factor authentication required")
                code = input("Enter 2FA code: ").strip()
                if not self.service.validate_2fa_code(code):
                    print("Invalid 2FA code")
                    return False
                
                # Save trusted device
                if not self.service.is_trusted_session:
                    print("Session not trusted. Some features may be limited.")
            
            self.apple_id = apple_id
            self.authenticated = True
            
            # Save to keyring for future use
            if use_keyring and KEYRING_AVAILABLE:
                keyring.set_password("iCloudCLI", apple_id, password)
            
            print("✅ Authentication successful!")
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