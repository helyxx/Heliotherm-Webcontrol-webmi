"""Hand-Betrieb ein/aus (aus = Auto)."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN
from .entity import WebMIEntity

SWITCHES = {"hkp_hand_aktiv": "HKP Handbetrieb", "eq_hand_aktiv": "EQ Handbetrieb"}


async def async_setup_entry(hass, entry, async_add_entities):
    client, coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        WebMISwitch(entry.entry_id, client, coordinator, k, n) for k, n in SWITCHES.items()
    )


class WebMISwitch(WebMIEntity, SwitchEntity):
    @property
    def is_on(self):
        v = self._value
        if v is None:
            return None
        if isinstance(v, str):  # "0"/"1" bzw. "false"/"true" waeren sonst immer True
            return v.strip().lower() not in ("", "0", "false")
        return bool(v)

    async def async_turn_on(self, **kwargs) -> None:
        await self._write(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self._write(False)
