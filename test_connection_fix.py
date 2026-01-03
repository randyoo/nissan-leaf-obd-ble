#!/usr/bin/env python3
"""
Test to verify the connection fix.

This test verifies that:
1. The bug where address was passed instead of ble_device is fixed
2. Logging levels have been appropriately adjusted
"""

def test_init_fix():
    """Verify that __init__.py passes ble_device correctly."""
    print("Testing __init__.py fix...")
    
    with open('custom_components/nissan_leaf_obd_ble/__init__.py', 'r') as f:
        content = f.read()
    
    # Check that we're passing ble_device
    if 'api = NissanLeafObdBleApiClient(ble_device)' in content:
        print("  ✓ PASS: __init__.py correctly passes ble_device to ApiClient")
        return True
    else:
        print("  ✗ FAIL: __init__.py does not pass ble_device correctly")
        return False

def test_logging_levels():
    """Verify that logging levels have been adjusted."""
    print("\nTesting logging level adjustments...")
    
    files_to_check = [
        ('custom_components/nissan_leaf_obd_ble/elm327.py', 'ELM327'),
        ('custom_components/nissan_leaf_obd_ble/obd.py', 'OBD'),
        ('custom_components/nissan_leaf_obd_ble/bleserial.py', 'BLE Serial'),
    ]
    
    all_passed = True
    
    for filepath, name in files_to_check:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check that we have appropriate DEBUG logging
        debug_count = content.count('logger.debug(')
        info_count = content.count('logger.info(')
        warning_count = content.count('logger.warning(')
        error_count = content.count('logger.error(')
        critical_count = content.count('logger.critical(')
        
        print(f"\n  {name}:")
        print(f"    DEBUG:   {debug_count}")
        print(f"    INFO:    {info_count}")
        print(f"    WARNING: {warning_count}")
        print(f"    ERROR:   {error_count}")
        print(f"    CRITICAL: {critical_count}")
        
        # Verify we have some DEBUG logging (for detailed operations)
        if debug_count > 0:
            print(f"    ✓ Has DEBUG level logging")
        else:
            print(f"    ⚠ No DEBUG level logging found")
        
        # Verify we have INFO logging (for important events)
        if info_count > 0:
            print(f"    ✓ Has INFO level logging")
        else:
            print(f"    ⚠ No INFO level logging found")
        
        # Check that we're not overusing WARNING/ERROR
        total_logs = debug_count + info_count + warning_count + error_count + critical_count
        if total_logs > 0:
            warning_percentage = (warning_count / total_logs) * 100
            error_percentage = (error_count / total_logs) * 100
            
            print(f"    WARNING percentage: {warning_percentage:.1f}%")
            print(f"    ERROR percentage:   {error_percentage:.1f}%")
            
            if warning_percentage < 30 and error_percentage < 20:
                print(f"    ✓ Logging levels look appropriate")
            else:
                print(f"    ⚠ High percentage of WARNING/ERROR logs")
        
    return all_passed

def test_specific_fixes():
    """Test specific fixes mentioned in the issue."""
    print("\nTesting specific fixes...")
    
    with open('custom_components/nissan_leaf_obd_ble/elm327.py', 'r') as f:
        elm_content = f.read()
    
    with open('custom_components/nissan_leaf_obd_ble/obd.py', 'r') as f:
        obd_content = f.read()
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Check that port opening errors are now DEBUG
    tests_total += 1
    if "logger.debug(\"An error occurred while opening port:" in elm_content:
        print("  ✓ Port opening errors logged at DEBUG level")
        tests_passed += 1
    else:
        print("  ✗ Port opening errors not at DEBUG level")
    
    # Test 2: Check that query failures when not connected are DEBUG
    tests_total += 1
    if "logger.debug(\"Query failed, no connection available" in obd_content:
        print("  ✓ Query failures logged at DEBUG level")
        tests_passed += 1
    else:
        print("  ✗ Query failures not at DEBUG level")
    
    # Test 3: Check that device disconnection while writing is INFO, not CRITICAL
    tests_total += 1
    if "logger.info(\"Device disconnected while writing:" in elm_content:
        print("  ✓ Device disconnection logged at INFO level")
        tests_passed += 1
    else:
        print("  ✗ Device disconnection not at INFO level")
    
    # Test 4: Check that failed port reads are DEBUG, not WARNING
    tests_total += 1
    if "logger.debug(\"Failed to read port" in elm_content:
        print("  ✓ Failed port reads logged at DEBUG level")
        tests_passed += 1
    else:
        print("  ✗ Failed port reads not at DEBUG level")
    
    print(f"\n  Score: {tests_passed}/{tests_total} tests passed")
    return tests_passed == tests_total

def main():
    """Run all tests."""
    print("=" * 70)
    print("Testing Nissan Leaf OBD BLE Connection Fixes")
    print("=" * 70)
    
    results = []
    
    results.append(test_init_fix())
    results.append(test_logging_levels())
    results.append(test_specific_fixes())
    
    print("\n" + "=" * 70)
    if all(results):
        print("✓ ALL TESTS PASSED!")
        print("=" * 70)
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("=" * 70)
        return 1

if __name__ == '__main__':
    exit(main())
