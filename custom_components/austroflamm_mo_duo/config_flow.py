"""Config flow for Austroflamm Mo Duo."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_URL, CONF_MAC, DOMAIN

class MoDuoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the Mo Duo."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the user step."""
        errors = {}
        if user_input is not None:
            mac = user_input[CONF_MAC].strip().upper().replace(":", "").replace("-", "")
            password = user_input[CONF_PASSWORD].strip()
            if len(mac) != 12:
                errors["base"] = "invalid_mac"
            else:
                await self.async_set_unique_id(mac)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME].strip() or "Austroflamm Mo Duo",
                    data={CONF_MAC: mac, CONF_PASSWORD: password},
                )

        schema = vol.Schema({
            vol.Required(CONF_NAME, default="Austroflamm Mo Duo"): str,
            vol.Required(CONF_MAC): str,
            vol.Required(CONF_PASSWORD): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
