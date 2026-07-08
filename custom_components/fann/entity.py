"""Base entity for FANN."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN


class FannEntity(CoordinatorEntity):
    """Base FANN entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, dbid: int) -> None:
        """Initialize entity."""
        super().__init__(coordinator)
        self._dbid = dbid

    @property
    def device(self):
        """Return current device data."""
        return self.coordinator.get_device(self._dbid)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        device = self.device

        return DeviceInfo(
            identifiers={(DOMAIN, str(self._dbid))},
            manufacturer="FANN",
            name=device.model,
            model=device.model,
            serial_number=device.nickname,
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        device = self.device
        return device is not None and device.connected