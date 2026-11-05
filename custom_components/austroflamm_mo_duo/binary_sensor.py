"""Binary sensors for Austroflamm Mo Duo."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import MoDuoCoordinator

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: MoDuoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MoDuoRunningSensor(coordinator, entry)])

class MoDuoRunningSensor(CoordinatorEntity[MoDuoCoordinator], BinarySensorEntity):
    """Whether the controller reports an active combustion state."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_name = f"{entry.title} Betrieb"
        self._attr_unique_id = f"{entry.entry_id}_running"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.mac)},
            "name": entry.title,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    @property
    def is_on(self):
        status = self.coordinator.data.get("status_id")
        return status in {10, 20, 21, 30, 40, 60, 80, 90, 100, 110}
