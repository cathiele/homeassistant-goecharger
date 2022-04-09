"""go-eCharger integration"""
import voluptuous as vol
import ipaddress
import logging
from datetime import timedelta
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import valid_entity_id
from homeassistant import core
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, CONF_SERIAL, CONF_CHARGERS, CONF_CORRECTION_FACTOR, CONF_NAME, CHARGER_API
from goecharger import GoeCharger

_LOGGER = logging.getLogger(__name__)

ABSOLUTE_MAX_CURRENT = "charger_absolute_max_current"
SET_CABLE_LOCK_MODE_ATTR = "cable_lock_mode"
SET_ABSOLUTE_MAX_CURRENT_ATTR = "charger_absolute_max_current"
CHARGE_LIMIT = "charge_limit"
SET_MAX_CURRENT_ATTR = "max_current"
CHARGER_NAME_ATTR = "charger_name"

MIN_UPDATE_INTERVAL = timedelta(seconds=10)
DEFAULT_UPDATE_INTERVAL = timedelta(seconds=20)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_CHARGERS, default=[]): vol.All([
                    cv.ensure_list, [
                        vol.All({
                            vol.Required(CONF_NAME): vol.All(cv.string),
                            vol.Required(CONF_HOST): vol.All(ipaddress.ip_address, cv.string),
                            vol.Optional(
                                CONF_CORRECTION_FACTOR, default=1
                            ): vol.All(cv.positive_float),
                        })
                    ]
                ]),
                vol.Optional(CONF_HOST): vol.All(ipaddress.ip_address, cv.string),
                vol.Optional(CONF_SERIAL): vol.All(cv.string),
                vol.Optional(
                    CONF_CORRECTION_FACTOR, default=1
                ): vol.All(cv.float),
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                ): vol.All(cv.time_period, vol.Clamp(min=MIN_UPDATE_INTERVAL)),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup_entry(hass, config):
    _LOGGER.debug("async_Setup_entry")
    _LOGGER.debug(repr(config.data))

    name = config.data[CONF_NAME]
    charger = GoeCharger(config.data[CONF_HOST])
    hass.data[DOMAIN]["api"][name] = charger

    await hass.data[DOMAIN]["coordinator"].async_refresh()

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config, "sensor")
    )
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config, "switch")
    )
    return True


async def async_unload_entry(hass, entry):
    _LOGGER.debug(f"Unloading charger '{entry.data[CONF_NAME]}")
    hass.data[DOMAIN]["api"].pop(entry.data[CONF_NAME])
    return True


class ChargerStateFetcher:
    def __init__(self, hass):
        self._hass = hass

    async def fetch_states(self):
        _LOGGER.debug('Updating status...')
        goeChargers = self._hass.data[DOMAIN]["api"]
        data = self.coordinator.data if self.coordinator.data else {}
        for chargerName in goeChargers.keys():
            _LOGGER.debug(f"update for '{chargerName}'..")
            fetchedStatus = await self._hass.async_add_executor_job(goeChargers[chargerName].requestStatus)
            if fetchedStatus.get("car_status", "unknown") != "unknown":
                data[chargerName] = fetchedStatus
                _LOGGER.debug(f"Got raw state: '{data[chargerName]}'")
                data[chargerName]["current_session_charged_energy_corrected"] = fetchedStatus.get("current_session_charged_energy") * CONF_CORRECTION_FACTOR
                data[chargerName]["energy_total_corrected"] = fetchedStatus.get("energy_total") * CONF_CORRECTION_FACTOR
                _LOGGER.debug(f"Got corrected state: '{data[chargerName]}'")
            else:
                _LOGGER.error(f"Unable to fetch state for Charger {chargerName}")
        return data


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up go-eCharger platforms and services."""

    _LOGGER.debug("async_setup")
    scan_interval = DEFAULT_UPDATE_INTERVAL

    hass.data[DOMAIN] = {}
    chargerApi = {}
    chargers = []
    if DOMAIN in config:
        scan_interval = config[DOMAIN].get(CONF_SCAN_INTERVAL, DEFAULT_UPDATE_INTERVAL)

        host = config[DOMAIN].get(CONF_HOST, False)
        serial = config[DOMAIN].get(CONF_SERIAL, "unknown")

        chargers = config[DOMAIN].get(CONF_CHARGERS, [])

        if host:
            if not serial:
                goeCharger = GoeCharger(host)
                status = goeCharger.requestStatus()
                serial = status["serial_number"]
            chargers.append([{CONF_NAME: serial, CONF_HOST: host}])
        _LOGGER.debug(repr(chargers))

        for charger in chargers:
            chargerName = charger[0][CONF_NAME]
            host = charger[0][CONF_HOST]
            _LOGGER.debug(f"charger: '{chargerName}' host: '{host}' ")

            goeCharger = GoeCharger(host)
            chargerApi[chargerName] = goeCharger

    hass.data[DOMAIN]["api"] = chargerApi

    chargeStateFecher = ChargerStateFetcher(hass)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=chargeStateFecher.fetch_states,
        update_interval=scan_interval,
    )
    chargeStateFecher.coordinator = coordinator

    hass.data[DOMAIN]["coordinator"] = coordinator

    await coordinator.async_refresh()

    async def async_handle_set_max_current(call):
        """Handle the service call to set the absolute max current."""
        chargerNameInput = call.data.get(CHARGER_NAME_ATTR, '')

        maxCurrentInput = call.data.get(
            SET_MAX_CURRENT_ATTR, 32  # TODO: dynamic based on chargers absolute_max-setting
        )
        maxCurrent = 0
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

        if len(chargerNameInput) > 0:
            _LOGGER.debug(f"set max_current for charger '{chargerNameInput}' to {maxCurrent}")
            try:
                await hass.async_add_executor_job(hass.data[DOMAIN]["api"][chargerNameInput].setTmpMaxCurrent, maxCurrent)
            except KeyError:
                _LOGGER.error(f"Charger with name '{chargerName}' not found!")

        else:
            for charger in hass.data[DOMAIN]["api"].keys():
                try:
                    _LOGGER.debug(f"set max_current for charger '{charger}' to {maxCurrent}")
                    await hass.async_add_executor_job(hass.data[DOMAIN]["api"][charger].setTmpMaxCurrent, maxCurrent)
                except KeyError:
                    _LOGGER.error(f"Charger with name '{chargerName}' not found!")

        await hass.data[DOMAIN]["coordinator"].async_refresh()

    async def async_handle_set_absolute_max_current(call):
        """Handle the service call to set the absolute max current."""
        chargerNameInput = call.data.get(CHARGER_NAME_ATTR, '')
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

        if len(chargerNameInput) > 0:
            _LOGGER.debug(f"set absolute_max_current for charger '{chargerNameInput}' to {absoluteMaxCurrent}")
            try:
                await hass.async_add_executor_job(
                    hass.data[DOMAIN]["api"][chargerNameInput].setAbsoluteMaxCurrent, absoluteMaxCurrent
                )
            except KeyError:
                _LOGGER.error(f"Charger with name '{chargerName}' not found!")

        else:
            for charger in hass.data[DOMAIN]["api"].keys():
                try:
                    _LOGGER.debug(f"set absolute_max_current for charger '{charger}' to {absoluteMaxCurrent}")
                    await hass.async_add_executor_job(
                        hass.data[DOMAIN]["api"][charger].setAbsoluteMaxCurrent, absoluteMaxCurrent
                    )
                except KeyError:
                    _LOGGER.error(f"Charger with name '{chargerName}' not found!")

        await hass.data[DOMAIN]["coordinator"].async_refresh()

    async def async_handle_set_cable_lock_mode(call):
        """Handle the service call to set the absolute max current."""
        chargerNameInput = call.data.get(CHARGER_NAME_ATTR, '')
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

        cableLockModeEnum = GoeCharger.CableLockMode.UNLOCKCARFIRST
        if cableLockModeInput == 1:
            cableLockModeEnum = GoeCharger.CableLockMode.AUTOMATIC
        if cableLockMode >= 2:
            cableLockModeEnum = GoeCharger.CableLockMode.LOCKED

        if len(chargerNameInput) > 0:
            _LOGGER.debug(f"set set_cable_lock_mode for charger '{chargerNameInput}' to {cableLockModeEnum}")
            try:
                await hass.async_add_executor_job(
                    hass.data[DOMAIN]["api"][chargerNameInput].setCableLockMode, cableLockModeEnum
                )
            except KeyError:
                _LOGGER.error(f"Charger with name '{chargerName}' not found!")

        else:
            for charger in hass.data[DOMAIN]["api"].keys():
                try:
                    _LOGGER.debug(f"set set_cable_lock_mode for charger '{charger}' to {cableLockModeEnum}")
                    await hass.async_add_executor_job(hass.data[DOMAIN]["api"][charger].setCableLockMode, cableLockModeEnum)
                except KeyError:
                    _LOGGER.error(f"Charger with name '{chargerName}' not found!")

        await hass.data[DOMAIN]["coordinator"].async_refresh()

    async def async_handle_set_charge_limit(call):
        """Handle the service call to set charge limit."""
        chargerNameInput = call.data.get(CHARGER_NAME_ATTR, '')
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

        if len(chargerNameInput) > 0:
            _LOGGER.debug(f"set set_charge_limit for charger '{chargerNameInput}' to {chargeLimit}")
            try:
                await hass.async_add_executor_job(hass.data[DOMAIN]["api"][chargerNameInput].setChargeLimit, chargeLimit)
            except KeyError:
                _LOGGER.error(f"Charger with name '{chargerName}' not found!")

        else:
            for charger in hass.data[DOMAIN]["api"].keys():
                try:
                    _LOGGER.debug(f"set set_charge_limit for charger '{charger}' to {chargeLimit}")
                    await hass.async_add_executor_job(hass.data[DOMAIN]["api"][charger].setChargeLimit, chargeLimit)
                except KeyError:
                    _LOGGER.error(f"Charger with name '{chargerName}' not found!")

        await hass.data[DOMAIN]["coordinator"].async_refresh()

    hass.services.async_register(DOMAIN, "set_max_current", async_handle_set_max_current)
    hass.services.async_register(
        DOMAIN, "set_absolute_max_current", async_handle_set_absolute_max_current
    )
    hass.services.async_register(DOMAIN, "set_cable_lock_mode", async_handle_set_cable_lock_mode)
    hass.services.async_register(DOMAIN, "set_charge_limit", async_handle_set_charge_limit)

    hass.async_create_task(async_load_platform(
        hass, "sensor", DOMAIN, {CONF_CHARGERS: chargers, CHARGER_API: chargerApi}, config)
    )
    hass.async_create_task(async_load_platform(
        hass, "switch", DOMAIN, {CONF_CHARGERS: chargers, CHARGER_API: chargerApi}, config)
    )

    return True
