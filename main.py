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
    if choice == "3":
        print("\n=== Authentication ===")
        auth_status = "Logged in" if cli.auth.is_authenticated() else "Not logged in"
        print(f"Current status: {auth_status}")
        
        if cli.auth.is_authenticated():
            print("\n1) Logout")
            print("2) Account information")
            print("3) Extend session timer")
            print("4) Back to main menu")
            
            auth_choice = input("\nEnter your choice (1-4): ").strip()
            
            if auth_choice == "1":
                cli.auth.logout()
                print("\n✅ You have been logged out.")
            elif auth_choice == "2":
                print("\n=== Account Information ===")
                print(f"Apple ID:  {cli.auth.apple_id or 'Unknown'}")
                if cli.auth.session_expiry:
                    remaining_secs = max(0, cli.auth.session_expiry - time.time())
                    remaining_h = int(remaining_secs // 3600)
                    remaining_m = int((remaining_secs % 3600) // 60)
                    print(f"Session:   Active ({remaining_h}h {remaining_m:02d}m remaining)")
                else:
                    print("Session:   Active")
                print("Access:    Read-only")
            elif auth_choice == "3":
                if cli.auth.refresh_session():
                    print("✅ Session timer extended for another 24 hours.")
                else:
                    print("❌ Could not extend session timer.")
            elif auth_choice == "4":
                return True
            else:
                print("❌ Invalid choice. Please enter 1-4.")
        else:
            print("\n1) Login to iCloud")
            print("2) Back to main menu")
            
            auth_choice = input("\nEnter your choice (1-2): ").strip()
            
            if auth_choice == "1":
                print("\n=== iCloud Login ===")
                print("• Your credentials are handled securely")
                print("• Passwords can be saved in system keyring (optional)")
                print("• Two-factor authentication supported")
                if cli.auth.login():
                    print("\n✅ Login successful!")
                else:
                    print("\n❌ Login cancelled or failed.")
            elif auth_choice == "2":
                return True
            else:
                print("❌ Invalid choice. Please enter 1-2.")
    elif choice == "4":
        print("\nGoodbye!")
        return False
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

    else:
        print("\nInvalid choice. Please try again.")
    
    return True

def require_authentication(cli):
    """Prompt the user to log in before accessing a service."""
    print("\n❌ Authentication Required")
    print("=" * 40)
    print("To access iCloud services, please log in first.")
    print("\n1) Login to iCloud")
    print("2) Exit")
    
    while True:
        choice = input("\nEnter your choice (1-2): ").strip()
        
        if choice == "1":
            print("\n=== iCloud Login ===")
            if cli.auth.login():
                print("\n✅ Login successful!")
                return True
            else:
                print("\n❌ Login cancelled or failed.")
                return False
        elif choice == "2":
            print("\nGoodbye!")
            return False
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")

def main():
    """Main program loop with improved UX"""
    cli = iCloudCLI()
    
    # Welcome message
    print("Welcome to iCloud CLI")
    print("=" * 40)
    print("A command-line interface for your iCloud services")
    
    # Dependency check (outside the constructor so no side-effects in __init__)
    missing = cli.auth.check_dependencies()
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print(f"   Install with: pip install {' '.join(missing)}")
        print("   All features require these packages.\n")
    else:
        # Try to resume a previous session from saved keyring credentials
        if cli.auth.try_resume_session():
            print(f"✅ Session resumed for {cli.auth.apple_id}")
        else:
            print("ℹ️  Ready — log in via Authentication (option 3) to access your iCloud data.")
    
    running = True
    
    while running:
        show_main_menu(cli)
        choice = input("\nEnter your choice (1-4): ").strip()
        
        # Check if authentication is needed for this choice
        if choice in ["1", "2"] and not cli.auth.is_authenticated():
            # Offer login before accessing a service
            if not require_authentication(cli):
                continue
        
        running = handle_menu_choice(choice, cli)
        
        # If a service call caused session expiry mid-use, offer re-login
        if running and choice in ["1", "2"] and not cli.auth.is_authenticated():
            print("\n⚠️  Your session expired during this operation.")
            relogin = input("   Log in again now? (y/n): ").strip().lower()
            if relogin == "y":
                cli.auth.login()
        
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