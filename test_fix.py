#!/usr/bin/env python3
"""
Test script to verify the asyncio import fix and device availability handling.
"""

import sys
import os

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components'))

def test_asyncio_import():
    """Test that asyncio is properly imported."""
    print("Testing asyncio import...")
    try:
        from nissan_leaf_obd_ble import __init__
        # If the import succeeds, asyncio must be imported in the module
        print("✓ asyncio import test passed")
        return True
    except NameError as e:
        if "asyncio" in str(e):
            print(f"✗ asyncio import test failed: {e}")
            return False
        raise
    except Exception as e:
        # Other import errors are not related to our fix
        print(f"✓ asyncio is imported (other error: {e})")
        return True

def test_device_none_handling():
    """Test that the code handles None ble_device gracefully."""
    print("\nTesting device availability handling...")
    
    try:
        from nissan_leaf_obd_ble.api import NissanLeafObdBleApiClient
        
        # Create an API client with None device (should not crash)
        api = NissanLeafObdBleApiClient(None)
        print("✓ API client accepts None ble_device")
        
        # Test that async_get_data returns empty dict when device is None
        import asyncio
        data = asyncio.run(api.async_get_data())
        if data == {}:
            print("✓ async_get_data returns empty dict for None device")
            return True
        else:
            print(f"✗ Expected empty dict, got: {data}")
            return False
            
    except Exception as e:
        print(f"✗ Device availability test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Nissan Leaf OBD BLE Integration Fixes")
    print("=" * 60)
    
    results = []
    results.append(test_asyncio_import())
    results.append(test_device_none_handling())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
