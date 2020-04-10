"""Platform for go-eCharger switch integration."""
import logging
from homeassistant.util.dt import utcnow
from homeassistant.components.switch import SwitchDevice
from homeassistant.const import CONF_HOST

from goecharger import GoeCharger

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up go-eCharger Switch platform."""
    if discovery_info is None:
        return

    serial = hass.data[DOMAIN]['serial_number']

    goeCharger = GoeCharger(discovery_info[CONF_HOST])

    attribute = 'allow_charging'
    add_entities(
        [
            GoeChargerSwitch(hass, goeCharger, f'switch.goecharger_{serial}_{attribute}', 'Charging allowed', attribute)
        ]
    )


class GoeChargerSwitch(SwitchDevice):
    def __init__(self, hass, goeCharger, entity_id, name, attribute):
        """Initialize the go-eCharger sensor."""
        self._entity_id = entity_id
        self._name = name
        self._attribute = attribute
        self.hass = hass
        self._goeCharger = goeCharger
        self._state = None

    def turn_on(self, **kwargs):
        """Turn the entity on."""
        self._goeCharger.setAllowCharging(True)

    def turn_off(self, **kwargs):
        """Turn the entity off."""
        self._goeCharger.setAllowCharging(False)

    @property
    def entity_id(self):
        """Return the entity_id of the switch."""
        return self._entity_id

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return the state of the switch."""
        return self._state

    def update(self):
        """Fetch new state data for the switch.
        This is the only method that should fetch new data for Home Assistant.
        """
        if self.hass.data[DOMAIN]['age'] + 1 < utcnow().timestamp():
            _LOGGER.debug('Updating status...')
            self.hass.data[DOMAIN] = self._goeCharger.requestStatus()
            self.hass.data[DOMAIN]['age'] = utcnow().timestamp()

        self._state = True if self.hass.data[DOMAIN][self._attribute] == 'on' else False
