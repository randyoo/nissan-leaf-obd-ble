# Bleak Retry Connector Integration

## Summary
This document describes the changes made to integrate `bleak-retry-connector` into the Nissan Leaf OBD BLE integration, addressing the warning message:
```
D4:36:39:89:30:C7: BleakClient.connect() called without bleak-retry-connector. 
For reliable connection establishment, use bleak_retry_connector.establish_connection().
```

## Changes Made

### 1. Updated `bleserial.py`
**File:** `custom_components/nissan_leaf_obd_ble/bleserial.py`

#### Import Changes:
- **Removed:** `from bleak import BleakClient, BleakError`
- **Added:** `from bleak_retry_connector import establish_connection, BleakClientWithServiceCache`
- **Kept:** `from bleak import BleakError` (still needed for error handling)

#### Type Annotation Changes:
- Changed `self.client: Optional[BleakClient]` to `self.client: Optional[BleakClientWithServiceCache]`

#### Connection Logic Changes in `open()` method:
**Before:**
```python
self.client = BleakClient(self.device)
await asyncio.wait_for(self.client.connect(), timeout=10.0)
```

**After:**
```python
# Use establish_connection with automatic retry logic
self.client = await establish_connection(
    BleakClientWithServiceCache,
    self.device,
    self.device.name or "Unknown Device",
    max_attempts=3,
    timeout=10.0
)
```

### 2. Updated `manifest.json`
**File:** `custom_components/nissan_leaf_obd_ble/manifest.json`

#### Requirements:
- **Before:** `"requirements": []`
- **After:** `"requirements": ["bleak-retry-connector>=3.0.5"]`

## Benefits of This Change

1. **Automatic Retry Logic**: The `establish_connection()` function automatically handles connection retries with exponential backoff, making the connection more reliable.

2. **Better Error Handling**: Built-in error handling for various BLE connection issues.

3. **Service Caching**: Using `BleakClientWithServiceCache` improves performance by caching service discovery results.

4. **Compliance**: Addresses the warning message from Home Assistant's Bluetooth integration, ensuring best practices are followed.

## Backward Compatibility

The changes maintain backward compatibility:
- The public API of the `bleserial` class remains unchanged
- All existing methods work exactly as before
- Only the internal connection mechanism has been updated

## Testing

To test these changes:
1. Install the package with dependencies: `pip install bleak-retry-connector>=3.0.5`
2. Run the integration in Home Assistant
3. Verify that the warning message no longer appears in logs
4. Check that connections are more reliable and retry automatically on failure

## References

- [bleak-retry-connector documentation](https://github.com/Bluetooth-Devices/bleak-retry-connector)
- [Home Assistant Bluetooth integration](https://developers.home-assistant.io/docs/en/integration_manifest.html#bluetooth)
