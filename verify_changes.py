#!/usr/bin/env python3
"""
Verification script to ensure all changes are correct.
"""

import json
import os

def verify_bleserial_imports():
    """Verify that bleserial.py has the correct imports."""
    print("Verifying bleserial.py imports...")
    
    file_path = 'custom_components/nissan_leaf_obd_ble/bleserial.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    checks = [
        ('from bleak_retry_connector import establish_connection', 'establish_connection import'),
        ('BleakClientWithServiceCache', 'BleakClientWithServiceCache import'),  # Can be in import or usage
        ('self.client: Optional[BleakClientWithServiceCache]', 'type annotation for client'),
        ('await establish_connection(', 'establish_connection call'),
    ]
    
    all_passed = True
    for check_str, description in checks:
        if check_str in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} - NOT FOUND")
            all_passed = False
    
    # Verify old imports are removed
    if 'from bleak import BleakClient' in content:
        print("  ✗ Old BleakClient import still present")
        all_passed = False
    else:
        print("  ✓ Old BleakClient import removed")
    
    return all_passed

def verify_manifest():
    """Verify that manifest.json has the correct requirements."""
    print("\nVerifying manifest.json...")
    
    file_path = 'custom_components/nissan_leaf_obd_ble/manifest.json'
    with open(file_path, 'r') as f:
        manifest = json.load(f)
    
    requirements = manifest.get('requirements', [])
    
    if 'bleak-retry-connector' in str(requirements):
        print(f"  ✓ bleak-retry-connector in requirements: {requirements}")
        return True
    else:
        print(f"  ✗ bleak-retry-connector NOT in requirements: {requirements}")
        return False

def verify_no_direct_connect():
    """Verify that there are no direct BleakClient.connect() calls."""
    print("\nVerifying no direct connect() calls...")
    
    file_path = 'custom_components/nissan_leaf_obd_ble/bleserial.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check for patterns that would indicate direct connect() calls
    bad_patterns = [
        'BleakClient(self.device).connect()',
        'self.client.connect()',  # This is OK if it's the retry connector client
    ]
    
    all_passed = True
    for pattern in bad_patterns:
        if pattern in content and 'establish_connection' not in content.split(pattern)[0][-100:]:
            print(f"  ✗ Found direct connect() call: {pattern}")
            all_passed = False
    
    if all_passed:
        print("  ✓ No direct BleakClient.connect() calls found")
    
    return all_passed

def verify_connection_parameters():
    """Verify that establish_connection is called with proper parameters."""
    print("\nVerifying establish_connection parameters...")
    
    file_path = 'custom_components/nissan_leaf_obd_ble/bleserial.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    checks = [
        ('BleakClientWithServiceCache', 'client class'),
        ('self.device', 'device parameter'),
        ('max_attempts=3', 'max_attempts parameter'),
        ('timeout=10.0', 'timeout parameter'),
    ]
    
    all_passed = True
    for check_str, description in checks:
        if check_str in content:
            print(f"  ✓ {description} present")
        else:
            print(f"  ✗ {description} NOT FOUND")
            all_passed = False
    
    return all_passed

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Verifying Bleak Retry Connector Integration Changes")
    print("=" * 60)
    
    results = []
    results.append(verify_bleserial_imports())
    results.append(verify_manifest())
    results.append(verify_no_direct_connect())
    results.append(verify_connection_parameters())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✓ All verifications passed!")
        print("\nThe integration has been successfully updated to use")
        print("bleak-retry-connector. The warning message should no longer appear.")
        return 0
    else:
        print("✗ Some verifications failed")
        return 1

if __name__ == "__main__":
    exit(main())
