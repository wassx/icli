"""
Authentication module for iCloud CLI
Handles Apple ID authentication and session management
"""

import time
import logging
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

logger = logging.getLogger(__name__)

class iCloudAuth:
    """Handle authentication with iCloud services"""
    
    def __init__(self):
        self.service = None
        self.authenticated = False
        self.apple_id = None
        self.session_token = None
        self.refresh_token = None
        self.session_expiry = None
        self.last_activity = None
        logger.info("iCloudAuth initialized")
    
    def check_dependencies(self):
        """Return a list of missing dependency names, or an empty list if all present."""
        missing = []
        if not PYICLOUD_AVAILABLE:
            missing.append("pyicloud")
        if not KEYRING_AVAILABLE:
            missing.append("keyring")
        return missing
    
    def login(self, apple_id=None, password=None, use_keyring=True):
        """Authenticate with iCloud with improved UX"""
        # Check dependencies before attempting login
        if not PYICLOUD_AVAILABLE:
            print("\n❌ Cannot login: pyicloud library not installed")
            print("   Install with: pip install pyicloud")
            print("   Continuing in demo mode.\n")
            return False
        
        try:
            # Check if we already have credentials in keyring
            if use_keyring and apple_id and KEYRING_AVAILABLE:
                password = keyring.get_password("iCloudCLI", apple_id)
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
            
            # Get password securely
            if not password:
                print("\nPassword:")
                try:
                    import getpass
                    password = getpass.getpass("   Enter your password: ")
                except ImportError:
                    # Fallback if getpass not available
                    password = input("   Enter your password: ")
                
                if not password:
                    print("Password cannot be empty")
                    return False
                if len(password) < 4:
                    print("Password too short")
                    return False
            
            print("\n🔄 Connecting to iCloud...")
            print("   This may take a few seconds...")
            
            # Clear any existing session before attempting new authentication so
            # that a failed re-login never leaves stale state behind.
            if self.authenticated or self.service:
                self._clear_session(clear_credentials=False)
            
            # Create the service — raises PyiCloudFailedLoginException on wrong credentials.
            try:
                self.service = PyiCloudService(apple_id, password)
            except PyiCloudFailedLoginException:
                # Wrong password: also wipe any previously saved password so the
                # user is prompted for a new one on the next attempt.
                if apple_id and KEYRING_AVAILABLE:
                    try:
                        keyring.delete_password("iCloudCLI", apple_id)
                    except Exception:
                        pass
                print("❌ Authentication failed. Check your credentials.")
                return False
            except Exception as e:
                print(f"❌ Authentication failed: {str(e)}")
                return False
            
            # Check 2FA requirement BEFORE accessing any service resource.
            # While 2FA is pending, every resource access raises an exception;
            # verifying auth first would make the 2FA flow unreachable.
            if not self.service.requires_2fa:
                # Verify authentication by attempting to access a service resource.
                try:
                    if hasattr(self.service, 'account'):
                        _ = self.service.account
                    elif hasattr(self.service, 'get_account'):
                        _ = self.service.get_account()
                    else:
                        if hasattr(self.service, 'mail'):
                            _ = self.service.mail
                        elif hasattr(self.service, 'calendar'):
                            _ = self.service.calendar
                        else:
                            _ = self.service.request('/account')
                except Exception as auth_error:
                    self.service = None
                    print(f"❌ Authentication failed: {str(auth_error)}")
                    return False
                
                if hasattr(self.service, 'authenticated') and not self.service.authenticated:
                    self.service = None
                    print("❌ Authentication failed: Invalid Apple ID or password")
                    return False
            
            if self.service.requires_2fa:
                print("\n🔐 Two-Factor Authentication Required")
                print("   A verification code has been sent to your trusted devices")
                print("   Check your iPhone, iPad, or Mac for the notification")
                
                while True:
                    code = input("   Enter 6-digit verification code: ").strip()
                    if len(code) != 6 or not code.isdigit():
                        print("   ❌ Please enter a valid 6-digit code")
                        continue
                    
                    try:
                        if self.service.validate_2fa_code(code):
                            print("   ✅ Two-factor authentication successful")
                            break
                        else:
                            print("   ❌ Invalid verification code. Please try again.")
                            continue
                    except Exception as e:
                        print(f"   ❌ 2FA validation error: {str(e)}")
                        self.service = None
                        return False
                
                # Check if session is trusted
                if not self.service.is_trusted_session:
                    print("\n⚠️  Session not trusted")
                    print("   Some features may be limited until you trust this device")
                    print("   You can trust this device in your iCloud security settings")
            
            self.apple_id = apple_id
            self.authenticated = True
            
            # Start session with timeout
            self._start_session(duration_hours=24)
            
            # Save to keyring for future use
            if use_keyring and KEYRING_AVAILABLE:
                keyring.set_password("iCloudCLI", apple_id, password)
                print("\nCredentials saved securely in system keyring")
            else:
                print("\nCredentials not saved (keyring not available)")
            
            print("\nAuthentication Successful!")
            print("   You now have secure access to your iCloud data")
            print("   All modules will load real data from your iCloud account")
            print("   Session will expire in 24 hours")
            print("   Remember: This CLI operates in read-only mode")
            
            return True
            
        except PyiCloudFailedLoginException:
            # Caught here only if raised outside the service-creation block
            # (e.g., during 2FA trust establishment).
            self.service = None
            print("❌ Authentication failed. Check your credentials.")
            return False
        except Exception as e:
            self.service = None
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def logout(self):
        """Logout from iCloud"""
        if self.authenticated or self.service:
            print("\nLogging out...")
            self._clear_session(clear_credentials=True)
            print("Logged out successfully")
        else:
            print("Not logged in")
    
    def try_resume_session(self):
        """Try to resume an existing session"""
        if not KEYRING_AVAILABLE or not PYICLOUD_AVAILABLE:
            return False
        
        try:
            # Try to get saved credentials
            saved_credentials = keyring.get_credential("iCloudCLI", None)
            if saved_credentials:
                apple_id = saved_credentials.username
                password = saved_credentials.password
                
                print(f"Found saved credentials for {apple_id}")
                print("Attempting to resume session...")
                
                # Try to authenticate
                self.service = PyiCloudService(apple_id, password)
                
                if self.service.requires_2fa:
                    print("2FA required for session resume")
                    self.service = None
                    return False
                
                self.apple_id = apple_id
                self.authenticated = True
                self._start_session(duration_hours=24)
                
                print("Session resumed successfully!")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Session resume failed: {str(e)}")
            return False
    
    def get_oauth_token(self):
        """Get OAuth token if available"""
        if not self.is_authenticated():
            return None
        
        try:
            # Try to get OAuth token from service
            if hasattr(self.service, 'oauth_token'):
                return self.service.oauth_token
            elif hasattr(self.service, 'get_oauth_token'):
                return self.service.get_oauth_token()
        except Exception:
            pass
        
        return None
    
    def save_oauth_token(self, token, refresh_token=None):
        """Save OAuth tokens for future use"""
        self.session_token = token
        self.refresh_token = refresh_token
        
        if KEYRING_AVAILABLE:
            try:
                # Save tokens securely
                keyring.set_password("iCloudCLI_tokens", self.apple_id, f"{token}:{refresh_token}")
                return True
            except Exception:
                pass
        
        return False
    
    def load_oauth_token(self):
        """Load saved OAuth tokens"""
        if not self.apple_id or not KEYRING_AVAILABLE:
            return False
        
        try:
            token_data = keyring.get_password("iCloudCLI_tokens", self.apple_id)
            if token_data and ":" in token_data:
                self.session_token, self.refresh_token = token_data.split(":", 1)
                return True
        except Exception:
            pass
        
        return False
    
    def refresh_oauth_token(self):
        """Refresh OAuth token using refresh token"""
        if not self.refresh_token or not self.is_authenticated():
            return False
        
        try:
            print("Refreshing OAuth token...")
            # This would require proper OAuth refresh endpoint
            # For now, we'll simulate the process
            if hasattr(self.service, 'refresh_oauth_token'):
                new_token = self.service.refresh_oauth_token(self.refresh_token)
                if new_token:
                    self.session_token = new_token
                    self.save_oauth_token(new_token, self.refresh_token)
                    print("OAuth token refreshed successfully")
                    return True
            
            print("OAuth token refresh not supported by current service")
            return False
            
        except Exception as e:
            print(f"OAuth token refresh failed: {str(e)}")
            return False
    

    
    def get_calendar_service(self):
        """Get calendar service if authenticated"""
        if not self.authenticated or not self.service:
            return None
        
        # Handle different pyicloud API versions
        if hasattr(self.service, 'calendar'):
            return self.service.calendar
        elif hasattr(self.service, 'calendar_service'):
            return self.service.calendar_service
        else:
            print("❌ Calendar service not available in this pyicloud version")
            return None
    
    def get_drive_service(self):
        """Get drive service if authenticated"""
        if not self.authenticated or not self.service:
            return None
        
        # Handle different pyicloud API versions
        if hasattr(self.service, 'drive'):
            return self.service.drive
        elif hasattr(self.service, 'drive_service'):
            return self.service.drive_service
        else:
            print("❌ Drive service not available in this pyicloud version")
            return None
    
    def is_authenticated(self):
        """Check authentication status"""
        if not self.authenticated or not self.service:
            return False
        
        # Check if session is still valid
        if self.session_expiry and self.session_expiry < time.time():
            print("Session expired. Please log in again.")
            # Preserve keyring credentials on normal expiry — they are still
            # valid and allow automatic re-authentication via try_resume_session.
            self._clear_session(clear_credentials=False)
            return False
        
        return True
    
    def _clear_session(self, clear_credentials=True):
        """Clear current session data.
        
        Args:
            clear_credentials: If True (default), also delete saved credentials
                from keyring. Pass False when clearing an expired session so
                that valid saved credentials are preserved for the next login.
        """
        self.service = None
        self.authenticated = False
        self.session_token = None
        self.refresh_token = None
        self.session_expiry = None
        self.last_activity = None
        
        # Optionally remove saved credentials from keyring
        if clear_credentials and self.apple_id and KEYRING_AVAILABLE:
            try:
                keyring.delete_password("iCloudCLI", self.apple_id)
            except Exception:
                pass
        
        self.apple_id = None
    
    def _start_session(self, duration_hours=24):
        """Start a new session with timeout"""
        self.last_activity = time.time()
        self.session_expiry = self.last_activity + (duration_hours * 3600)
        print(f"Session started. Will expire in {duration_hours} hours.")
    
    def refresh_session(self):
        """Refresh the current session"""
        if not self.is_authenticated():
            print("No active session to refresh.")
            return False
        
        self.last_activity = time.time()
        # Extend session by 24 hours
        self.session_expiry = self.last_activity + (24 * 3600)
        print("Session refreshed. Extended for another 24 hours.")
        return True
    
    def check_session_activity(self):
        """Check and refresh session if needed"""
        if not self.is_authenticated():
            return False
        
        # Auto-refresh if session expires soon (within 1 hour)
        if self.session_expiry and (self.session_expiry - time.time()) < 3600:
            print("Session about to expire. Refreshing...")
            return self.refresh_session()
        
        return True