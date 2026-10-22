"""Base entity for Chaptarr."""

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ChaptarrCoordinator


class ChaptarrEntity(CoordinatorEntity[ChaptarrCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: ChaptarrCoordinator, key: str) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Chaptarr",
            manufacturer="Chaptarr",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=entry.data["url"],
        )
