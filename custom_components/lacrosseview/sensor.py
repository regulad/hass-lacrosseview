import logging

import homeassistant.helpers.config_validation as cv
import voluptuous
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import TEMP_FAHRENHEIT, CONF_USERNAME, CONF_PASSWORD, TEMP_CELSIUS
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import Entity, DeviceInfo

REQUIREMENTS = ['pylacrosseview==0.1.2']

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    voluptuous.Required(CONF_USERNAME): cv.string,
    voluptuous.Required(CONF_PASSWORD): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    from pylacrosseview import WeatherStation
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    weather_station = WeatherStation()
    weather_station.start(username, password)
    entities = []
    for device in weather_station.devices:
        for field in device.states().keys():
            entities.append(LaCrosseViewSensor(device, field))
    add_devices(entities)


class LaCrosseViewSensor(Entity):
    def __init__(self, lacrosse_device, field):
        self._lacrosse_device = lacrosse_device
        self._field = field
        self._state = None

    def update(self) -> None:
        states = self._lacrosse_device.states()
        self._state = states[self._field][-1].value

    @property
    def unique_id(self) -> str:
        return f"{self._lacrosse_device.id}_{self._field}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={("lacrosse", self._lacrosse_device.id)},
            model=self._lacrosse_device.sensor_type,
            manufacturer="LaCrosse",
            name=self._lacrosse_device.name.replace('_', ' ').title(),
        )

    @property
    def name(self):
        return f"{self._lacrosse_device.name.replace('_', ' ').title()} {self._field}"

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        if self._field.unit == "degrees_celsius":
            return TEMP_CELSIUS
        elif self._field.unit == "degrees_fahrenheit":
            return TEMP_FAHRENHEIT
        elif self._field.unit == "relative_humidity":
            return "%"
        else:
            return self._field.unit
