from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        RctBatterySensor(coordinator, entry.entry_id, "ah_capacity", "Measured Capacity", "Ah"),
        RctBatterySensor(coordinator, entry.entry_id, "cell_drift", "Cell Voltage Drift", "V"),
        RctBatterySensor(coordinator, entry.entry_id, "soc", "Battery SOC", "%"),
        RctBatterySensor(coordinator, entry.entry_id, "soh", "Official Battery SOH", "%", enabled_default=False)
    ]
    async_add_entities(sensors)

# WICHTIG: Hier muss CoordinatorEntity als erstes stehen
class RctBatterySensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry_id, data_key, name, unit, enabled_default=True):
        """Pass den Coordinator an die Basis-Klasse weiter."""
        super().__init__(coordinator)
        
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
    def device_info(self):
        """Ordnet den Sensor einem Gerät zu (für die schöne Qnap-Style Übersicht)."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": "RCT Power Storage Analytics",
            "manufacturer": "RCT Power",
            "model": "Power Storage Pro",
            "sw_version": "1.0.0",
        }

    @property
    def native_value(self):
        """Holt den Wert direkt aus dem Speicher des Coordinators."""
        if self.coordinator.data is None:
            return None
            
        value = self.coordinator.data.get(self._data_key)
        if value is None:
            return None

        # Umrechnungen & Rundungen
        if self._data_key in ["soc", "soh"]:
            return round(value * 100, 1)
        if self._data_key == "ah_capacity":
            return round(value, 2)
        if self._data_key == "cell_drift":
            return round(value, 3)

        return value

    # Hinweis: available und should_poll werden automatisch von CoordinatorEntity geregelt