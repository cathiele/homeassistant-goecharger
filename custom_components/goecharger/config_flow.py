from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
import homeassistant.helpers.config_validation as cv
import ipaddress
from datetime import timedelta
from goecharger import GoeCharger
import logging
_LOGGER = logging.getLogger(__name__)

from .const import DOMAIN, CONF_NAME

import voluptuous as vol


DEFAULT_UPDATE_INTERVAL = timedelta(seconds=20)
MIN_UPDATE_INTERVAL = timedelta(seconds=10)



class ConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for go-eCharger setup."""
    VERSION = 1

    @staticmethod
    @callback
    async def async_get_options_flow(config_entry):
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
                    ): int
            	}
	        ),	
        )
