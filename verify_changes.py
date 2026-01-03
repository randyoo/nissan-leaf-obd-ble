#!/usr/bin/env python3
"""Verify the changes made to reduce log spam."""

import re

def check_file_log_levels(filepath, module_name):
    """Check logging levels in a file."""
    print(f"\n{module_name}:")
    print("=" * 60)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find all logger calls
    logger_pattern = r'logger\.(\w+)\([^)]*\)'
    matches = re.findall(logger_pattern, content)
    
    if not matches:
        print("  No logger calls found")
        return
    
    # Count each level
    levels = {}
    for level in matches:
        levels[level] = levels.get(level, 0) + 1
    
    # Sort by count descending
    for level, count in sorted(levels.items(), key=lambda x: x[1], reverse=True):
        print(f"  {level:8s}: {count}")
    
    return levels

def main():
    """Main verification function."""
    print("Verifying changes to reduce log spam")
    print("=" * 60)
    
    # Check key files
    files = [
        ('custom_components/nissan_leaf_obd_ble/elm327.py', 'ELM327 Module'),
        ('custom_components/nissan_leaf_obd_ble/obd.py', 'OBD Module'),
        ('custom_components/nissan_leaf_obd_ble/bleserial.py', 'BLE Serial Module'),
    ]
    
    for filepath, module_name in files:
        check_file_log_levels(filepath, module_name)
    
    print("\n" + "=" * 60)
    print("Summary of changes:")
    print("=" * 60)
    print("1. Fixed bug in __init__.py: Now passing ble_device instead of address")
    print("2. Reduced WARNING logs to DEBUG for connection issues")
    print("3. Reduced INFO logs to DEBUG for expected operations")
    print("4. Improved error handling for disconnections")
    print("5. Made logging more appropriate for different scenarios")

if __name__ == '__main__':
    main()
