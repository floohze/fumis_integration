"""Diagnostics support for Austroflamm Mo Duo."""
from __future__ import annotations

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import CONF_MAC, CONF_PASSWORD, DOMAIN

TO_REDACT = {CONF_MAC, CONF_PASSWORD}

async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry):
    """Return sanitized status data to help protocol research."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    return {
        "config_entry": async_redact_data(dict(entry.data), TO_REDACT),
        "status": coordinator.data,
    }
