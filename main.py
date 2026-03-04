#!/usr/bin/env python3
"""iCloud CLI - Main entry point"""

import time
from icli import iCloudCLI

def show_main_menu(cli):
    """Display the main menu and handle user input"""
    auth_status = "🔒 Logged in" if cli.auth.is_authenticated() else "🔓 Not logged in"
    print(f"\n=== iCloud CLI - {auth_status} ===")
    print("1) Mail")
    print("2) Calendar")
    print("3) iCloud Drive")
    print("4) Authentication")
    print("5) Exit")
    print("\n===================")

def handle_menu_choice(choice, cli):
    """Handle the user's menu choice"""
    if choice == "4":
        print("\n=== Authentication ===")
        auth_status = "Logged in" if cli.auth.is_authenticated() else "Not logged in"
        print(f"Current status: {auth_status}")
        
        if cli.auth.is_authenticated():
            print("\n1) Logout")
            print("2) Account information")
            print("3) Refresh session")
            print("4) Back to main menu")
        else:
            print("\n1) Login to iCloud")
            print("2) About authentication")
            print("3) Back to main menu")
        
        auth_choice = input("\nEnter your choice: ").strip()
        
        if auth_choice == "1":
            if cli.auth.is_authenticated():
                # Logout
                cli.auth.logout()
                print("\n✅ You have been logged out.")
                print("   Switched to demo mode with mock data.")
            else:
                # Login
                print("\n=== iCloud Login ===")
                print("Secure access to your iCloud services")
                print("• Your credentials are handled securely")
                print("• Passwords can be saved in system keyring (optional)")
                print("• Two-factor authentication supported")
                print("\n📋 Requirements:")
                print("• Apple ID email address")
                print("• Apple ID password")
                print("• 2FA code if enabled on your account")
                
                if cli.auth.login():
                    print("\nLogin successful!")
                    print("   You now have access to your real iCloud data.")
                    print("   All modules will load data from your iCloud account.")
                else:
                    print("\nLogin cancelled or failed.")
                    print("   Continuing in demo mode.")
        elif auth_choice == "2":
            if cli.auth.is_authenticated():
                # Show account info
                print("\n=== Account Information ===")
                print("Authentication: Active")
                print("Email: " + cli.auth.apple_id if cli.auth.apple_id else "Unknown")
                print("Session: Secure")
                
                # Show session status
                if cli.auth.session_expiry:
                    remaining = (cli.auth.session_expiry - time.time()) / 3600
                    print(f"Session expires in: {remaining:.1f} hours")
                
                print("\nData Access:")
                print("• Mail: Real iCloud emails")
                print("• Calendar: Real iCloud events")
                print("• Drive: Real iCloud files")
                print("\nSession Management:")
                print("• Read-only access (no modifications)")
                print("• Secure connection")
                print("• Automatic reconnection")
            else:
                # Show authentication info
                print("\n=== About Authentication ===")
                print("Secure Login Process:")
                print("1. Enter your Apple ID and password")
                print("2. Complete 2FA if enabled (recommended)")
                print("3. Access your real iCloud data")
                print("\nSecurity Features:")
                print("• End-to-end encryption")
                print("• No password storage (optional keyring)")
                print("• Read-only access only")
                print("• Session timeout protection")
                print("\nData Access:")
                print("• View emails, events, and files")
                print("• No modifications possible")
                print("• Full privacy protection")
        elif auth_choice == "3":
            if cli.auth.is_authenticated():
                # Refresh session
                if cli.auth.refresh_session():
                    print("Session refreshed successfully!")
                else:
                    print("Session refresh failed.")
                input("\nPress Enter to continue...")
            else:
                return True
        elif auth_choice == "4" and cli.auth.is_authenticated():
            return True
        else:
            print("Invalid choice")
    elif choice == "1":
        print("\n=== Mail Menu ===")
        print("1) List unread emails")
        print("2) Back to main menu")
        mail_choice = input("\nEnter your choice: ").strip()
        if mail_choice == "1":
            cli.mail.list_emails()
        elif mail_choice == "2":
            return True
        else:
            print("Invalid choice")
    elif choice == "2":
        print("\n=== Calendar Menu ===")
        print("1) List events")
        print("2) Create event")
        print("3) Back to main menu")
        calendar_choice = input("\nEnter your choice: ").strip()
        if calendar_choice == "1":
            cli.calendar.list_events()
        elif calendar_choice == "2":
            print("Create event functionality not yet implemented")
        elif calendar_choice == "3":
            return True
    elif choice == "3":
        print("\n=== iCloud Drive Menu ===")
        print("1) List files")
        print("2) Upload file")
        print("3) Download file")
        print("4) Back to main menu")
        drive_choice = input("\nEnter your choice: ").strip()
        if drive_choice == "1":
            cli.drive.list_files()
        elif drive_choice == "2":
            print("Upload file functionality not yet implemented")
        elif drive_choice == "3":
            print("Download file functionality not yet implemented")
        elif drive_choice == "4":
            return True
    elif choice == "4":
        print("\nOther functionality coming soon...")
    elif choice == "5":
        print("\nExiting iCloud CLI...")
        return False
    else:
        print("\nInvalid choice. Please try again.")
    
    return True

def require_authentication(cli):
    """Handle authentication requirement with better UX"""
    print("\nAuthentication Required")
    print("=" * 40)
    print("To access iCloud services, please log in first.")
    print("\n1) Login to iCloud")
    print("2) Continue with demo mode (mock data)")
    print("3) Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        # Direct to login
        print("\n=== iCloud Login ===")
        if cli.auth.login():
            print("\n✅ Login successful! You now have access to real iCloud data.")
            return True
        else:
            print("\n❌ Login failed. Continuing in demo mode.")
            return False
    elif choice == "2":
        print("\n🎭 Continuing in demo mode with sample data.")
        print("   (No real iCloud data will be accessed)")
        return False
    elif choice == "3":
        print("\nGoodbye!")
        return False
    else:
        print("\nInvalid choice. Please try again.")
        return require_authentication(cli)

def main():
    """Main program loop with improved UX"""
    cli = iCloudCLI()
    
    # Welcome message
    print("Welcome to iCloud CLI")
    print("=" * 40)
    print("A command-line interface for your iCloud services")
    
    # Check if we can use real data
    has_pyicloud = True
    try:
        from pyicloud import PyiCloudService
    except ImportError:
        has_pyicloud = False
    
    if has_pyicloud:
        print("Current mode: Ready for real iCloud data 🎉")
        print("Note: Login to access your actual iCloud account")
    else:
        print("Current mode: Demo (mock data)")
        print("⚠️  Install 'pyicloud' for real iCloud access")
        print("   Command: pip install pyicloud keyring")
    
    running = True
    
    while running:
        show_main_menu(cli)
        choice = input("\nEnter your choice (1-5): ").strip()
        
        # Check if authentication is needed for this choice
        if choice in ["1", "2", "3"] and not cli.auth.is_authenticated():
            # Ask user if they want to authenticate
            if require_authentication(cli):
                # User successfully logged in, continue with their choice
                pass  # Will handle the choice below
            else:
                # User chose demo mode, continue with mock data
                continue
        
        running = handle_menu_choice(choice, cli)
        
        if running:
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()