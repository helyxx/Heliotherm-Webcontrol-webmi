"""Handwerte der Pumpen (lesen und schreiben)."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import PERCENTAGE

from .const import DOMAIN
from .entity import WebMIEntity

NUMBERS = {"hkp_handwert": "HKP Handwert", "eq_handwert": "EQ Handwert"}


async def async_setup_entry(hass, entry, async_add_entities):
    client, coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        WebMINumber(entry.entry_id, client, coordinator, k, n) for k, n in NUMBERS.items()
    )


class WebMINumber(WebMIEntity, NumberEntity):
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX

    @property
    def native_value(self):
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        await self._write(int(value))
