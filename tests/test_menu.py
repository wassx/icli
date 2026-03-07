#!/usr/bin/env python3
"""Test script for the iCloud CLI menu"""

import sys
from io import StringIO
from unittest.mock import patch

from main import show_main_menu, handle_menu_choice
from icli import iCloudCLI

def test_main_menu():
    """Test that the main menu displays correctly"""
    print("Testing main menu display...")
    
    cli = iCloudCLI()
    
    # Capture stdout
    captured_output = StringIO()
    with patch('sys.stdout', new=captured_output):
        show_main_menu(cli)
    
    output = captured_output.getvalue()
    assert "=== iCloud CLI" in output
    assert "1) Mail" in output
    assert "2) Calendar" in output
    assert "3) iCloud Drive" in output
    assert "4) Authentication" in output
    assert "5) Exit" in output
    
    print("✓ Main menu display test passed")

def test_menu_choices():
    """Test menu choice handling"""
    print("\nTesting menu choice handling...")
    
    cli = iCloudCLI()
    
    # Test exit choice
    result = handle_menu_choice("5", cli)
    assert result == False
    print("✓ Exit choice test passed")
    
    # Test invalid choice
    captured_output = StringIO()
    with patch('sys.stdout', new=captured_output):
        result = handle_menu_choice("99", cli)
    assert result == True
    assert "Invalid choice" in captured_output.getvalue()
    print("✓ Invalid choice test passed")
    
    # Test mail menu back choice
    with patch('builtins.input', side_effect=['3']):
        result = handle_menu_choice("1", cli)
    assert result == True
    print("✓ Mail menu back choice test passed")

if __name__ == "__main__":
    test_main_menu()
    test_menu_choices()
    print("\n✓ All tests passed!")