"""API for nissan leaf obd ble."""

import asyncio
import logging
from typing import Optional

from bleak.backends.device import BLEDevice
from bleak.exc import BleakError

from .commands import leaf_commands
from .obd import OBD, OBDStatus

_LOGGER: logging.Logger = logging.getLogger(__package__)


class NissanLeafObdBleApiClient:
    """API for connecting to the Nissan Leaf OBD BLE dongle."""

    def __init__(
        self,
        ble_device: BLEDevice,
    ) -> None:
        """Initialise."""
        self._ble_device = ble_device
        self._connection_attempts = 0
        self._last_successful_connection = None

    async def async_get_data(self) -> dict:
        """Get data from the API with retry logic for transient failures."""

        if self._ble_device is None:
            _LOGGER.debug("BLE device is None")
            return {}

        max_retries = 3
        base_delay = 0.5
        
        for attempt in range(max_retries):
            try:
                api = await self._create_obd_connection()
                
                if api is None:
                    _LOGGER.warning("Failed to create OBD connection (attempt %d/%d)", 
                                  attempt + 1, max_retries)
                    if attempt < max_retries - 1:
                        await asyncio.sleep(base_delay * (2 ** attempt))
                    continue
                
                data = await self._query_commands(api)
                await api.close()
                
                # Reset connection attempts on success
                self._connection_attempts = 0
                self._last_successful_connection = asyncio.get_event_loop().time()
                _LOGGER.debug("Successfully retrieved data: %s", data)
                return data
                
            except (BleakError, asyncio.TimeoutError, Exception) as err:
                _LOGGER.warning(
                    "Connection attempt %d/%d failed: %s", 
                    attempt + 1, max_retries, err
                )
                self._connection_attempts += 1
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(base_delay * (2 ** attempt))
                else:
                    _LOGGER.error("All connection attempts failed: %s", err)
                    return {}
        
        return {}

    async def _create_obd_connection(self):
        """Create OBD connection with error handling."""
        try:
            api = await OBD.create(self._ble_device, protocol="6")
            if api is None or api.status() == OBDStatus.NOT_CONNECTED:
                _LOGGER.warning("OBD connection failed - device not connected")
                return None
            return api
        except Exception as err:
            _LOGGER.warning("Error creating OBD connection: %s", err)
            return None

    async def _query_commands(self, api):
        """Query all commands with error handling."""
        data = {}
        for command in leaf_commands.values():
            try:
                response = await api.query(command, force=True)
                # the first command is the Mystery command. If this doesn't have a response, then none of the other will
                if command.name == "unknown" and len(response.messages) == 0:
                    _LOGGER.debug("Mystery command returned no data - car may be off")
                    break
                if response.value is not None:
                    data.update(response.value)
            except Exception as err:
                _LOGGER.warning("Error querying command %s: %s", command.name, err)
                # Continue with next command even if one fails
                continue
        return data
