"""Module to implement a serial-like interface over BLE GATT."""

import asyncio
import logging
from typing import Optional

from bleak import BleakClient, BleakError
from bleak.backends.device import BLEDevice

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class bleserial:
    """Encapsulates the ble connection and make it appear something like a UART port."""

    __buffer = bytearray()

    def __init__(self, device: BLEDevice, service_uuid, characteristic_uuid_read, characteristic_uuid_write) -> None:
        """Initialise."""
        self.device = device
        self.service_uuid = service_uuid
        self.characteristic_uuid_read = characteristic_uuid_read
        self.characteristic_uuid_write = characteristic_uuid_write
        self.client: Optional[BleakClient] = None
        self._rx_buffer = bytearray()
        self._timeout: Optional[float] = None
        self._write_timeout: Optional[float] = None
        self._connection_attempts = 0
        self._last_write_success = True

    async def _wait_for_data(self, size):
        """Wait for data to be available in the buffer."""
        max_retries = 100  # ~1 second timeout
        for _ in range(max_retries):
            if len(self._rx_buffer) >= size:
                return
            await asyncio.sleep(0.01)
        logger.warning("Timeout waiting for %d bytes of data", size)

    async def _wait_for_line(self):
        """Wait for a complete line (containing \\n) to be available."""
        max_retries = 100  # ~1 second timeout
        for _ in range(max_retries):
            if b"\n" in self._rx_buffer:
                return
            await asyncio.sleep(0.01)
        logger.warning("Timeout waiting for line terminator")

    def reset_input_buffer(self):
        """Reset the input buffer."""
        logger.debug("Resetting input buffer")
        self._rx_buffer.clear()

    def reset_output_buffer(self):
        """Reset the output buffer."""
        logger.debug("Resetting output buffer")
        # Since there's no explicit output buffer, this is a no-op.

    def flush(self):
        """Reset the input and the output buffer."""
        self.reset_input_buffer()
        self.reset_output_buffer()

    @property
    def in_waiting(self):
        """Return the number of bytes in the receive buffer."""
        return len(self._rx_buffer)

    @property
    def timeout(self):
        """Timeout duration."""
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        """Set the timeout duration."""
        self._timeout = value

    @property
    def write_timeout(self):
        """Write timeout duration."""
        return self._write_timeout

    @write_timeout.setter
    def write_timeout(self, value):
        """Set the write timeout duration."""
        self._write_timeout = value

    def _notification_handler(self, sender, data):
        """Handle when a GATT notification arrives."""
        logger.debug("Notification received: %s", data)
        if data:  # Only extend buffer if we got actual data
            self._rx_buffer.extend(data)

    async def open(self):
        """Open the port with retry logic."""
        max_retries = 3
        base_delay = 0.5
        
        for attempt in range(max_retries):
            try:
                self.client = BleakClient(self.device)
                logger.debug("Connecting to device: %s (attempt %d/%d)", self.device, attempt + 1, max_retries)
                await asyncio.wait_for(self.client.connect(), timeout=10.0)
                logger.info("Connected to device: %s", self.device)
                
                logger.debug(
                    "Starting notifications on characteristic UUID: %s",
                    self.characteristic_uuid_read,
                )
                await asyncio.wait_for(
                    self.client.start_notify(
                        self.characteristic_uuid_read, self._notification_handler
                    ),
                    timeout=5.0
                )
                logger.info("Notifications started successfully")
                
                # Reset connection attempts on success
                self._connection_attempts = 0
                return
                
            except asyncio.TimeoutError:
                logger.warning("Connection timeout (attempt %d/%d)", attempt + 1, max_retries)
                if self.client:
                    try:
                        await self.client.disconnect()
                    except:
                        pass
                    self.client = None
            except BleakError as e:
                logger.warning("Failed to connect or start notifications (attempt %d/%d): %s", 
                             attempt + 1, max_retries, e)
                if self.client:
                    try:
                        await self.client.disconnect()
                    except:
                        pass
                    self.client = None
            except Exception as e:
                logger.error("Unexpected error during connection (attempt %d/%d): %s", 
                            attempt + 1, max_retries, e)
                if self.client:
                    try:
                        await self.client.disconnect()
                    except:
                        pass
                    self.client = None
            
            if attempt < max_retries - 1:
                await asyncio.sleep(base_delay * (2 ** attempt))
        
        logger.error("All connection attempts failed")
        raise BleakError("Failed to connect after multiple attempts")

    async def close(self):
        """Close the port gracefully."""
        if self.client:
            try:
                logger.debug(
                    "Stopping notifications on characteristic UUID: %s",
                    self.characteristic_uuid_read,
                )
                await asyncio.wait_for(
                    self.client.stop_notify(self.characteristic_uuid_read),
                    timeout=2.0
                )
                logger.debug("Notifications stopped")
            except (BleakError, asyncio.TimeoutError) as e:
                logger.warning("Failed to stop notifications: %s", e)
            
            try:
                logger.debug("Disconnecting from device")
                await asyncio.wait_for(self.client.disconnect(), timeout=2.0)
                logger.debug("Disconnected from device")
            except (BleakError, asyncio.TimeoutError) as e:
                logger.warning("Failed to disconnect: %s", e)
            finally:
                self.client = None

    async def write(self, data):
        """Write bytes with retry logic."""
        if isinstance(data, str):
            data = data.encode()
        
        max_retries = 2
        base_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                if not self.client or not self.client.is_connected:
                    logger.error("Cannot write: client not connected")
                    self._last_write_success = False
                    raise BleakError("Client not connected")
                
                logger.debug(
                    "Writing data to characteristic UUID: %s Data: %s",
                    self.characteristic_uuid_write,
                    data,
                )
                await asyncio.wait_for(
                    self.client.write_gatt_char(self.characteristic_uuid_write, data),
                    timeout=2.0
                )
                logger.debug("Data written successfully")
                self._last_write_success = True
                return
                
            except (BleakError, asyncio.TimeoutError) as e:
                logger.warning("Write attempt %d/%d failed: %s", attempt + 1, max_retries, e)
                self._last_write_success = False
                if attempt < max_retries - 1:
                    await asyncio.sleep(base_delay * (2 ** attempt))
            except Exception as e:
                logger.error("Unexpected error during write: %s", e)
                self._last_write_success = False
                raise
        
        logger.error("All write attempts failed")
        raise BleakError("Failed to write after multiple attempts")

    async def read(self, size=1):
        """Read from the buffer with timeout handling."""
        try:
            if not self.client or not self.client.is_connected:
                logger.error("Cannot read: client not connected")
                raise BleakError("Client not connected")
            
            logger.debug("Reading %s bytes of data", size)
            
            # Use timeout if set
            if self._timeout:
                try:
                    await asyncio.wait_for(self._wait_for_data(size), timeout=self._timeout)
                except asyncio.TimeoutError:
                    logger.warning("Read operation timed out after %s seconds", self._timeout)
                    raise BleakError(f"Read operation timed out after {self._timeout} seconds")
            else:
                await self._wait_for_data(size)
            
            data = self._rx_buffer[:size]
            self._rx_buffer = self._rx_buffer[size:]
            logger.debug("Read data: %s", data)
            return bytes(data)
        except Exception as e:
            logger.error("Failed to read data: %s", e)
            raise

    async def readline(self):
        """Read a whole line from the buffer with timeout handling."""
        try:
            if not self.client or not self.client.is_connected:
                logger.error("Cannot read line: client not connected")
                raise BleakError("Client not connected")
            
            logger.debug("Reading line")
            
            # Use timeout if set
            if self._timeout:
                try:
                    await asyncio.wait_for(self._wait_for_line(), timeout=self._timeout)
                except asyncio.TimeoutError:
                    logger.warning("Readline operation timed out after %s seconds", self._timeout)
                    raise BleakError(f"Readline operation timed out after {self._timeout} seconds")
            else:
                await self._wait_for_line()
            
            index = self._rx_buffer.index(b"\n") + 1
            data = self._rx_buffer[:index]
            self._rx_buffer = self._rx_buffer[index:]
            logger.debug("Read line: %s", data)
            return bytes(data)
        except BleakError:
            raise
        except Exception as e:
            logger.error("Failed to read line: %s", e)
            raise BleakError(f"Failed to read line: {e}") from e
