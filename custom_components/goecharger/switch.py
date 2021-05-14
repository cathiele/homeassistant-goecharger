"""Platform for go-eCharger switch integration."""
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_HOST
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant import core, config_entries

from goecharger import GoeCharger

from .const import DOMAIN, CONF_CHARGERS, CONF_NAME, CHARGER_API

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    _LOGGER.debug("setup sensors...")
    _LOGGER.debug(repr(config_entry.as_dict()))
    config = config_entry.as_dict()["data"]

    chargerName = config[CONF_NAME]
    host = config[CONF_HOST]
    chargerApi = GoeCharger(host)

    entities = []

    attribute = "allow_charging"
    entities.append(
        GoeChargerSwitch(
            hass.data[DOMAIN]["coordinator"],
            hass,
            chargerApi,
            f"switch.goecharger_{chargerName}_{attribute}",
            chargerName,
            "Charging allowed",
            attribute,
        )
    )

    async_add_entities(entities)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up go-eCharger Switch platform."""
    if discovery_info is None:
        return
    _LOGGER.debug("setup_platform")

    chargers = discovery_info[CONF_CHARGERS]
    chargerApi = discovery_info[CHARGER_API]

    entities = []

    for charger in chargers:
        chargerName = charger[0][CONF_NAME]

        attribute = "allow_charging"
        entities.append(
            GoeChargerSwitch(
                hass.data[DOMAIN]["coordinator"],
                hass,
                chargerApi[chargerName],
                f"switch.goecharger_{chargerName}_{attribute}",
                chargerName,
                "Charging allowed",
                attribute,
            )
        )
    async_add_entities(entities)


class GoeChargerSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, hass, goeCharger, entity_id, chargerName, name, attribute):
        """Initialize the go-eCharger sensor."""
        super().__init__(coordinator)
        self.entity_id = entity_id
        self._chargername = chargerName
        self._name = name
        self._attribute = attribute
        self.hass = hass
        self._goeCharger = goeCharger
        self._state = None

    @property
    def device_info(self):
        return {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self._chargername)
            },
            "name": self.name,
            "manufacturer": "go-e",
            "model": "HOME",
        }

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        await self.hass.async_add_executor_job(self._goeCharger.setAllowCharging, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self.hass.async_add_executor_job(self._goeCharger.setAllowCharging, False)
        await self.coordinator.async_request_refresh()

    @property
    def name(self):
        """Return the name of the switch."""
        return self._chargername

    @property
    def unique_id(self):
        """Return the unique_id of the switch."""
        return f"{self._chargername}_{self._attribute}"

    @property
    def is_on(self):
        """Return the state of the switch."""
        return True if self.coordinator.data[self._chargername][self._attribute] == "on" else False
