"""Mail module for iCloud CLI"""

class MailModule:
    def __init__(self):
        # Mock data for demonstration
        self.unread_emails = [
            {
                "id": 1,
                "from": "Amazon <orders@amazon.com>",
                "subject": "Your Amazon Order #123-4567890-1234567",
                "date": "Today, 10:30 AM",
                "preview": "Your order has been shipped and will arrive by Wednesday, March 10.",
                "body": "Dear Customer,\n\nYour order #123-4567890-1234567 has been shipped via UPS Ground.\n\nItems:\n- Wireless Headphones (Black)\n- USB-C Cable (2m)\n\nTracking number: 1Z999AA10123456784\nEstimated delivery: Wednesday, March 10, 2023\n\nThank you for shopping with Amazon!"
            },
            {
                "id": 2,
                "from": "GitHub <notifications@github.com>",
                "subject": "[github] New issue opened in your repository",
                "date": "Today, 9:15 AM",
                "preview": "User john-doe opened a new issue: Bug in login functionality",
                "body": "New Issue Opened\n\nRepository: yourusername/awesome-project\nIssue #42: Bug in login functionality\nOpened by: john-doe\n\nDescription:\nWhen I try to login with special characters in the password, I get a 500 error.\n\nSteps to reproduce:\n1. Go to login page\n2. Enter username: testuser\n3. Enter password: P@ssw0rd!\n4. Click login\n\nExpected: Successful login\nActual: 500 Internal Server Error"
            },
            {
                "id": 3,
                "from": "Netflix <info@netflix.com>",
                "subject": "Your Netflix membership",
                "date": "Yesterday, 3:45 PM",
                "preview": "Your membership will renew on March 15, 2023.",
                "body": "Hello Stefan,\n\nYour Netflix membership will automatically renew on March 15, 2023 for $15.99.\n\nCurrent plan: Premium (4K Ultra HD)\nNext billing date: March 15, 2023\nPayment method: Visa •••• 1234\n\nYou can change or cancel your plan anytime at netflix.com/account."
            }
        ]
    
    def list_emails(self):
        """List unread emails with quick overview"""
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
        """Offer options after reading an email"""
        print("\nOptions:")
        print("1. Reply")
        print("2. Forward")
        print("3. Delete")
        print("4. Mark as read")
        print("5. Back to email list")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "1":
            print("Reply functionality not yet implemented")
        elif choice == "2":
            print("Forward functionality not yet implemented")
        elif choice == "3":
            print("Delete functionality not yet implemented")
        elif choice == "4":
            print("Email marked as read")
            # Remove from unread list
            del self.unread_emails[email_index]
        elif choice == "5":
            return
        else:
            print("Invalid choice")
        
        # Go back to email list if there are still emails
        if self.unread_emails:
            self.list_emails()
    
    def send_email(self, to, subject, body):
        """Send an email"""
        print(f"Sending email to {to}...")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        # TODO: Implement actual email sending