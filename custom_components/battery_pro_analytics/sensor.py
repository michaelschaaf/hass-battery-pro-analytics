import logging
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, DEFAULT_NOMINAL_CAPACITY, SOH_THRESHOLD_EOL, CONF_FALLBACK_CYCLES_YEAR

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        RctSohSensor(coordinator),
        RctDriftSensor(coordinator),
        RctAgingPrognosisSensor(coordinator)
    ]
    
    # Optional: Add a cycle sensor for the "Senior" (Stack 5)
    async_add_entities(entities)

class RctBatteryBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for RCT Battery Analytics sensors."""
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "rct_advanced_analytics")},
            "name": "Advanced Battery Analytics",
            "manufacturer": "RCT Power",
        }

class RctSohSensor(RctBatteryBaseSensor):
    """State of Health Sensor."""
    _attr_name = "Battery State of Health"
    _attr_unique_id = "rct_battery_soh"
    _attr_native_unit_of_measurement = "%"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        capacity = self.coordinator.data.get("ah_capacity")
        if capacity:
            return round((float(capacity) / DEFAULT_NOMINAL_CAPACITY) * 100, 2)
        return None

class RctDriftSensor(RctBatteryBaseSensor):
    """Cell Voltage Drift Sensor."""
    _attr_name = "Battery Cell Drift"
    _attr_unique_id = "rct_battery_cell_drift"
    _attr_native_unit_of_measurement = "V"
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        return self.coordinator.data.get("cell_drift")

class RctAgingPrognosisSensor(RctBatteryBaseSensor):
    """Prognosis in Years until 80% SOH."""
    _attr_name = "Battery Remaining Years Prognosis"
    _attr_unique_id = "rct_battery_prognosis_years"
    _attr_native_unit_of_measurement = "years"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        data = self.coordinator.data
        current_ah = data.get("ah_capacity")
        
        # Target: Stack 5 as the reference for cycles
        # We assume Stack 5 is the oldest (Senior)
        modules = data.get("modules", {})
        senior_cycles = None
        
        # Dynamic search for Stack 5 or the one with max cycles
        for sn, mod_data in modules.items():
            cycles = mod_data.get("cycles")
            if cycles and (senior_cycles is None or cycles > senior_cycles):
                senior_cycles = cycles

        if current_ah and senior_cycles and senior_cycles > 0:
            target_ah = DEFAULT_NOMINAL_CAPACITY * (SOH_THRESHOLD_EOL / 100)
            loss_total = DEFAULT_NOMINAL_CAPACITY - float(current_ah)
            
            if loss_total > 0:
                loss_per_cycle = loss_total / senior_cycles
                remaining_ah = float(current_ah) - target_ah
                remaining_cycles = remaining_ah / loss_per_cycle
                
                # Using the fallback or later a dynamic value for cycles/year
                return round(remaining_cycles / CONF_FALLBACK_CYCLES_YEAR, 1)
        
        return None