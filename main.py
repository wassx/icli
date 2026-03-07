#!/usr/bin/env python3
"""iCloud CLI - Main entry point"""

import sys
import os
import json
import argparse
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
    print("1) iCloud Mail")
    print("2) Calendar")
    print("3) iCloud Drive")
    print("4) Authentication")
    print("5) Exit")
    print("\n" + separator("-"))

def handle_menu_choice(choice, cli):
    """Handle the user's menu choice"""
    if choice == "4":
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
    elif choice == "5":
        print("\nGoodbye!")
        return False
    elif choice == "1":
        print("\n=== iCloud Mail ===")
        print("1) Inbox overview")
        print("2) Browse folders")
        print("3) Back to main menu")
        mail_choice = input("\nEnter your choice (1-3): ").strip()
        if mail_choice == "1":
            cli.mail.show_inbox()
        elif mail_choice == "2":
            cli.mail.browse_folders()
        elif mail_choice == "3":
            return True
    elif choice == "2":
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
    elif choice == "3":
        print("\n=== iCloud Drive Menu ===")
        print("1) Browse files (interactive tree)")
        print("2) Search files")
        print("3) List files (simple)")
        print("4) Back to main menu")
        drive_choice = input("\nEnter your choice (1-4): ").strip()
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
            print("ℹ️  Ready — log in via Authentication (option 4) to access your iCloud data.")
    
    running = True
    
    try:
        while running:
            show_main_menu(cli)
            choice = input("\nEnter your choice (1-5): ").strip()
            
            # Check if authentication is needed for this choice
            if choice in ["1", "2", "3"] and not cli.auth.is_authenticated():
                # Offer login before accessing a service
                if not require_authentication(cli):
                    continue
            
            running = handle_menu_choice(choice, cli)
            
            # If a service call caused session expiry mid-use, offer re-login
            if running and choice in ["1", "2", "3"] and not cli.auth.is_authenticated():
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
        result_choice = input(f"Enter result number (1-{len(results)}, Enter=back): ").strip()
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

# ── Non-interactive CLI (scripting / agent mode) ─────────────────────────────

def _quiet(fn, *args, **kwargs):
    """Call fn(*args, **kwargs) while suppressing all stdout output."""
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def _pretty_cli(data, _indent=0):
    """Recursively print a dict/list in a compact human-readable format."""
    pad = "  " * _indent
    if isinstance(data, list):
        if not data:
            print(f"{pad}(no results)")
            return
        for i, item in enumerate(data, 1):
            print(f"{pad}[{i}]")
            _pretty_cli(item, _indent + 1)
    elif isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                print(f"{pad}{k}:")
                _pretty_cli(v, _indent + 1)
            elif v is not None:
                print(f"{pad}{k}: {v}")
    else:
        if data is not None:
            print(f"{pad}{data}")


def run_cli():
    """Non-interactive CLI dispatcher for scripting and agent use.

    Invoked automatically when the script is called with arguments::

        python main.py auth status
        python main.py calendar events --days 7 --json
        python main.py drive search report --type pdf --json

    Run without arguments to enter the interactive menu.
    """
    from icli.api import ICloudAPI

    parser = argparse.ArgumentParser(
        prog="icli",
        description=(
            "iCloud CLI — non-interactive / scripting mode.\n"
            "Run without arguments for the interactive menu."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Authentication setup (once):\n"
            "  python main.py auth login          # interactive; saves to keyring\n\n"
            "Subsequent calls resume the saved session automatically:\n"
            "  python main.py calendar events --json\n"
            "  python main.py drive search report --type pdf --json\n"
        ),
    )
    parser.add_argument("--apple-id", metavar="EMAIL",
                        help="Apple ID (overrides ICLOUD_APPLE_ID env var)")
    parser.add_argument("--password", metavar="PASSWORD",
                        help="Password (overrides ICLOUD_PASSWORD env var; prefer keyring)")

    # Shared --json flag inherited by every leaf subparser via parents=
    _json = argparse.ArgumentParser(add_help=False)
    _json.add_argument("--json", action="store_true",
                       help="Output results as JSON (suppresses progress text)")

    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    # ── auth ──────────────────────────────────────────────────────────────────
    auth_p = sub.add_parser("auth", help="Authentication management")
    auth_sub = auth_p.add_subparsers(dest="auth_cmd", required=True, metavar="SUBCOMMAND")
    auth_sub.add_parser("status", parents=[_json],
                        help="Show current authentication status")
    auth_sub.add_parser("login",  parents=[_json],
                        help="Login interactively and save credentials to keyring")
    auth_sub.add_parser("logout", parents=[_json],
                        help="Logout and remove saved credentials from keyring")

    # ── calendar ──────────────────────────────────────────────────────────────
    cal_p = sub.add_parser("calendar", help="Calendar commands")
    cal_sub = cal_p.add_subparsers(dest="cal_cmd", required=True, metavar="SUBCOMMAND")
    cal_sub.add_parser("list", parents=[_json], help="List all calendars")
    ev_p = cal_sub.add_parser("events", parents=[_json], help="List upcoming events")
    ev_p.add_argument("--calendar", metavar="NAME",
                      help="Filter by calendar name (partial match, case-insensitive)")
    ev_p.add_argument("--days", type=int, default=14, metavar="N",
                      help="Look-ahead window in days (default: 14)")

    # ── drive ─────────────────────────────────────────────────────────────────
    drv_p = sub.add_parser("drive", help="iCloud Drive commands")
    drv_sub = drv_p.add_subparsers(dest="drv_cmd", required=True, metavar="SUBCOMMAND")
    ls_p = drv_sub.add_parser("list", parents=[_json],
                               help="List files and folders at a path")
    ls_p.add_argument("--path", default="/", metavar="PATH",
                      help="iCloud Drive directory path (default: /)")
    sr_p = drv_sub.add_parser("search", parents=[_json],
                               help="Search files in iCloud Drive")
    sr_p.add_argument("query", nargs="?", default="",
                      help="Text to match in filenames (omit to match all)")
    sr_p.add_argument("--type", dest="file_type", metavar="EXT",
                      help="Filter by file extension, e.g. pdf or docx")
    sr_p.add_argument("--min", dest="min_size", type=int, metavar="NKB",
                      help="Minimum file size in KB")
    sr_p.add_argument("--max", dest="max_size", type=int, metavar="NKB",
                      help="Maximum file size in KB")
    dl_p = drv_sub.add_parser("download", parents=[_json],
                               help="Download a file from iCloud Drive")
    dl_p.add_argument("remote_path", metavar="PATH",
                      help="iCloud Drive file path, e.g. /Documents/report.pdf")
    dl_p.add_argument("-o", "--output", dest="local_path", metavar="FILE",
                      help="Local destination file or directory (default: current dir)")

    # ── mail ──────────────────────────────────────────────────────────────────
    mail_p = sub.add_parser("mail", help="iCloud Mail commands")
    mail_sub = mail_p.add_subparsers(dest="mail_cmd", required=True, metavar="SUBCOMMAND")
    mail_sub.add_parser("folders", parents=[_json],
                         help="List mail folders")
    ml_p = mail_sub.add_parser("list", parents=[_json],
                                help="List recent emails")
    ml_p.add_argument("--folder", default="INBOX", metavar="FOLDER",
                      help="Mail folder (default: INBOX)")
    ml_p.add_argument("--limit", type=int, default=20, metavar="N",
                      help="Number of emails to fetch (default: 20)")
    mr_p = mail_sub.add_parser("read", parents=[_json],
                                help="Read a specific email by UID")
    mr_p.add_argument("uid", metavar="UID",
                      help="Email UID (from 'mail list' output)")
    mr_p.add_argument("--folder", default="INBOX", metavar="FOLDER",
                      help="Mail folder (default: INBOX)")

    args = parser.parse_args()
    use_json = args.json
    apple_id = args.apple_id or os.environ.get("ICLOUD_APPLE_ID")
    password = args.password or os.environ.get("ICLOUD_PASSWORD")

    def out(data):
        if use_json:
            print(json.dumps(data, indent=2, default=str))
        else:
            _pretty_cli(data)

    def die(msg, code=1):
        payload = {"ok": False, "error": str(msg)}
        if use_json:
            print(json.dumps(payload), file=sys.stderr)
        else:
            print(f"\u274c {msg}", file=sys.stderr)
        sys.exit(code)

    api = ICloudAPI()

    try:
        # ── auth commands ─────────────────────────────────────────────────────
        if args.command == "auth":
            if args.auth_cmd == "status":
                out(api.auth_status())

            elif args.auth_cmd == "login":
                # Always interactive so 2FA prompts work correctly.
                tmp = iCloudCLI()
                if _quiet(tmp.auth.try_resume_session):
                    out({"ok": True, "message": f"Session resumed for {tmp.auth.apple_id}"})
                else:
                    ok = tmp.auth.login(apple_id=apple_id, password=password)
                    if ok:
                        out({"ok": True, "message": f"Logged in as {tmp.auth.apple_id}"})
                    else:
                        die("Login failed")

            elif args.auth_cmd == "logout":
                _quiet(api.auth.try_resume_session)
                result = _quiet(api.logout)
                out(result)

        # ── data commands (need authentication) ───────────────────────────────
        else:
            try:
                _quiet(api.authenticate, apple_id=apple_id, password=password)
            except RuntimeError as exc:
                die(str(exc))

            if args.command == "calendar":
                if args.cal_cmd == "list":
                    out(_quiet(api.list_calendars))
                elif args.cal_cmd == "events":
                    out(_quiet(api.list_events,
                               calendar_name=args.calendar, days=args.days))

            elif args.command == "drive":
                if args.drv_cmd == "list":
                    out(_quiet(api.list_files, path=args.path))
                elif args.drv_cmd == "search":
                    min_b = args.min_size * 1024 if args.min_size else None
                    max_b = args.max_size * 1024 if args.max_size else None
                    out(_quiet(api.search_files,
                               query=args.query,
                               file_type=args.file_type,
                               min_size=min_b,
                               max_size=max_b))
                elif args.drv_cmd == "download":
                    result = api.download_file(
                        remote_path=args.remote_path,
                        local_path=args.local_path,
                    )
                    if not result.get("ok"):
                        die(result.get("error", "Download failed"))
                    out(result)

            elif args.command == "mail":
                if args.mail_cmd == "folders":
                    out(_quiet(api.list_mail_folders))
                elif args.mail_cmd == "list":
                    out(_quiet(api.list_emails,
                               folder=args.folder, limit=args.limit))
                elif args.mail_cmd == "read":
                    out(_quiet(api.get_email,
                               uid=args.uid, folder=args.folder))

    except (RuntimeError, ValueError) as exc:
        die(str(exc))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_cli()
    else:
        main()