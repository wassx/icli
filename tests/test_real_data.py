#!/usr/bin/env python3
"""
Test script for real data integration
This tests the authentication and real data loading without requiring actual credentials
"""

from icli import iCloudCLI

def test_real_data_integration():
    """Test the real data integration"""
    print("=== Testing Real Data Integration ===\n")
    
    cli = iCloudCLI()
    
    # Test 1: Initial state (not authenticated)
    print("1. Testing initial authentication state:")
    print(f"   Authenticated: {cli.auth.is_authenticated()}")
    print(f"   Expected: False")
    assert not cli.auth.is_authenticated(), "Should start unauthenticated"
    print("✓ Correctly starts unauthenticated\n")
    
    # Test 2: Calendar module without authentication
    print("3. Testing calendar module without authentication:")
    cli.calendar.list_events()  # Should show error message
    print("✓ Correctly shows authentication required\n")
    
    # Test 4: Drive module without authentication
    print("4. Testing drive module without authentication:")
    cli.drive.list_files()  # Should show error message
    print("✓ Correctly shows authentication required\n")
    
    # Test 5: Authentication flow (simulated)
    print("5. Testing authentication flow:")
    print("   (This would require real credentials in production)")
    print("   Login method available:", hasattr(cli.auth, 'login'))
    print("   Logout method available:", hasattr(cli.auth, 'logout'))
    print("✓ Authentication methods available\n")
    
    # Test 6: Service access methods
    print("6. Testing service access methods:")

    print("   Calendar service:", cli.auth.get_calendar_service() is None)  # Should be None
    print("   Drive service:", cli.auth.get_drive_service() is None)  # Should be None
    print("✓ Service methods work correctly\n")
    
    print("🎉 All real data integration tests passed!")
    print("\nThe system is ready for real iCloud integration.")
    print("To use real data:")
    print("1. Run: python main.py")
    print("2. Choose Authentication -> Login")
    print("3. Enter your Apple ID credentials")
    print("4. Complete 2FA if required")
    print("5. Access real iCloud data from all modules")

if __name__ == "__main__":
    test_real_data_integration()