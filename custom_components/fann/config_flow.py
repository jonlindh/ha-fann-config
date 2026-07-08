"""Config flow for FANN Config."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)
from homeassistant.exceptions import HomeAssistantError

from .api import FannApi
from .const import CONF_KEY, CONF_SERIAL, DOMAIN


class FannConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for FANN."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle user step."""

        errors = {}

        if user_input is not None:
            api = FannApi(
                serial=user_input[CONF_SERIAL],
                key=user_input[CONF_KEY],
            )

            try:
                devices = await api.get_devices()
                await api.disconnect()

                if not devices:
                    raise CannotConnect

            except Exception:
                await api.disconnect()
                errors["base"] = "cannot_connect"

            else:
                await self.async_set_unique_id(user_input[CONF_SERIAL])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="FANN Config",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SERIAL): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.TEXT)
                    ),
                    vol.Required(CONF_KEY): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    ),
                }
            ),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Unable to connect."""