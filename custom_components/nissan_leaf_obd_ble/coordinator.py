"""Coodinator for Nissan Leaf OBD BLE."""

from datetime import timedelta, datetime
import logging
from typing import Any

from homeassistant.components.bluetooth.api import async_address_present
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NissanLeafObdBleApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# when the device is in range, and the car is on, poll quickly to get
# as much data as we can before it turns off
FAST_POLL_INTERVAL = timedelta(seconds=10)

# when the device is in range, but the car is off, we need to poll
# occasionally to see whether the car has be turned back on. On some cars
# this causes a relay to click every time, so this interval needs to be
# as long as possible to prevent excessive wear on the relay.
SLOW_POLL_INTERVAL = timedelta(minutes=5)

# when the device is out of range, use ultra slow polling since a bluetooth
# advertisement message will kick it back into life when back in range.
# see __init__.py: _async_specific_device_found()
ULTRA_SLOW_POLL_INTERVAL = timedelta(hours=1)

# Maximum number of consecutive failures before increasing poll interval
MAX_CONSECUTIVE_FAILURES = 3

# Backoff multiplier for failed connections
FAILURE_BACKOFF_MULTIPLIER = 2

# Maximum poll interval when experiencing failures
MAX_POLL_INTERVAL_ON_FAILURE = timedelta(minutes=15)


class NissanLeafObdBleDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self, hass: HomeAssistant, address: str, api: NissanLeafObdBleApiClient, options
    ) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=FAST_POLL_INTERVAL,
            always_update=True,
        )
        self._address = address
        self.api = api
        self._cache_data: dict[str, Any] = {}
        self.cache_data = {}
        self.options = options
        self._consecutive_failures = 0
        self._last_failure_time = None
        self._device_was_available = True

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library with adaptive polling and failure handling."""

        # Check if the device is still available
        _LOGGER.debug("Check if the device is still available to connect")
        available = async_address_present(self.hass, self._address, connectable=True)
        
        # Handle device availability changes
        if not available and self._device_was_available:
            # Device just went out of range
            _LOGGER.info("Device went out of range")
            self._device_was_available = False
            self._consecutive_failures = 0  # Reset failures when device is unavailable
        elif available and not self._device_was_available:
            # Device just came back in range - reset failure counter
            _LOGGER.info("Device back in range")
            self._device_was_available = True
            self._consecutive_failures = 0

        if not available:
            # Device out of range? Switch to ultra slow polling interval for when it reappears
            _LOGGER.debug("Car out of range, using ultra slow polling")
            self.update_interval = timedelta(seconds=self._xs_poll_interval)
            _LOGGER.debug(
                "Ultra slow polling interval: %s",
                self.update_interval,
            )
            if self.options["cache_values"]:
                return self._cache_data
            return {}

        try:
            new_data = await self.api.async_get_data()
            
            # Reset failure counter on successful data retrieval
            self._consecutive_failures = 0
            self._last_failure_time = None
            
            if len(new_data) == 0:
                # Car is probably off. Switch to slow polling interval
                self.update_interval = timedelta(seconds=self._slow_poll_interval)
                _LOGGER.debug(
                    "Car is probably off, switch to slow polling: interval = %s",
                    self.update_interval,
                )
            else:
                # Car is on and responding. Use fast polling
                self.update_interval = timedelta(seconds=self._fast_poll_interval)
                _LOGGER.debug(
                    "Car is on, using fast polling: interval = %s",
                    self.update_interval,
                )
            
        except UpdateFailed as err:
            # Handle update failures with adaptive backoff
            self._consecutive_failures += 1
            self._last_failure_time = datetime.now()
            _LOGGER.warning(
                "Update failed (attempt %d): %s", 
                self._consecutive_failures, err
            )
            
            # Apply adaptive backoff based on consecutive failures
            if self._consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                backoff_interval = min(
                    timedelta(seconds=self._slow_poll_interval * FAILURE_BACKOFF_MULTIPLIER ** (self._consecutive_failures - MAX_CONSECUTIVE_FAILURES)),
                    MAX_POLL_INTERVAL_ON_FAILURE
                )
                self.update_interval = backoff_interval
                _LOGGER.warning(
                    "Multiple consecutive failures, increasing poll interval to %s",
                    self.update_interval,
                )
            
            # Return cached data if available and caching is enabled
            if self.options["cache_values"]:
                return self._cache_data
            raise  # Re-raise the exception to mark the update as failed
        except Exception as err:
            # Handle other exceptions (should not happen with proper error handling in API)
            _LOGGER.error("Unexpected error during update: %s", err)
            self._consecutive_failures += 1
            if self.options["cache_values"]:
                return self._cache_data
            raise UpdateFailed(f"Unexpected error: {err}") from err
        else:
            # Update cache and return data
            if self.options["cache_values"]:
                self.cache_data.update(new_data)
                return self.cache_data
            return new_data

    @property
    def options(self):
        """User configuration options."""
        return self._options

    @options.setter
    def options(self, options):
        """Set the configuration options."""
        self._options = options
        self._fast_poll_interval = options["fast_poll"]
        self._slow_poll_interval = options["slow_poll"]
        self._xs_poll_interval = options["xs_poll"]
