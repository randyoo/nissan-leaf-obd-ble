"""Custom integration to integrate Nissan Leaf OBD BLE with Home Assistant.

For more details about this integration, please refer to
https://github.com/pbutterworth/nissan-leaf-obd-ble
"""

import logging

from bleak_retry_connector import get_device

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import Config, HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady

from .api import NissanLeafObdBleApiClient
from .const import DOMAIN, PLATFORMS, STARTUP_MESSAGE
from .coordinator import NissanLeafObdBleDataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    address: str = entry.data[CONF_ADDRESS]
    
    # Try to find the BLE device with retry logic
    max_retries = 3
    base_delay = 1.0
    ble_device = None
    
    for attempt in range(max_retries):
        try:
            ble_device = bluetooth.async_ble_device_from_address(
                hass, address.upper(), True
            )
            if not ble_device:
                _LOGGER.info("Device not found via Home Assistant Bluetooth, trying direct discovery (attempt %d/%d)", 
                           attempt + 1, max_retries)
                ble_device = await get_device(address)
            
            if ble_device:
                _LOGGER.info("Successfully discovered BLE device: %s", address)
                break
            
            if attempt < max_retries - 1:
                await asyncio.sleep(base_delay * (2 ** attempt))
        except Exception as err:
            _LOGGER.warning("Error discovering device (attempt %d/%d): %s", 
                          attempt + 1, max_retries, err)
            if attempt < max_retries - 1:
                await asyncio.sleep(base_delay * (2 ** attempt))
    
    if not ble_device:
        raise ConfigEntryNotReady(
            f"Could not find OBDBLE device with address {address}"
        )

    api = NissanLeafObdBleApiClient(ble_device)
    coordinator = NissanLeafObdBleDataUpdateCoordinator(
        hass, address=address, api=api, options=entry.options
    )

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Initial refresh with error handling
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("Initial refresh failed: %s", err)
        # Don't fail the setup, just log the error and continue
        _LOGGER.info("Continuing setup despite initial refresh failure")
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    @callback
    def _async_specific_device_found(
        service_info: bluetooth.BluetoothServiceInfoBleak,
        change: bluetooth.BluetoothChange,
    ) -> None:
        """Handle re-discovery of the device."""
        _LOGGER.debug("New service_info: %s - %s", service_info, change)
        # have just discovered the device is back in range - ping the coordinator to update immediately
        hass.async_create_task(coordinator.async_request_refresh())

    # stuff to do when cleaning up
    entry.async_on_unload(
        bluetooth.async_register_callback(
            hass,
            _async_specific_device_found,
            {"address": address},
            bluetooth.BluetoothScanningMode.ACTIVE,
        )  # does the register callback, and returns a cancel callback for cleanup
    )

    async def update_options_listener(hass: HomeAssistant | None, entry: ConfigEntry):
        """Handle options update."""
        coordinator.options = entry.options

    entry.async_on_unload(
        entry.add_update_listener(update_options_listener)
    )  # add the listener for when the user changes options

    # entry.add_update_listener(async_reload_entry)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    hass.data.pop(DOMAIN)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
