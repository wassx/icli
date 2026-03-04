#!/usr/bin/env python3
"""Demo script to show iCloud CLI functionality"""

from icli import iCloudCLI

def demo():
    """Demonstrate the iCloud CLI functionality"""
    print("=== iCloud CLI Demo ===\n")
    
    cli = iCloudCLI()
    
    print("1. Testing Mail Module:")
    print("-" * 20)
    cli.mail.list_emails()
    print()
    
    print("2. Testing Calendar Module:")
    print("-" * 20)
    cli.calendar.list_events()
    print()
    
    print("3. Testing Drive Module:")
    print("-" * 20)
    cli.drive.list_files()
    cli.drive.upload_file("local_file.txt", "/remote/path/")
    cli.drive.download_file("/remote/path/file.txt", "local_download.txt")
    print()
    
    print("Demo completed!")

if __name__ == "__main__":
    demo()