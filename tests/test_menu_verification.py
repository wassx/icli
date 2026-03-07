#!/usr/bin/env python3
"""Verify that sub-menu handlers in main.py list the correct options."""
import os
import sys

def test_menu_shortcuts():
    """Verify sub-menu print statements are present in main.py."""
    print("=== Menu Shortcut Verification ===\n")

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    main_src = open(os.path.join(root, "main.py")).read()

    checks = [
        # Calendar sub-menu
        ('"1) Browse events (interactive)"', "Calendar option 1"),
        ('"2) List calendars"', "Calendar option 2"),
        ('"3) List upcoming events"', "Calendar option 3"),
        # Drive sub-menu
        ('"1) Browse files (interactive tree)"', "Drive option 1"),
        ('"2) Search files"', "Drive option 2"),
        # Mail sub-menu
        ('"1) Inbox overview"', "Mail option 1"),
        ('"2) Browse folders"', "Mail option 2"),
    ]

    errors = []
    for snippet, label in checks:
        if snippet not in main_src:
            errors.append(f"Missing: {label} ({snippet})")

    if errors:
        for e in errors:
            print(f"  ❌ {e}")
        sys.exit(1)

    print("✅ All sub-menu options present in main.py.")

if __name__ == "__main__":
    test_menu_shortcuts()