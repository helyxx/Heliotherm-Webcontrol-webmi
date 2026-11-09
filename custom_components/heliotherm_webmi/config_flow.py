"""Config Flow: Host und Intervall (Login ist fest hinterlegt)."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .client import WebMIClient, WebMIError
from .const import ADDR, CONF_INTERVAL, DEFAULT_INTERVAL, DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()
            client = WebMIClient(async_get_clientsession(self.hass), user_input[CONF_HOST])
            try:
                await client.connect()
                await client.read([ADDR["hkp_ist"]])
            except WebMIError:
                errors["base"] = "cannot_connect"
            else:
                if not client.logged_in:
                    errors["base"] = "invalid_auth"
                else:
                    return self.async_create_entry(title="Heliotherm WebControl",
                                                   data=user_input)
        schema = vol.Schema({
            vol.Required(CONF_HOST, default="10.0.0.3"): str,
            vol.Optional(CONF_INTERVAL, default=DEFAULT_INTERVAL): vol.All(
                vol.Coerce(int), vol.Range(min=10)),
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
