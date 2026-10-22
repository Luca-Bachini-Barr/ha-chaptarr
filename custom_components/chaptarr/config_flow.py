"""Config flow for Chaptarr."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY, CONF_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ChaptarrApi, ChaptarrAuthError, ChaptarrError
from .const import DEFAULT_URL, DOMAIN


class ChaptarrConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            api = ChaptarrApi(async_get_clientsession(self.hass), user_input[CONF_URL], user_input[CONF_API_KEY])
            try:
                status = await api.status()
            except ChaptarrAuthError:
                errors["base"] = "invalid_auth"
            except ChaptarrError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(status.get("installationId") or user_input[CONF_URL])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=status.get("instanceName") or "Chaptarr", data=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_URL, default=DEFAULT_URL): str, vol.Required(CONF_API_KEY): str}
            ),
            errors=errors,
        )
