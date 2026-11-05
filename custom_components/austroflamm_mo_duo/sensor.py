"""Sensors for Austroflamm Mo Duo."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import UnitOfTemperature, UnitOfPower
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL, estimated_pellet_rate_kg_h
from .coordinator import MoDuoCoordinator

SENSORS = {
    "temperature": ("Raumtemperatur", "temperature", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS),
    "target_temperature": ("Solltemperatur", "target_temperature", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS),
    "combustion_chamber_temperature": ("Brennraumtemperatur", "combustion_chamber_temperature", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS),
    "kw": ("Leistung", "kw", None, UnitOfPower.KILO_WATT),
    "actual_power": ("Aktuelle Leistungsstufe", "actual_power", None, None),
    "rpm": ("Gebläsedrehzahl", "rpm", None, "rpm"),
    "pressure": ("Unterdruck", "pressure", None, None),
    "fuel_quality": ("Brennstoffqualität", "fuel_quality", None, None),
    "fuel_quantity": ("Brennstoffmenge laut Fumis", "fuel_quantity", None, PERCENTAGE),
    "heating_time": ("Heizzeit", "heating_time", SensorDeviceClass.DURATION, UnitOfTime.HOURS),
    "time_to_service": ("Zeit bis Service", "time_to_service", SensorDeviceClass.DURATION, UnitOfTime.HOURS),
    "igniter_starts": ("Zündstarts", "igniter_starts", None, None),
    "misfires": ("Fehlzündungen", "misfires", None, None),
    "overheatings": ("Überhitzungen", "overheatings", None, None),
}

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: MoDuoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MoDuoSensor(coordinator, entry, key, meta) for key, meta in SENSORS.items()] + [PelletRateSensor(coordinator, entry)])

class MoDuoSensor(CoordinatorEntity[MoDuoCoordinator], SensorEntity):
    """A read-only Fumis status sensor."""

    def __init__(self, coordinator, entry, key, meta):
        super().__init__(coordinator)
        self.key = key
        self.meta = meta
        self._attr_name = f"{entry.title} {meta[0]}"
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_has_entity_name = False
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.mac)},
            "name": entry.title,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": coordinator.data.get("controller_version"),
        }
        self._attr_device_class = meta[2]
        self._attr_native_unit_of_measurement = meta[3]

    @property
    def native_value(self):
        return self.coordinator.data.get(self.key)

class PelletRateSensor(CoordinatorEntity[MoDuoCoordinator], SensorEntity):
    """Provisional pellet rate calculated from selected power level."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_name = f"{entry.title} Geschätzter Pelletverbrauch"
        self._attr_unique_id = f"{entry.entry_id}_estimated_pellet_rate"
        self._attr_native_unit_of_measurement = "kg/h"
        self._attr_icon = "mdi:weight-kilogram"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.mac)},
            "name": entry.title,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    @property
    def native_value(self):
        """Only calculate when API power is a recognized level 1–5."""
        try:
            level = int(self.coordinator.data.get("actual_power"))
        except (TypeError, ValueError):
            return None
        return estimated_pellet_rate_kg_h(level)
