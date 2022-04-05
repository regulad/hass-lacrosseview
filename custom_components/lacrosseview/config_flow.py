"""Config flow for LaCrosse View integration."""
from functools import partial

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from pylacrosseview import WeatherStation

from .const import DOMAIN


class LaCrosseViewConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]

            ws = WeatherStation()
            try:
                await self.hass.loop.run_in_executor(None, partial(ws.start, username, password))
            except RuntimeError:
                errors["base"] = "cannot_connect"
            else:
                # Abort in case the host was already configured before.
                await self.async_set_unique_id(username)
                self._abort_if_unique_id_configured()

                # Configuration data are available and no error was detected, create configuration entry.
                return self.async_create_entry(title=username, data={CONF_USERNAME: username, CONF_PASSWORD: password})

        # Show configuration form (default form in case of no user_input,
        # form filled with user_input and eventually with errors otherwise).
        return self._show_config_form(user_input, errors)

    def _show_config_form(self, user_input=None, errors=None):
        """Show the setup form to the user."""
        if user_input is None:
            user_input = {}

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )
