"""The Chaptarr integration."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY, CONF_URL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ChaptarrApi
from .coordinator import ChaptarrConfigEntry, ChaptarrCoordinator

PLATFORMS = [Platform.BINARY_SENSOR, Platform.CALENDAR, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ChaptarrConfigEntry) -> bool:
    api = ChaptarrApi(async_get_clientsession(hass), entry.data[CONF_URL], entry.data[CONF_API_KEY])
    coordinator = ChaptarrCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ChaptarrConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
