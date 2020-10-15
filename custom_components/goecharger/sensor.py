"""Platform for go-eCharger sensor integration."""
import logging
from homeassistant.util.dt import utcnow
from homeassistant.const import (TEMP_CELSIUS, ENERGY_KILO_WATT_HOUR)
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_HOST

from goecharger import GoeCharger

from . import DOMAIN

AMPERE = 'A'
VOLT = 'V'
POWER_KILO_WATT = 'kW'
CARD_ID = 'Card ID'
PERCENT = '%'

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up go-eCharger Sensor platform."""

    if discovery_info is None:
        return

    serial = hass.data[DOMAIN]['serial_number']

    goeCharger = GoeCharger(discovery_info[CONF_HOST])

    entities = []

    sensorUnits = {
        'charger_temp': {'unit': TEMP_CELSIUS, 'name': 'Charger Temp'},
        'p_l1': {'unit': POWER_KILO_WATT, 'name': 'Power L1'},
        'p_l2': {'unit': POWER_KILO_WATT, 'name': 'Power L2'},
        'p_l3': {'unit': POWER_KILO_WATT, 'name': 'Power L3'},
        'p_n': {'unit': POWER_KILO_WATT, 'name': 'Power N'},
        'p_all': {'unit': POWER_KILO_WATT, 'name': 'Power All'},
        'current_session_charged_energy': {'unit': ENERGY_KILO_WATT_HOUR, 'name': 'Current Session charged'},
        'energy_total': {'unit': ENERGY_KILO_WATT_HOUR, 'name': 'Total Charged'},
        'charge_limit': {'unit': ENERGY_KILO_WATT_HOUR, 'name': 'Charge limit'},
        'u_l1': {'unit': VOLT, 'name': 'Voltage L1'},
        'u_l2': {'unit': VOLT, 'name': 'Voltage L2'},
        'u_l3': {'unit': VOLT, 'name': 'Voltage L3'},
        'u_n': {'unit': VOLT, 'name': 'Voltage N'},
        'i_l1': {'unit': AMPERE, 'name': 'Current L1'},
        'i_l2': {'unit': AMPERE, 'name': 'Current L2'},
        'i_l3': {'unit': AMPERE, 'name': 'Current L3'},
        'charger_max_current': {'unit': AMPERE, 'name': 'Charger max current setting'},
        'charger_absolute_max_current': {'unit': AMPERE, 'name': 'Charger absolute max current setting'},
        'cable_lock_mode': {'unit': '', 'name': 'Cable lock mode'},
        'cable_max_current': {'unit': AMPERE, 'name': 'Cable max current'},
        'unlocked_by_card': {'unit': CARD_ID, 'name': 'Card used'},
        'lf_l1': {'unit': PERCENT, 'name': 'Loadfactor L1'},
        'lf_l2': {'unit': PERCENT, 'name': 'Loadfactor L2'},
        'lf_l3': {'unit': PERCENT, 'name': 'Loadfactor L3'},
        'lf_n': {'unit': PERCENT, 'name': 'Loadfactor N'},
        'car_status': {'unit': '', 'name': 'Status'}
    }

    for sensor in hass.data[DOMAIN]:
        if sensor not in ('allow_charging', 'age'):
            _LOGGER.debug('adding Sensor: %s' % sensor)
            sensorUnit = sensorUnits.get(sensor).get('unit') if sensorUnits.get(sensor) else ''
            sensorName = sensorUnits.get(sensor).get('name') if sensorUnits.get(sensor) else sensor
            entities.append(
                GoeChargerSensor(
                    hass, goeCharger, f"sensor.goecharger_{serial}_{sensor}", sensorName, sensor, sensorUnit
                )
            )

    add_entities(entities)


class GoeChargerSensor(Entity):
    def __init__(self, hass, goeCharger, entity_id, name, attribute, unit):
        """Initialize the go-eCharger sensor."""
        self._entity_id = entity_id
        self._name = name
        self._attribute = attribute
        self._unit = unit
        self.hass = hass
        self._goeCharger = goeCharger
        self._state = None

    @property
    def entity_id(self):
        """Return the entity_id of the sensor."""
        return self._entity_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        if self.hass.data[DOMAIN]['age'] + 1 < utcnow().timestamp():
            _LOGGER.debug('Updating status...')
            fetchedStatus = self._goeCharger.requestStatus()
            if fetchedStatus.get("car", "unknown") != "unknown" or not "car" in self.hass.data[DOMAIN]:
                self.hass.data[DOMAIN] = fetchedStatus
                self.hass.data[DOMAIN]['age'] = utcnow().timestamp()

        self._state = self.hass.data[DOMAIN][self._attribute]
