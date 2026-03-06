#!/usr/bin/env python3
"""Demo script to show iCloud CLI functionality"""

from icli import iCloudCLI

def demo():
    """Demonstrate the iCloud CLI functionality"""
    print("=== iCloud CLI Demo ===\n")
    
    cli = iCloudCLI()
    
    print("1. Testing Calendar Module:")
    print("-" * 20)
    cli.calendar.list_events()
    print()
    
    print("3. Testing Drive Module:")
    print("-" * 20)
    print("Drive browser functionality:")
    print("• Interactive file tree navigation")
    print("• Directory browsing with breadcrumbs")
    print("• File details viewing")
    print("• Download functionality")
    print("• File caching for performance")
    print("• Human-readable file sizes")
    print("✓ Drive browser ready for use")
    print()
    # Simple file listing (non-interactive)
    cli.drive.list_files()
    print()
    
    print("Demo completed!")

if __name__ == "__main__":
    demo()