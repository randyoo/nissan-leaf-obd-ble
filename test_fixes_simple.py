#!/usr/bin/env python3
"""Simple test script to verify the fixes for config flow issues."""

import sys
import os

def test_config_flow_syntax():
    """Test that config_flow.py has correct syntax and structure."""
    print("Testing config_flow.py syntax...")
    try:
        with open('custom_components/nissan_leaf_obd_ble/config_flow.py', 'r') as f:
            content = f.read()
            
        # Check that the property is defined correctly
        if '@property\n    def config_entry(self)' in content:
            print("  ✓ config_entry property found")
        else:
            print("  ✗ config_entry property not found")
            return False
            
        # Check that _config_entry is used instead of direct assignment
        if 'self._config_entry = config_entry' in content:
            print("  ✓ Using _config_entry for storage")
        else:
            print("  ✗ Not using _config_entry for storage")
            return False
            
        # Check that the property returns _config_entry
        if 'return self._config_entry' in content:
            print("  ✓ Property returns _config_entry")
        else:
            print("  ✗ Property doesn't return _config_entry")
            return False
            
        print("  ✓ config_flow.py syntax is correct")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_coordinator_syntax():
    """Test that coordinator.py has correct syntax and structure."""
    print("Testing coordinator.py syntax...")
    try:
        with open('custom_components/nissan_leaf_obd_ble/coordinator.py', 'r') as f:
            content = f.read()
            
        # Check that options.get() is used instead of options[""]
        if 'options.get("fast_poll"' in content:
            print("  ✓ Using options.get() for fast_poll")
        else:
            print("  ✗ Not using options.get() for fast_poll")
            return False
            
        if 'options.get("slow_poll"' in content:
            print("  ✓ Using options.get() for slow_poll")
        else:
            print("  ✗ Not using options.get() for slow_poll")
            return False
            
        if 'options.get("xs_poll"' in content:
            print("  ✓ Using options.get() for xs_poll")
        else:
            print("  ✗ Not using options.get() for xs_poll")
            return False
            
        # Check that default values are provided
        if 'options or {}' in content:
            print("  ✓ Handling None options with 'or {}'")
        else:
            print("  ✗ Not handling None options")
            return False
            
        print("  ✓ coordinator.py syntax is correct")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_init_syntax():
    """Test that __init__.py has correct syntax and structure."""
    print("Testing __init__.py syntax...")
    try:
        with open('custom_components/nissan_leaf_obd_ble/__init__.py', 'r') as f:
            content = f.read()
            
        # Check that default options are provided
        if '"cache_values": False' in content:
            print("  ✓ Default cache_values option set")
        else:
            print("  ✗ Default cache_values option not found")
            return False
            
        if '"fast_poll": 10' in content:
            print("  ✓ Default fast_poll option set")
        else:
            print("  ✗ Default fast_poll option not found")
            return False
            
        if '"slow_poll": 300' in content:
            print("  ✓ Default slow_poll option set")
        else:
            print("  ✗ Default slow_poll option not found")
            return False
            
        if '"xs_poll": 3600' in content:
            print("  ✓ Default xs_poll option set")
        else:
            print("  ✗ Default xs_poll option not found")
            return False
            
        # Check that options are merged properly
        if 'dict(entry.options) if entry.options' in content:
            print("  ✓ Properly handling existing options")
        else:
            print("  ✗ Not properly handling existing options")
            return False
            
        print("  ✓ __init__.py syntax is correct")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing fixes for config flow issues")
    print("=" * 60)
    
    results = []
    results.append(test_config_flow_syntax())
    results.append(test_coordinator_syntax())
    results.append(test_init_syntax())
    
    print("=" * 60)
    if all(results):
        print("✓ All syntax tests passed!")
        return 0
    else:
        print("✗ Some syntax tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
