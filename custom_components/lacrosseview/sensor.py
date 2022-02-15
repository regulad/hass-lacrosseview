import logging
from functools import partial

import homeassistant.helpers.config_validation as cv
import voluptuous
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_USERNAME, CONF_PASSWORD
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import LaCrosseViewSensor, DOMAIN

REQUIREMENTS = ['pylacrosseview==0.1.2']

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    voluptuous.Required(CONF_USERNAME): cv.string,
    voluptuous.Required(CONF_PASSWORD): cv.string,
})


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    entities = []
    ws = hass.data[DOMAIN][config_entry.unique_id]
    for device in ws.devices:
        states = await hass.loop.run_in_executor(None, partial(device.states))
        for field in states.keys():
            entities.append(LaCrosseViewSensor(device, field))
    async_add_entities(entities)
