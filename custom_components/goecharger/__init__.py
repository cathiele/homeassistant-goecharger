import voluptuous as vol
import logging
import ipaddress
from datetime import timedelta
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_HOST, CONF_SCAN_INTERVAL)
from homeassistant.util.dt import utcnow

from goecharger import GoeCharger

DOMAIN='goecharger'
ABSOLUTE_MAX_CURRENT='charger_absolute_max_current'
SET_ABSOLUTE_MAX_CURRENT_ATTR='absolute_max_current'
CHARGE_LIMIT='charge_limit'
SET_MAX_CURRENT_ATTR='max_current'

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
    """Set up go-eCharger platforms and services."""

    interval = config[DOMAIN].get(CONF_SCAN_INTERVAL)
    host = config[DOMAIN][CONF_HOST]
    goeCharger = GoeCharger(host)
    status = goeCharger.requestStatus()
    hass.data[DOMAIN] = status
    hass.data[DOMAIN]['age'] = utcnow().timestamp()

    def handle_set_max_current(call):
        """Handle the service call."""
        maxCurrent = call.data.get(SET_MAX_CURRENT_ATTR, hass.data[DOMAIN][ABSOLUTE_MAX_CURRENT])
        if isinstance(maxCurrent, str):
            maxCurrent = int(maxCurrent)

        if maxCurrent < 6:
            maxCurrent = 6
        if maxCurrent > 32:
            maxCurrent = 32
        hass.data[DOMAIN] = goeCharger.setMaxCurrent(maxCurrent)
        hass.data[DOMAIN]['age'] = utcnow().timestamp()

    def handle_set_absolute_max_current(call):
        """Handle the service call."""
        absoluteMaxCurrent = call.data.get(SET_ABSOLUTE_MAX_CURRENT_ATTR, 16)
        if isinstance(absoluteMaxCurrent, str):
            absoluteMaxCurrent = int(absoluteMaxCurrent)

        if absoluteMaxCurrent < 6:
            absoluteMaxCurrent = 6
        if absoluteMaxCurrent > 32:
            absoluteMaxCurrent = 32
        hass.data[DOMAIN] = goeCharger.setAbsoluteMaxCurrent(absoluteMaxCurrent)
        hass.data[DOMAIN]['age'] = utcnow().timestamp()

    def handle_set_charge_limit(call):
        """Handle the service call."""
        chargeLimit = call.data.get(CHARGE_LIMIT, 0.0)
        if isinstance(chargeLimit, str):
            chargeLimit = float(chargeLimit)

        if chargeLimit < 0:
            chargeLimit = 0
        hass.data[DOMAIN] = goeCharger.setChargeLimit(chargeLimit)
        hass.data[DOMAIN]['age'] = utcnow().timestamp()

    hass.services.register(DOMAIN, 'set_max_current', handle_set_max_current)
    hass.services.register(DOMAIN, 'set_absolute_max_current', handle_set_absolute_max_current)
    hass.services.register(DOMAIN, 'set_charge_limit', handle_set_charge_limit)

    hass.helpers.discovery.load_platform('sensor', DOMAIN, {CONF_HOST: host}, config)
    hass.helpers.discovery.load_platform('switch', DOMAIN, {CONF_HOST: host}, config)

    return True
