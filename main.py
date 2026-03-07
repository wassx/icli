#!/usr/bin/env python3
"""iCloud CLI - Main entry point"""

import time
from icli import iCloudCLI
from icli.utils import separator, Spinner

BANNER = r"""
 _  ___ _    ___ 
(_)/ __| |  |_ _|
| | (__| |__ | | 
|_|\___|____|___|
"""

def pause():
    """Wait for the user to press Enter before redrawing the menu."""
    input("\nPress Enter to continue...")

def show_main_menu(cli):
    """Display the main menu and handle user input"""
    auth_status = "🔒 Logged in" if cli.auth.is_authenticated() else "🔓 Not logged in"
    print(f"\n=== iCloud CLI - {auth_status} ===")
    print("1) Calendar")
    print("2) iCloud Drive")
    print("3) Authentication")
    print("4) Exit")
    print("\n" + separator("-"))

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
        print("4) Monthly calendar grid")
        print("5) Back to main menu")
        calendar_choice = input("\nEnter your choice (1-5): ").strip()
        if calendar_choice == "1":
            cli.calendar.browse_events()
        elif calendar_choice == "2":
            cli.calendar.list_calendars()
        elif calendar_choice == "3":
            cli.calendar.list_events()
        elif calendar_choice == "4":
            cli.calendar.show_calendar_grid()
        elif calendar_choice == "5":
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
    print(separator())
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
    print(BANNER)
    print(separator())
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
    
    try:
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
                pause()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    
    return False

def _handle_drive_search(drive_module):
    """Handle iCloud Drive file search.
    
    Accepts a single-line query so users can specify all filters at once
    and edit them easily on re-search without re-entering each field.

    Syntax:  [text] [type=ext] [min=NKB] [max=NKB]
    Example: report type=pdf min=100 max=5000
    """
    print("\n=== iCloud Drive Search ===")
    print("🔍 Single-line search: [text] [type=ext] [min=NKB] [max=NKB]")
    print("   Examples:")
    print("     report                   → filenames containing 'report'")
    print("     budget type=xlsx         → xlsx files with 'budget' in name")
    print("     type=pdf min=500         → PDF files ≥ 500 KB")
    print("     min=1024 max=10240       → files between 1 MB and 10 MB")
    print(separator())
    
    raw = input("\n🔎 Search: ").strip()
    if not raw:
        print("ℹ️  No search terms entered.")
        return
    
    # Parse tokens
    query_parts = []
    file_type = None
    min_size = None
    max_size = None
    
    for token in raw.split():
        lower = token.lower()
        if lower.startswith("type="):
            file_type = lower[5:] or None
        elif lower.startswith("min="):
            try:
                min_size = int(lower[4:]) * 1024
            except ValueError:
                print(f"⚠️  Ignored invalid min value: '{token}'")
        elif lower.startswith("max="):
            try:
                max_size = int(lower[4:]) * 1024
            except ValueError:
                print(f"⚠️  Ignored invalid max value: '{token}'")
        else:
            query_parts.append(token)
    
    query = " ".join(query_parts)
    
    # Display resolved search criteria
    print("\n🔍 Searching:")
    print(f"   Text: '{query}'" if query else "   Text: (any)")
    print(f"   Type: {file_type}" if file_type else "   Type: (any)")
    if min_size or max_size:
        lo = f"{min_size // 1024} KB" if min_size else "—"
        hi = f"{max_size // 1024} KB" if max_size else "—"
        print(f"   Size: {lo} → {hi}")
    else:
        print("   Size: (any)")
    print(separator())
    
    results = drive_module.search_files(
        query=query,
        file_type=file_type,
        min_size=min_size,
        max_size=max_size
    )
    
    if results:
        print(f"\n📂 {len(results)} result(s) found. Enter a result number to navigate to it, or press Enter to go back.")
        result_choice = input("Result number: ").strip()
        if result_choice.isdigit():
            result_index = int(result_choice) - 1
            if 0 <= result_index < len(results):
                selected_file = results[result_index]
                if selected_file and 'path' in selected_file:
                    drive_module.current_path = selected_file['path'].rsplit('/', 1)[0]
                    print(f"📁 Navigated to: {drive_module.current_path}")
                    drive_module.browse_files()
            else:
                print("❌ Invalid result number")

if __name__ == "__main__":
    main()