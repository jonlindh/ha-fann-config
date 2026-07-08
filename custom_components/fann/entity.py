"""Base entity for FANN."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class FannEntity(CoordinatorEntity):
    """Base FANN entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, dbid: int) -> None:
        super().__init__(coordinator)
        self._dbid = dbid

    @property
    def device(self):
        return self.coordinator.get_device(self._dbid)

    @property
    def device_info(self) -> DeviceInfo:
        device = self.device

        return DeviceInfo(
            identifiers={(DOMAIN, str(self._dbid))},
            manufacturer="FANN",
            name=device.display_name,
            model=device.model,
            serial_number=device.nickname,
        )

    @property
    def available(self) -> bool:
        device = self.device
        return device is not None and device.connected
    
    @property
    def translation_key(self) -> str:
        """Return translation key."""
        return ""