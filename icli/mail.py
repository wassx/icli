"""Mail module for iCloud CLI"""

class MailModule:
    def __init__(self, auth=None):
        self.auth = auth
        self.unread_emails = []
        self._use_real_data = True  # Always use real data (demo mode removed)
    
    def _load_real_emails(self):
        """Load real emails from iCloud"""
        if not self.auth or not self.auth.is_authenticated():
            print("❌ Not authenticated. Please log in to access your iCloud data.")
            return
        
        try:
            mail_service = self.auth.get_mail_service()
            if not mail_service:
                print("Mail service not available")
                return
            
            # Get unread emails from inbox
            try:
                inbox = mail_service.inbox
                self.unread_emails = []
                
                for email in inbox:
                    if not email.read:
                        self.unread_emails.append({
                            "id": email.id,
                            "from": email.sender,
                            "subject": email.subject,
                            "date": email.date.strftime("%Y-%m-%d %H:%M:%S"),
                            "preview": email.preview,
                            "body": email.plain_text_body if hasattr(email, 'plain_text_body') else ""
                        })
            except AttributeError as e:
                print(f"❌ Mail service API has changed: {str(e)}")
                print("   Please check your pyicloud version and update if needed")
                return
            
            print(f"Loaded {len(self.unread_emails)} unread emails from iCloud")
            
        except Exception as e:
            print(f"❌ Error loading real emails: {str(e)}")
            print("   Please check your internet connection and try again.")
    
    def list_emails(self):
        """List unread emails with quick overview"""
        # Check session activity first
        if self.auth:
            self.auth.check_session_activity()
        
        # Load real data if enabled
        if self._use_real_data:
            self._load_real_emails()
        
        if not self.unread_emails:
            print("No unread emails.")
            return
        
        print(f"\nYou have {len(self.unread_emails)} unread emails:\n")
        print("=" * 80)
        
        for i, email in enumerate(self.unread_emails, 1):
            print(f"{i}. FROM: {email['from']}")
            print(f"   SUBJECT: {email['subject']}")
            print(f"   DATE: {email['date']}")
            print(f"   PREVIEW: {email['preview']}")
            print("-" * 80)
        
        # Offer to read an email in detail
        self._offer_read_email()
    
    def _offer_read_email(self):
        """Offer to read a specific email in detail"""
        if not self.unread_emails:
            return
        
        choice = input("\nEnter email number to read in detail (or 'q' to quit): ").strip()
        
        if choice.lower() == 'q':
            return
        
        try:
            email_index = int(choice) - 1
            if 0 <= email_index < len(self.unread_emails):
                self.read_email_detail(email_index)
            else:
                print("Invalid email number.")
        except ValueError:
            print("Invalid input. Please enter a number or 'q' to quit.")
    
    def read_email_detail(self, email_index):
        """Read a specific email in detail"""
        if email_index < 0 or email_index >= len(self.unread_emails):
            print("Invalid email index.")
            return
        
        email = self.unread_emails[email_index]
        
        print("\n" + "=" * 80)
        print("EMAIL DETAIL")
        print("=" * 80)
        print(f"FROM: {email['from']}")
        print(f"SUBJECT: {email['subject']}")
        print(f"DATE: {email['date']}")
        print("\n" + "-" * 80)
        print("BODY:")
        print(email['body'])
        print("=" * 80)
        
        # Offer options after reading
        self._offer_email_options(email_index)
    
    def _offer_email_options(self, email_index):
        """Offer options after reading an email - READ-ONLY mode"""
        print("\nOptions (Read-Only Mode):")
        print("1. Mark as read")
        print("2. Back to email list")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "1":
            print("Email marked as read")
            # Remove from unread list
            del self.unread_emails[email_index]
        elif choice == "2":
            return
        else:
            print("Invalid choice")
        
        # Go back to email list if there are still emails
        if self.unread_emails:
            self.list_emails()
    
    def send_email(self, to, subject, body):
        """Send an email - DISABLED for read-only mode"""
        print("❌ Email sending is disabled in read-only mode")
        return False