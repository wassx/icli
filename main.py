#!/usr/bin/env python3
"""iCloud CLI - Main entry point"""

from icli import iCloudCLI

def show_main_menu():
    """Display the main menu and handle user input"""
    print("\n=== iCloud CLI ===")
    print("1) Mail")
    print("2) Calendar")
    print("3) iCloud Drive")
    print("4) Other")
    print("5) Exit")
    print("\n===================")

def handle_menu_choice(choice, cli):
    """Handle the user's menu choice"""
    if choice == "1":
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

def main():
    """Main program loop"""
    cli = iCloudCLI()
    running = True
    
    while running:
        show_main_menu()
        choice = input("\nEnter your choice (1-5): ").strip()
        running = handle_menu_choice(choice, cli)
        
        if running:
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()