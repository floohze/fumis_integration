"""Fumis cloud API coordinator for Austroflamm Mo Duo."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_URL, DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

class MoDuoCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch and normalize read-only Fumis status data."""

    def __init__(self, hass: HomeAssistant, session: aiohttp.ClientSession, mac: str, password: str):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.session = session
        self.mac = mac
        self.password = password

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch status from the Fumis cloud API."""
        payload = {
            "unit": {"id": self.mac, "type": 0, "pin": self.password},
            "apiVersion": "1",
        }
        try:
            async with asyncio.timeout(20):
                async with self.session.get(
                    API_URL,
                    headers={
                        "Accept": "application/json",
                        "appname": "HomeAssistant-AustroflammMoDuo",
                        "password": self.password,
                        "User-Agent": "HomeAssistant-AustroflammMoDuo/0.1.0",
                        "username": self.mac,
                    },
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    raw = await response.json()
        except (TimeoutError, aiohttp.ClientError, ValueError) as err:
            raise UpdateFailed(f"Fumis API request failed: {err}") from err

        if not isinstance(raw, dict):
            raise UpdateFailed("Fumis API returned an unexpected response")
        return self._normalize(raw)

    @staticmethod
    def _normalize(raw: dict[str, Any]) -> dict[str, Any]:
        """Extract known read-only values without assuming optional fields exist."""
        unit = raw.get("unit") or {}
        controller = raw.get("controller") or {}
        stats = controller.get("statistic") or {}
        power = controller.get("power") or {}
        diagnostic = controller.get("diagnostic") or {}
        variables = diagnostic.get("variables") or []
        temperatures = controller.get("temperatures") or []
        fuels = controller.get("fuels") or []
        eco = controller.get("ecoMode") or {}

        def variable_value(identifier: int):
            item = next((x for x in variables if isinstance(x, dict) and x.get("id") == identifier), {})
            return item.get("value")

        room = next(
            (x for x in temperatures if isinstance(x, dict) and x.get("onMainScreen") is True and (x.get("actualType") or 0) > 0),
            {},
        )
        chamber = next((x for x in temperatures if isinstance(x, dict) and x.get("id") == 7), {})
        fuel = next((x for x in fuels if isinstance(x, dict) and x.get("id") == 1), {})

        return {
            "unit_id": unit.get("id"),
            "unit_version": unit.get("version"),
            "controller_version": controller.get("version"),
            "rssi": unit.get("rssi"),
            "state_id": controller.get("command"),
            "status_id": controller.get("status"),
            "temperature": room.get("actual"),
            "target_temperature": room.get("set"),
            "temperature_id": room.get("id"),
            "combustion_chamber_temperature": chamber.get("actual", variable_value(11)),
            "kw": power.get("kw"),
            "actual_power": power.get("actualPower"),
            "rpm": variable_value(34),
            "pressure": variable_value(35),
            "time_to_service": controller.get("timeToService"),
            "heating_time": stats.get("heatingTime"),
            "igniter_starts": stats.get("igniterStarts"),
            "misfires": stats.get("misfires"),
            "overheatings": stats.get("overheatings"),
            "uptime": stats.get("uptime"),
            "fuel_quality": fuel.get("quality"),
            "fuel_quantity": fuel.get("quantity"),
            "eco_mode": eco.get("ecoModeEnable"),
            "timers": controller.get("timers") or [],
            "raw_status_fields": {
                "diagnostic_parameter_count": len(diagnostic.get("parameters") or []),
                "diagnostic_variable_count": len(variables),
            },
        }
