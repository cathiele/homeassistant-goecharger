import logging
from datetime import timedelta
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from .const import DOMAIN, CONF_NAME, CONF_CORRECTION_FACTOR
_LOGGER = logging.getLogger(__name__)


DEFAULT_UPDATE_INTERVAL = timedelta(seconds=20)
MIN_UPDATE_INTERVAL = timedelta(seconds=10)


class ConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for go-eCharger setup."""
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, info):
        if info is not None:
            _LOGGER.debug(info)
            return self.async_create_entry(title=info[CONF_NAME], data=info)

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_NAME): str,
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=20
                    ): int,
                    vol.Required(
                        CONF_CORRECTION_FACTOR, default="1.0"
                    ): str,
                }
            ),
        )

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for the go-eCharger"""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """"Initialize options flow"""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> config_entries.FlowResult:
        """Manage options for the goe-Charger component"""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Gets current values from config entry
        current_host = self.config_entry.options.get(CONF_HOST)
        current_scan_interval = self.config_entry.options.get(CONF_SCAN_INTERVAL)
        current_correction_factor = self.config_entry.options.get(CONF_CORRECTION_FACTOR)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=current_host): str,
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=current_scan_interval if current_scan_interval else 20 
                    ): int,
                    vol.Required(
                        CONF_CORRECTION_FACTOR, default=current_correction_factor if current_correction_factor else "1.0"
                    ): str,
                }
            )
        )