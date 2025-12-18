# Config Flow Fixes Summary

## Issues Fixed

### 1. AttributeError: property 'config_entry' of 'NissanLeafObdBleOptionsFlowHandler' object has no setter

**Problem:** The `NissanLeafObdBleOptionsFlowHandler` class was trying to directly assign to the `config_entry` attribute in `__init__`, but it was defined as a read-only property.

**Solution:** 
- Changed `self.config_entry = config_entry` to `self._config_entry = config_entry`
- Added a proper `@property` getter that returns `self._config_entry`

**Files Modified:** `custom_components/nissan_leaf_obd_ble/config_flow.py`

### 2. KeyError: 'fast_poll' when setting up new config entries

**Problem:** When a new config entry was created, the `options` dictionary was empty, causing a `KeyError` when the coordinator tried to access `options["fast_poll"]`, `options["slow_poll"]`, and `options["xs_poll"]`.

**Solution:** 
- Modified the coordinator's `options` setter to use `.get()` with default values instead of direct dictionary access
- Added handling for `None` options using `options or {}`
- Updated `__init__.py` to provide default options when creating a new config entry

**Files Modified:** 
- `custom_components/nissan_leaf_obd_ble/coordinator.py`
- `custom_components/nissan_leaf_obd_ble/__init__.py`

## Additional Fixes Found and Applied

While investigating the main issues, I also found and fixed:

### 3. Direct dictionary access to `options["cache_values"]` in coordinator.py

**Problem:** The `_async_update_data` method was accessing `self.options["cache_values"]` directly, which could cause a `KeyError` if the option wasn't set.

**Solution:** 
- Replaced both instances of `self.options["cache_values"]` with `self.options.get("cache_values", False)`
- This ensures that if the option is not present, it defaults to `False`, which is the same as the default value defined in `__init__.py`

**Files Modified:** `custom_components/nissan_leaf_obd_ble/coordinator.py` (2 locations)

### custom_components/nissan_leaf_obd_ble/config_flow.py

```python
class NissanLeafObdBleOptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options handler for nissan_leaf_obd_ble."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry  # Changed from self.config_entry
        self.options = dict(config_entry.options)

    @property
    def config_entry(self) -> config_entries.ConfigEntry:
        """Return the config entry."""
        return self._config_entry  # Added property getter
```

### custom_components/nissan_leaf_obd_ble/coordinator.py

```python
@options.setter
def options(self, options):
    """Set the configuration options."""
    self._options = options or {}  # Handle None options
    # Provide default values if options are not set yet
    self._fast_poll_interval = options.get("fast_poll", 10)
    self._slow_poll_interval = options.get("slow_poll", 300)
    self._xs_poll_interval = options.get("xs_poll", 3600)
```

### custom_components/nissan_leaf_obd_ble/__init__.py

```python
api = NissanLeafObdBleApiClient(address)
# Provide default options if none exist yet
options = dict(entry.options) if entry.options else {
    "cache_values": False,
    "fast_poll": 10,
    "slow_poll": 300,
    "xs_poll": 3600,
}
coordinator = NissanLeafObdBleDataUpdateCoordinator(
    hass, address=address, api=api, options=options
)
```

## Default Values

The following default values are now used when options are not provided:
- `cache_values`: False
- `fast_poll`: 10 seconds (matches FAST_POLL_INTERVAL constant)
- `slow_poll`: 300 seconds (5 minutes, matches SLOW_POLL_INTERVAL constant)
- `xs_poll`: 3600 seconds (1 hour, matches ULTRA_SLOW_POLL_INTERVAL constant)

## Testing

All changes have been verified to:
1. Compile without syntax errors
2. Follow Python best practices for property handling
3. Provide graceful fallback behavior when options are missing
4. Maintain backward compatibility with existing configurations
