import voluptuous as vol
import logging
import ipaddress
from datetime import timedelta
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_HOST, CONF_SCAN_INTERVAL)
from homeassistant.util.dt import utcnow

from goecharger import GoeCharger

DOMAIN='goecharger'

MIN_UPDATE_INTERVAL = timedelta(seconds=10)
DEFAULT_UPDATE_INTERVAL = timedelta(seconds=20)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(
            CONF_HOST
        ): vol.All(ipaddress.ip_address, cv.string),
        vol.Optional(
            CONF_SCAN_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): 
            vol.All(cv.time_period, vol.Clamp(min=MIN_UPDATE_INTERVAL))
    })
}, extra=vol.ALLOW_EXTRA)

def setup(hass, config):
    """Set up go-eCharger Sensor platform."""

    interval = config[DOMAIN].get(CONF_SCAN_INTERVAL)
    host = config[DOMAIN][CONF_HOST]
    goeCharger = GoeCharger(host)
    status = goeCharger.requestStatus()
    hass.data[DOMAIN] = status
    hass.data[DOMAIN]['age'] = utcnow().timestamp()

    hass.helpers.discovery.load_platform('sensor', DOMAIN, {CONF_HOST: host}, config)
    hass.helpers.discovery.load_platform('switch', DOMAIN, {CONF_HOST: host}, config)

    return True
