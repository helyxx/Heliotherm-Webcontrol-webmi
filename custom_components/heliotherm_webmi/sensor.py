"""Istwerte der Pumpen als Sensoren (werden von HA geloggt)."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.const import PERCENTAGE

from .const import DOMAIN
from .entity import WebMIEntity

SENSORS = {"hkp_ist": "HKP Istwert", "eq_ist": "EQ Istwert"}


async def async_setup_entry(hass, entry, async_add_entities):
    client, coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        WebMISensor(entry.entry_id, client, coordinator, k, n) for k, n in SENSORS.items()
    )


class WebMISensor(WebMIEntity, SensorEntity):
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        return self._value
