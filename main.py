#!/usr/bin/env python3
"""iCloud CLI - Main entry point"""

import time
from icli import iCloudCLI

def show_main_menu(cli):
    """Display the main menu and handle user input"""
    auth_status = "🔒 Logged in" if cli.auth.is_authenticated() else "🔓 Not logged in"
    print(f"\n=== iCloud CLI - {auth_status} ===")
    print("1) Calendar")
    print("2) iCloud Drive")
    print("3) Authentication")
    print("4) Exit")
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
            print("2) Back to main menu")
        
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
                print("• Calendar: Real iCloud events")
                print("• Drive: Real iCloud files")
                print("\nSession Management:")
                print("• Read-only access (no modifications)")
                print("• Secure connection")
                print("• Automatic reconnection")
            else:
                print("\nPlease log in to access your iCloud data.")
                print("Authentication is required for all features.")
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
        print("\n=== Calendar Menu ===")
        print("1) Browse events (interactive)")
        print("2) List calendars")
        print("3) List upcoming events")
        print("4) Back to main menu")
        calendar_choice = input("\nEnter your choice: ").strip()
        if calendar_choice == "1":
            cli.calendar.browse_events()
        elif calendar_choice == "2":
            cli.calendar.list_calendars()
        elif calendar_choice == "3":
            cli.calendar.list_events()
        elif calendar_choice == "4":
            return True
    elif choice == "2":
        print("\n=== iCloud Drive Menu ===")
        print("1) Browse files (interactive tree)")
        print("2) Search files")
        print("3) List files (simple)")
        print("4) Back to main menu")
        drive_choice = input("\nEnter your choice: ").strip()
        if drive_choice == "1":
            cli.drive.browse_files()
        elif drive_choice == "2":
            _handle_drive_search(cli.drive)
        elif drive_choice == "3":
            cli.drive.list_files()
        elif drive_choice == "4":
            return True
    elif choice == "5":
        print("\nExiting iCloud CLI...")
        return False
    else:
        print("\nInvalid choice. Please try again.")
    
    return True

def require_authentication(cli):
    """Handle authentication requirement - demo mode removed"""
    print("\n❌ Authentication Required")
    print("=" * 40)
    print("To access iCloud services, please log in first.")
    print("\n1) Login to iCloud")
    print("2) Exit")
    
    choice = input("\nEnter your choice (1-2): ").strip()
    
    if choice == "1":
        # Direct to login
        print("\n=== iCloud Login ===")
        if cli.auth.login():
            print("\nLogin successful!")
            print("   You now have access to your real iCloud data.")
            print("   All modules will load data from your iCloud account.")
            return True
        else:
            print("\nLogin cancelled or failed.")
            return False
    elif choice == "2":
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
        print("Current mode: Ready for real iCloud data")
        print("Note: Login to access your actual iCloud account")
    else:
        print("❌ Dependencies required for real iCloud access")
        print("   Install: pip install pyicloud keyring")
        print("   All features require authentication")
    
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
    
    return False

def _handle_drive_search(drive_module):
    """Handle iCloud Drive file search with interactive prompts"""
    print("\n=== iCloud Drive Search ===")
    print("🔍 Search your iCloud Drive files")
    print("Leave fields blank to skip filters")
    print("=" * 60)
    
    # Get search criteria from user
    query = input("\n🔎 Search text (filename contains): ").strip()
    file_type = input("📄 File type (e.g., pdf, docx): ").strip() or None
    
    # Get size constraints
    min_size_input = input("💾 Min size (KB, e.g., 100 for 100KB): ").strip()
    max_size_input = input("💾 Max size (KB, e.g., 1024 for 1MB): ").strip()
    
    # Convert size inputs to bytes
    min_size = None
    max_size = None
    
    if min_size_input:
        try:
            min_size = int(min_size_input) * 1024  # Convert KB to bytes
        except ValueError:
            print(f"⚠️  Invalid min size: '{min_size_input}'. Using no minimum.")
    
    if max_size_input:
        try:
            max_size = int(max_size_input) * 1024  # Convert KB to bytes
        except ValueError:
            print(f"⚠️  Invalid max size: '{max_size_input}'. Using no maximum.")
    
    # Display search criteria
    print("\n🔍 Searching with criteria:")
    print(f"   Text: '{query}'" if query else "   Text: (any)")
    print(f"   Type: {file_type}" if file_type else "   Type: (any)")
    print(f"   Size: {min_size//1024}KB - {max_size//1024}KB" if min_size or max_size else "   Size: (any)")
    print("=" * 60)
    
    # Perform the search
    results = drive_module.search_files(
        query=query,
        file_type=file_type,
        min_size=min_size,
        max_size=max_size
    )
    
    # Offer to navigate to search results
    if results:
        print("\n📂 Search complete. Options:")
        print("1. Browse to a search result")
        print("2. Back to drive menu")
        
        choice = input("\nEnter your choice: ").strip()
        if choice == "1":
            result_choice = input("Enter result number (1-20): ").strip()
            if result_choice.isdigit():
                result_index = int(result_choice) - 1
                if 0 <= result_index < len(results):
                    selected_file = results[result_index]
                    if selected_file and 'path' in selected_file:
                        # Navigate to the file's directory
                        drive_module.current_path = selected_file['path'].rsplit('/', 1)[0]
                        print(f"📁 Navigated to: {drive_module.current_path}")
                        # Show the directory contents
                        drive_module.browse_files()
                else:
                    print("❌ Invalid result number")

if __name__ == "__main__":
    main()