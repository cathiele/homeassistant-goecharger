"""go-eCharger integration"""
import voluptuous as vol
import ipaddress
import logging
from datetime import timedelta
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import valid_entity_id
from homeassistant.util.dt import utcnow

from goecharger import GoeCharger

_LOGGER = logging.getLogger(__name__)

DOMAIN = "goecharger"
ABSOLUTE_MAX_CURRENT = "charger_absolute_max_current"
SET_CABLE_LOCK_MODE_ATTR = "cable_lock_mode"
SET_ABSOLUTE_MAX_CURRENT_ATTR = "charger_absolute_max_current"
CHARGE_LIMIT = "charge_limit"
SET_MAX_CURRENT_ATTR = "max_current"

MIN_UPDATE_INTERVAL = timedelta(seconds=10)
DEFAULT_UPDATE_INTERVAL = timedelta(seconds=20)

CONF_SERIAL = "serial"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): vol.All(ipaddress.ip_address, cv.string),
                vol.Optional(CONF_SERIAL): vol.All(cv.string),
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                ): vol.All(cv.time_period, vol.Clamp(min=MIN_UPDATE_INTERVAL)),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass, config):
    """Set up go-eCharger platforms and services."""

    # interval = config[DOMAIN].get(CONF_SCAN_INTERVAL)
    host = config[DOMAIN][CONF_HOST]
    serial = config[DOMAIN].get(CONF_SERIAL, "unknown")
    goeCharger = GoeCharger(host)
    status = goeCharger.requestStatus()

    if status.get("serial_number") == "unknown":
        status["serial_number"] = serial

    hass.data[DOMAIN] = status
    hass.data[DOMAIN]["age"] = utcnow().timestamp()

    def handle_set_max_current(call):
        """Handle the service call to set the absolute max current."""
        maxCurrentInput = call.data.get(
            SET_MAX_CURRENT_ATTR, hass.data[DOMAIN][ABSOLUTE_MAX_CURRENT]
        )
        if isinstance(maxCurrentInput, str):
            if maxCurrentInput.isnumeric():
                maxCurrent = int(maxCurrentInput)
            elif valid_entity_id(maxCurrentInput):
                maxCurrent = int(hass.states.get(maxCurrentInput).state)
            else:
                _LOGGER.error(
                    "No valid value for '%s': %s", SET_MAX_CURRENT_ATTR, maxCurrent
                )
                return
        else:
            maxCurrent = maxCurrentInput

        if maxCurrent < 6:
            maxCurrent = 6
        if maxCurrent > 32:
            maxCurrent = 32
        hass.data[DOMAIN] = goeCharger.setMaxCurrent(maxCurrent)
        hass.data[DOMAIN]["age"] = utcnow().timestamp()

    def handle_set_absolute_max_current(call):
        """Handle the service call to set the absolute max current."""
        absoluteMaxCurrentInput = call.data.get(SET_ABSOLUTE_MAX_CURRENT_ATTR, 16)
        if isinstance(absoluteMaxCurrentInput, str):
            if absoluteMaxCurrentInput.isnumeric():
                absoluteMaxCurrent = int(absoluteMaxCurrentInput)
            elif valid_entity_id(absoluteMaxCurrentInput):
                absoluteMaxCurrent = int(hass.states.get(absoluteMaxCurrentInput).state)
            else:
                _LOGGER.error(
                    "No valid value for '%s': %s",
                    SET_ABSOLUTE_MAX_CURRENT_ATTR,
                    absoluteMaxCurrentInput,
                )
                return
        else:
            absoluteMaxCurrent = absoluteMaxCurrentInput

        if absoluteMaxCurrent < 6:
            absoluteMaxCurrent = 6
        if absoluteMaxCurrent > 32:
            absoluteMaxCurrent = 32
        hass.data[DOMAIN] = goeCharger.setAbsoluteMaxCurrent(absoluteMaxCurrent)
        hass.data[DOMAIN]["age"] = utcnow().timestamp()

    def handle_set_cable_lock_mode(call):
        """Handle the service call to set the absolute max current."""
        cableLockModeInput = call.data.get(SET_CABLE_LOCK_MODE_ATTR, 0)
        if isinstance(cableLockModeInput, str):
            if cableLockModeInput.isnumeric():
                cableLockMode = int(cableLockModeInput)
            elif valid_entity_id(cableLockModeInput):
                cableLockMode = int(hass.states.get(cableLockModeInput).state)
            else:
                _LOGGER.error(
                    "No valid value for '%s': %s",
                    SET_CABLE_LOCK_MODE_ATTR,
                    cableLockModeInput,
                )
                return
        else:
            cableLockMode = cableLockModeInput

        if cableLockModeInput < 0:
            cableLockMode = 0
        if cableLockMode > 2:
            cableLockMode = 2
        hass.data[DOMAIN] = goeCharger.setCableLockMode(cableLockMode)
        hass.data[DOMAIN]["age"] = utcnow().timestamp()

    def handle_set_charge_limit(call):
        """Handle the service call to set charge limit."""
        chargeLimitInput = call.data.get(CHARGE_LIMIT, 0.0)
        if isinstance(chargeLimitInput, str):
            if chargeLimitInput.isnumeric():
                chargeLimit = float(chargeLimitInput)
            elif valid_entity_id(chargeLimitInput):
                chargeLimit = float(hass.states.get(chargeLimitInput).state)
            else:
                _LOGGER.error(
                    "No valid value for '%s': %s", CHARGE_LIMIT, chargeLimitInput
                )
                return
        else:
            chargeLimit = chargeLimitInput

        if chargeLimit < 0:
            chargeLimit = 0
        hass.data[DOMAIN] = goeCharger.setChargeLimit(chargeLimit)
        hass.data[DOMAIN]["age"] = utcnow().timestamp()

    hass.services.register(DOMAIN, "set_max_current", handle_set_max_current)
    hass.services.register(
        DOMAIN, "set_absolute_max_current", handle_set_absolute_max_current
    )
    hass.services.register(DOMAIN, "set_cable_lock_mode", handle_set_cable_lock_mode)
    hass.services.register(DOMAIN, "set_charge_limit", handle_set_charge_limit)

    hass.helpers.discovery.load_platform("sensor", DOMAIN, {CONF_HOST: host}, config)
    hass.helpers.discovery.load_platform("switch", DOMAIN, {CONF_HOST: host}, config)

    return True
