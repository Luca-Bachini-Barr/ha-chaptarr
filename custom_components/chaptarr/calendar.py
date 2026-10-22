"""Calendar for Chaptarr book releases."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .api import ChaptarrError
from .coordinator import ChaptarrConfigEntry
from .entity import ChaptarrEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ChaptarrConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([ChaptarrCalendar(entry.runtime_data)])


def _event(book: dict) -> CalendarEvent | None:
    released = dt_util.parse_datetime(book.get("releaseDate") or "")
    if released is None:
        return None
    day = dt_util.as_local(released).date()
    author = (book.get("author") or {}).get("authorName")
    kind = book.get("mediaType") or ""
    summary = f"{author} – {book.get('title')}" if author else book.get("title", "?")
    return CalendarEvent(
        start=day,
        end=day + timedelta(days=1),
        summary=summary,
        description=f"{kind}{' · ' + book['seriesTitle'] if book.get('seriesTitle') else ''}".strip(" ·"),
    )


class ChaptarrCalendar(ChaptarrEntity, CalendarEntity):
    _attr_name = None

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "calendar")

    @property
    def event(self) -> CalendarEvent | None:
        today = dt_util.now().date()
        events = sorted(
            (e for b in self.coordinator.data.calendar if (e := _event(b)) and e.end > today),
            key=lambda e: e.start,
        )
        return events[0] if events else None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        try:
            books = await self.coordinator.api.calendar(
                start_date.date().isoformat(), (end_date.date() + timedelta(days=1)).isoformat()
            )
        except ChaptarrError:
            return []
        return [e for b in books if (e := _event(b))]
