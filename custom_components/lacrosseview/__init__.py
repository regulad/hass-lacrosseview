"""LaCrosse View component for Home Assistant."""
from functools import partial
from typing import Optional
import time

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import DEVICE_CLASS_TEMPERATURE, TEMP_CELSIUS, TEMP_FAHRENHEIT, DEVICE_CLASS_HUMIDITY, \
    CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from pylacrosseview import Device, Field, WeatherStation

from .const import DOMAIN

PLATFORMS = [Platform.SENSOR]


def device_info_of(device: Device) -> DeviceInfo:
    """Return device info for device."""
    return DeviceInfo(
        identifiers={(DOMAIN, device.id)},
        model=device.sensor_type,
        manufacturer="LaCrosse",
        name=device.name.replace('_', ' ').title(),
    )


class LaCrosseViewSensor(SensorEntity):
    def __init__(self, hass: HomeAssistant, lacrosse_device: Device, field: Field):
        self._lacrosse_device = lacrosse_device
        self._field = field
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._state = None
        self._hass = hass

    def update(self) -> None:
        states = self._lacrosse_device.states(time_zone=self._hass.config.time_zone, start=time.time() - 3600)
        try:
            self._state = states[self._field][-1].value
        except IndexError:
            self._state = None

    @property
    def unique_id(self) -> str:
        return f"{self._lacrosse_device.id}_{self._field}"

    @property
    def device_info(self) -> DeviceInfo:
        return device_info_of(self._lacrosse_device)

    @property
    def name(self):
        return f"{self._lacrosse_device.name.replace('_', ' ').title()} {self._field}"

    @property
    def native_value(self):
        return self._state

    @property
    def available(self):
        return self._state is not None

    @property
    def device_class(self) -> Optional[str]:
        if self._field.unit == "degrees_celsius" or self._field.unit == "degrees_fahrenheit":
            return DEVICE_CLASS_TEMPERATURE
        elif self._field.unit == "relative_humidity":
            return DEVICE_CLASS_HUMIDITY
        else:
            return None

    @property
    def native_unit_of_measurement(self) -> str:
        if self._field.unit == "degrees_celsius":
            return TEMP_CELSIUS
        elif self._field.unit == "degrees_fahrenheit":
            return TEMP_FAHRENHEIT
        elif self._field.unit == "relative_humidity":
            return "%"
        else:
            return self._field.unit


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    domain_data = hass.data.setdefault(DOMAIN, {})
    ws = WeatherStation()
    uuid = entry.data[CONF_USERNAME]
    await hass.loop.run_in_executor(None, partial(ws.start, entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD]))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    domain_data[uuid] = ws
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    unique_id = config_entry.unique_id

    # Unload platforms.
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )

    # Clean up.
    hass.data[DOMAIN].pop(unique_id).close()

    return unload_ok
