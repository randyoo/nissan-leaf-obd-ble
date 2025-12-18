# How the Fix Works

## Scenario: Home Assistant Restarts When Car is Unavailable

### Before the Fix
1. **Startup**: Home Assistant starts and tries to load the Nissan Leaf OBD BLE integration
2. **Device Discovery**: The integration attempts to find the BLE device (OBD dongle in your car)
3. **Failure**: Device not found → `NameError: name 'asyncio' is not defined`
4. **Result**: Integration setup fails completely with a crash
5. **User Action Required**: User must manually reload the integration once the car is nearby and powered on

### After the Fix
1. **Startup**: Home Assistant starts and tries to load the Nissan Leaf OBD BLE integration
2. **Device Discovery**: The integration attempts to find the BLE device (OBD dongle in your car)
3. **Failure Handling**: Device not found → Graceful degradation
   - Logs a warning message: "Could not find OBDBLE device..."
   - Creates a dummy coordinator with `None` as the BLE device
   - Integration remains loaded but non-functional
4. **Bluetooth Monitoring**: The integration registers a callback to monitor for Bluetooth devices
5. **Car Returns**: When your car comes within range and powers up:
   - Bluetooth proxy detects the OBD dongle's broadcast
   - Callback `_async_specific_device_found()` is triggered
   - Integration detects: "Device was previously unavailable"
   - Logs: "Device came back in range! Reloading integration..."
   - **Automatic Reload**: The entire integration reloads itself
6. **Success**: All sensors are now properly set up and functional!
7. **Normal Operation**: Integration continues to monitor the car and refresh data as needed

## Key Technical Details

### 1. Asyncio Import Fix
```python
import asyncio  # Line 7 - This was missing!
```
This simple import fixes the immediate crash when `asyncio.sleep()` is called.

### 2. Graceful Device Unavailable Handling
```python
if not ble_device:
    _LOGGER.warning(
        "Could not find OBDBLE device with address %s. "
        "The integration will remain loaded but won't be functional until the car is in range.",
        address
    )
    # Create a dummy coordinator that will fail gracefully
    api = NissanLeafObdBleApiClient(None)
    coordinator = NissanLeafObdBleDataUpdateCoordinator(
        hass, address=address, api=api, options=entry.options
    )
    hass.data[DOMAIN][entry.entry_id] = coordinator
    return True  # Don't raise ConfigEntryNotReady!
```
Instead of raising `ConfigEntryNotReady` (which causes setup to fail), we:
- Log a clear warning message
- Create a coordinator with `None` as the BLE device
- Return `True` to indicate successful setup
- The integration stays loaded but sensors will show as unavailable

### 3. Automatic Recovery Mechanism
```python
@callback
def _async_specific_device_found(...):
    """Handle re-discovery of the device."""
    
    if not coordinator.api.ble_device:
        # Device was previously unavailable!
        _LOGGER.info(
            "Device %s came back in range! Reloading integration...",
            address
        )
        hass.async_create_task(async_reload_entry(hass, entry))
    else:
        # Device was already available, just refresh data
        hass.async_create_task(coordinator.async_request_refresh())
```
The callback checks if the coordinator has a valid BLE device:
- **If `None`**: Device just became available → Reload entire integration
- **If valid**: Device was already there → Just refresh sensor data

### 4. Initial Failure Tracking
```python
except Exception as err:
    _LOGGER.error("Initial refresh failed: %s", err)
    _LOGGER.info("Continuing setup despite initial refresh failure")
    coordinator._device_was_available = False  # Track this!
```
When the initial data refresh fails, we mark the coordinator so it knows to reload when the device is found.

## What You'll See in Your Logs

### On Startup (Car Unavailable)
```
WARNING: Could not find OBDBLE device with address XX:XX:XX:XX:XX:XX. 
The integration will remain loaded but won't be functional until the car is in range.
```

### When Car Returns
```
INFO: Device XX:XX:XX:XX:XX:XX came back in range! Reloading integration...
INFO: Successfully discovered BLE device: XX:XX:XX:XX:XX:XX
INFO: Finished fetching Nissan Leaf OBD BLE data in X.X seconds
```

### Normal Operation
```
DEBUG: Device is in range, requesting data refresh
DEBUG: Car is on, using fast polling: interval = 0:00:10
```

## Benefits Summary

✅ **No More Crashes**: The integration loads successfully even when the car isn't available

✅ **Automatic Recovery**: When your car returns and powers up, everything works automatically

✅ **Better User Experience**: No manual intervention required!

✅ **Clear Logging**: You can see exactly what's happening in your logs

✅ **Graceful Degradation**: The integration stays loaded but gracefully handles unavailable devices
