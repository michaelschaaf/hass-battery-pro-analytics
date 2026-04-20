from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from . import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        RctBatterySensor(coordinator, entry.entry_id, "ah_capacity", "Measured Capacity", "Ah"),
        RctBatterySensor(coordinator, entry.entry_id, "cell_drift", "Cell Voltage Drift", "V"),
        RctBatterySensor(coordinator, entry.entry_id, "soc", "Battery SOC", "%"),
        RctBatterySensor(coordinator, entry.entry_id, "soh", "Official Battery SOH", "%", enabled_default=False)
    ]
    async_add_entities(sensors)

class RctBatterySensor(SensorEntity):
    def __init__(self, coordinator, entry_id, data_key, name, unit, enabled_default=True):
        self.coordinator = coordinator
        self._data_key = data_key
        self._attr_name = f"RCT Battery {name}"
        self._attr_native_unit_of_measurement = unit
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{data_key}"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_entity_registry_enabled_default = enabled_default
        
        if data_key in ["soc", "soh"]:
            self._attr_device_class = SensorDeviceClass.BATTERY
        elif data_key == "cell_drift":
            self._attr_device_class = SensorDeviceClass.VOLTAGE

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return None
            
        value = self.coordinator.data.get(self._data_key)
        if value is None:
            return None

        if self._data_key in ["soc", "soh"]:
            return round(value * 100, 1)
        if self._data_key == "ah_capacity":
            return round(value, 2)
        if self._data_key == "cell_drift":
            return round(value, 3)

        return value

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success