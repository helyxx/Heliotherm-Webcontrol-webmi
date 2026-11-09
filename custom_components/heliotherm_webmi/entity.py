"""Gemeinsame Basis fuer alle Entitaeten."""
from __future__ import annotations

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .client import WebMIError
from .const import ADDR, DOMAIN


class WebMIEntity(CoordinatorEntity):
    _attr_has_entity_name = True

    def __init__(self, entry_id, client, coordinator, key: str, name: str) -> None:
        super().__init__(coordinator)
        self._client = client
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)}, name="Heliotherm WebControl",
            manufacturer="Heliotherm",
        )

    @property
    def _value(self):
        return (self.coordinator.data or {}).get(self._key)

    async def _write(self, value) -> None:
        """Wert schreiben und danach neu einlesen; Fehler als HA-Fehler melden."""
        try:
            await self._client.write(ADDR[self._key], value)
        except WebMIError as err:
            raise HomeAssistantError(f"{self.name}: {err}") from err
        await self.coordinator.async_request_refresh()
