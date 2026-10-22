"""Data coordinator for Chaptarr."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import ChaptarrApi, ChaptarrAuthError, ChaptarrError
from .const import CALENDAR_DAYS, DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


@dataclass
class ChaptarrData:
    queue: list[dict] = field(default_factory=list)
    wanted_missing: int = 0
    health: list[dict] = field(default_factory=list)
    calendar: list[dict] = field(default_factory=list)


type ChaptarrConfigEntry = ConfigEntry[ChaptarrCoordinator]


class ChaptarrCoordinator(DataUpdateCoordinator[ChaptarrData]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, api: ChaptarrApi) -> None:
        super().__init__(
            hass, _LOGGER, config_entry=entry, name=DOMAIN, update_interval=SCAN_INTERVAL
        )
        self.api = api

    async def _async_update_data(self) -> ChaptarrData:
        now = dt_util.utcnow()
        start = now.date().isoformat()
        end = (now + timedelta(days=CALENDAR_DAYS)).date().isoformat()
        try:
            return ChaptarrData(
                queue=await self.api.queue(),
                wanted_missing=await self.api.wanted_missing_total(),
                health=await self.api.health(),
                calendar=await self.api.calendar(start, end),
            )
        except ChaptarrAuthError as err:
            raise ConfigEntryAuthFailed from err
        except ChaptarrError as err:
            raise UpdateFailed(str(err)) from err
