#!/usr/bin/env python3
"""Comprehensive test to verify all fixes work correctly."""

import sys

def test_all_direct_accesses_removed():
    """Verify that no direct dictionary accesses remain in the code."""
    print("Testing that all direct dictionary accesses have been removed...")
    
    import subprocess
    result = subprocess.run(
        ['grep', '-r', r'options\[', 'custom_components/nissan_leaf_obd_ble/'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and result.stdout.strip():
        print(f"  ✗ Found direct dictionary accesses:\n{result.stdout}")
        return False
    else:
        print("  ✓ No direct dictionary accesses found")
        return True

def test_all_get_methods_present():
    """Verify that options.get() is used for all option accesses."""
    print("Testing that options.get() is used appropriately...")
    
    import subprocess
    result = subprocess.run(
        ['grep', '-r', 'options.get(', 'custom_components/nissan_leaf_obd_ble/'],
        capture_output=True,
        text=True
    )
    
    if not result.stdout.strip():
        print("  ✗ No options.get() calls found")
        return False
    
    # Just verify that we have the expected number of get() calls
    lines = [line for line in result.stdout.strip().split('\n') if line.strip()]
    expected_count = 5  # fast_poll, slow_poll, xs_poll (twice), cache_values (twice)
    
    if len(lines) >= expected_count:
        print(f"  ✓ Found {len(lines)} options.get() calls (expected at least {expected_count})")
        return True
    else:
        print(f"  ✗ Only found {len(lines)} options.get() calls (expected at least {expected_count})")
        return False

def test_property_pattern():
    """Verify that the config_entry property pattern is correct."""
    print("Testing config_entry property pattern...")
    
    with open('custom_components/nissan_leaf_obd_ble/config_flow.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('self._config_entry = config_entry', 'Using _config_entry for storage'),
        ('@property', 'Property decorator present'),
        ('def config_entry(self)', 'config_entry method defined'),
        ('return self._config_entry', 'Returns _config_entry')
    ]
    
    all_passed = True
    for pattern, description in checks:
        if pattern in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} - NOT FOUND")
            all_passed = False
    
    return all_passed

def test_default_values():
    """Verify that default values are properly defined."""
    print("Testing default values...")
    
    with open('custom_components/nissan_leaf_obd_ble/__init__.py', 'r') as f:
        content = f.read()
    
    expected_defaults = [
        ('"cache_values": False', 'cache_values default'),
        ('"fast_poll": 10', 'fast_poll default'),
        ('"slow_poll": 300', 'slow_poll default'),
        ('"xs_poll": 3600', 'xs_poll default')
    ]
    
    all_passed = True
    for pattern, description in expected_defaults:
        if pattern in content:
            print(f"  ✓ {description} present")
        else:
            print(f"  ✗ {description} missing")
            all_passed = False
    
    return all_passed

def test_none_handling():
    """Verify that None options are handled properly."""
    print("Testing None options handling...")
    
    with open('custom_components/nissan_leaf_obd_ble/coordinator.py', 'r') as f:
        content = f.read()
    
    if 'options or {}' in content:
        print("  ✓ None handling with 'or {}' present")
        return True
    else:
        print("  ✗ None handling missing")
        return False

def main():
    """Run all comprehensive tests."""
    print("=" * 70)
    print("Comprehensive Test Suite for Config Flow Fixes")
    print("=" * 70)
    
    results = []
    results.append(test_all_direct_accesses_removed())
    results.append(test_all_get_methods_present())
    results.append(test_property_pattern())
    results.append(test_default_values())
    results.append(test_none_handling())
    
    print("=" * 70)
    if all(results):
        print("✓ All comprehensive tests passed!")
        return 0
    else:
        print("✗ Some comprehensive tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
