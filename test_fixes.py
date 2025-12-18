#!/usr/bin/env python3
"""Test script to verify the fixes for config flow issues."""

import sys
import os

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components'))

from nissan_leaf_obd_ble.coordinator import NissanLeafObdBleDataUpdateCoordinator
from nissan_leaf_obd_ble.config_flow import NissanLeafObdBleOptionsFlowHandler
from homeassistant.config_entries import ConfigEntry

class MockHass:
    """Mock HomeAssistant object."""
    pass

class MockApiClient:
    """Mock API client."""
    async def async_get_data(self):
        return {}

def test_coordinator_with_empty_options():
    """Test that coordinator handles empty options gracefully."""
    print("Testing coordinator with empty options...")
    try:
        hass = MockHass()
        api = MockApiClient()
        
        # This should not raise KeyError anymore
        coordinator = NissanLeafObdBleDataUpdateCoordinator(
            hass, address="AA:BB:CC:DD:EE:FF", api=api, options={}
        )
        
        # Check that default values are set
        assert hasattr(coordinator, '_fast_poll_interval'), "Missing _fast_poll_interval"
        assert hasattr(coordinator, '_slow_poll_interval'), "Missing _slow_poll_interval"
        assert hasattr(coordinator, '_xs_poll_interval'), "Missing _xs_poll_interval"
        
        print("  ✓ Coordinator handles empty options correctly")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_coordinator_with_none_options():
    """Test that coordinator handles None options gracefully."""
    print("Testing coordinator with None options...")
    try:
        hass = MockHass()
        api = MockApiClient()
        
        # This should not raise KeyError anymore
        coordinator = NissanLeafObdBleDataUpdateCoordinator(
            hass, address="AA:BB:CC:DD:EE:FF", api=api, options=None
        )
        
        # Check that default values are set
        assert hasattr(coordinator, '_fast_poll_interval'), "Missing _fast_poll_interval"
        assert hasattr(coordinator, '_slow_poll_interval'), "Missing _slow_poll_interval"
        assert hasattr(coordinator, '_xs_poll_interval'), "Missing _xs_poll_interval"
        
        print("  ✓ Coordinator handles None options correctly")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_coordinator_with_full_options():
    """Test that coordinator works with full options."""
    print("Testing coordinator with full options...")
    try:
        hass = MockHass()
        api = MockApiClient()
        
        options = {
            "fast_poll": 15,
            "slow_poll": 300,
            "xs_poll": 7200,
            "cache_values": True
        }
        
        coordinator = NissanLeafObdBleDataUpdateCoordinator(
            hass, address="AA:BB:CC:DD:EE:FF", api=api, options=options
        )
        
        # Check that values are set correctly
        assert coordinator._fast_poll_interval == 15, f"Expected 15, got {coordinator._fast_poll_interval}"
        assert coordinator._slow_poll_interval == 300, f"Expected 300, got {coordinator._slow_poll_interval}"
        assert coordinator._xs_poll_interval == 7200, f"Expected 7200, got {coordinator._xs_poll_interval}"
        
        print("  ✓ Coordinator handles full options correctly")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_options_flow_handler():
    """Test that OptionsFlowHandler can be instantiated."""
    print("Testing OptionsFlowHandler instantiation...")
    try:
        # Create a mock config entry
        class MockConfigEntry:
            def __init__(self):
                self.options = {"fast_poll": 10, "slow_poll": 300, "xs_poll": 3600}
                self.data = {}
                self.entry_id = "test_entry"
        
        config_entry = MockConfigEntry()
        options_flow = NissanLeafObdBleOptionsFlowHandler(config_entry)
        
        # Check that config_entry property works
        assert options_flow.config_entry is not None, "config_entry should not be None"
        assert options_flow.config_entry == config_entry, "config_entry should match"
        
        print("  ✓ OptionsFlowHandler instantiation works correctly")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing fixes for config flow issues")
    print("=" * 60)
    
    results = []
    results.append(test_coordinator_with_empty_options())
    results.append(test_coordinator_with_none_options())
    results.append(test_coordinator_with_full_options())
    results.append(test_options_flow_handler())
    
    print("=" * 60)
    if all(results):
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
