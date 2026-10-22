"""Sensors for Chaptarr."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import ChaptarrConfigEntry
from .entity import ChaptarrEntity


def _label(item: dict) -> str:
    book = item.get("book") or {}
    author = (item.get("author") or {}).get("authorName") or ""
    title = book.get("title") or item.get("title") or "?"
    return f"{author} – {title}" if author else title


async def async_setup_entry(
    hass: HomeAssistant, entry: ChaptarrConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    async_add_entities([ChaptarrQueueSensor(coordinator), ChaptarrWantedSensor(coordinator)])


class ChaptarrQueueSensor(ChaptarrEntity, SensorEntity):
    _attr_translation_key = "queue"
    _attr_icon = "mdi:download"
    _attr_native_unit_of_measurement = "books"
    _attr_state_class = SensorStateClass.TOTAL
    # Per-book attributes can easily exceed the recorder's 16 KB limit.
    _unrecorded_attributes = frozenset({MATCH_ALL})

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "queue")

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data.queue)

    @property
    def extra_state_attributes(self) -> dict:
        attrs: dict[str, str] = {}
        blocked = 0
        for item in self.coordinator.data.queue:
            size = item.get("size") or 0
            pct = 100 * (size - (item.get("sizeleft") or 0)) / size if size else 0
            state = item.get("trackedDownloadState") or item.get("status") or ""
            if state in ("importBlocked", "importFailed"):
                blocked += 1
            attrs[_label(item)] = f"{pct:.0f}% ({state})" if state not in ("downloading", "") else f"{pct:.1f}%"
        return {"import_blocked": blocked, **attrs}


class ChaptarrWantedSensor(ChaptarrEntity, SensorEntity):
    _attr_translation_key = "wanted"
    _attr_icon = "mdi:book-search"
    _attr_native_unit_of_measurement = "books"
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "wanted")

    @property
    def native_value(self) -> int:
        return self.coordinator.data.wanted_missing
