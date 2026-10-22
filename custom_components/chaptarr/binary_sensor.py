"""Binary sensors for Chaptarr."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import ChaptarrConfigEntry
from .entity import ChaptarrEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ChaptarrConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([ChaptarrHealthSensor(entry.runtime_data)])


class ChaptarrHealthSensor(ChaptarrEntity, BinarySensorEntity):
    _attr_translation_key = "health"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "health")

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.health)

    @property
    def extra_state_attributes(self) -> dict:
        return {h.get("source", "issue"): h.get("message", "") for h in self.coordinator.data.health}
