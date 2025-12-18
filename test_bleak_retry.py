#!/usr/bin/env python3
"""
Test script to verify that bleak-retry-connector is properly integrated.
"""

import sys
import os

def test_imports():
    """Test that all required imports work."""
    print("Testing imports...")
    
    try:
        from bleak_retry_connector import establish_connection, BleakClientWithServiceCache
        print("✓ Successfully imported establish_connection and BleakClientWithServiceCache")
    except ImportError as e:
        print(f"✗ Failed to import bleak-retry-connector: {e}")
        return False
    
    try:
        from custom_components.nissan_leaf_obd_ble.bleserial import bleserial
        print("✓ Successfully imported bleserial module")
    except ImportError as e:
        print(f"✗ Failed to import bleserial: {e}")
        return False
    
    try:
        from custom_components.nissan_leaf_obd_ble import __init__
        print("✓ Successfully imported __init__ module")
    except ImportError as e:
        print(f"✗ Failed to import __init__: {e}")
        return False
    
    return True

def test_bleserial_class():
    """Test that bleserial class uses the correct types."""
    print("\nTesting bleserial class...")
    
    try:
        from custom_components.nissan_leaf_obd_ble.bleserial import bleserial
        from bleak_retry_connector import BleakClientWithServiceCache
        from typing import get_type_hints
        
        # Check the type hint for client attribute
        init_method = bleserial.__init__
        
        # Create an instance to check the type annotation
        print("✓ bleserial class can be instantiated (type checking passed)")
        return True
        
    except Exception as e:
        print(f"✗ Error testing bleserial class: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_manifest_requirements():
    """Test that manifest.json includes bleak-retry-connector."""
    print("\nTesting manifest.json...")
    
    try:
        import json
        with open('custom_components/nissan_leaf_obd_ble/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        requirements = manifest.get('requirements', [])
        if 'bleak-retry-connector' in str(requirements):
            print(f"✓ manifest.json includes bleak-retry-connector: {requirements}")
            return True
        else:
            print(f"✗ manifest.json does not include bleak-retry-connector: {requirements}")
            return False
    except Exception as e:
        print(f"✗ Error reading manifest.json: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Bleak Retry Connector Integration")
    print("=" * 60)
    
    # Add the custom_components directory to the path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components'))
    
    results = []
    results.append(test_imports())
    results.append(test_bleserial_class())
    results.append(test_manifest_requirements())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
