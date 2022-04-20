"""Platform for go-eCharger sensor integration."""
import logging
from homeassistant.const import (
    TEMP_CELSIUS,
    ENERGY_KILO_WATT_HOUR
)

from homeassistant import core, config_entries
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import (
    STATE_CLASS_TOTAL_INCREASING,
    DEVICE_CLASS_ENERGY,
    SensorEntity
)


from .const import CONF_CHARGERS, DOMAIN, CONF_NAME, CONF_CORRECTION_FACTOR

AMPERE = 'A'
VOLT = 'V'
POWER_KILO_WATT = 'kW'
CARD_ID = 'Card ID'
PERCENT = '%'

_LOGGER = logging.getLogger(__name__)

_sensorUnits = {
    'charger_temp': {'unit': TEMP_CELSIUS, 'name': 'Charger Temp'},
    'charger_temp0': {'unit': TEMP_CELSIUS, 'name': 'Charger Temp 0'},
    'charger_temp1': {'unit': TEMP_CELSIUS, 'name': 'Charger Temp 1'},
    'charger_temp2': {'unit': TEMP_CELSIUS, 'name': 'Charger Temp 2'},
    'charger_temp3': {'unit': TEMP_CELSIUS, 'name': 'Charger Temp 3'},
    'p_l1': {'unit': POWER_KILO_WATT, 'name': 'Power L1'},
    'p_l2': {'unit': POWER_KILO_WATT, 'name': 'Power L2'},
    'p_l3': {'unit': POWER_KILO_WATT, 'name': 'Power L3'},
    'p_n': {'unit': POWER_KILO_WATT, 'name': 'Power N'},
    'p_all': {'unit': POWER_KILO_WATT, 'name': 'Power All'},
    'current_session_charged_energy': {'unit': ENERGY_KILO_WATT_HOUR, 'name': 'Current Session charged'},
    'current_session_charged_energy_corrected': {'unit': ENERGY_KILO_WATT_HOUR, 'name': 'Current Session charged corrected'},
    'energy_total': {'unit': ENERGY_KILO_WATT_HOUR, 'name': 'Total Charged'},
    'energy_total_corrected': {'unit': ENERGY_KILO_WATT_HOUR, 'name': 'Total Charged corrected'},
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
    'lf_l1': {'unit': PERCENT, 'name': 'Power factor L1'},
    'lf_l2': {'unit': PERCENT, 'name': 'Power factor L2'},
    'lf_l3': {'unit': PERCENT, 'name': 'Power factor L3'},
    'lf_n': {'unit': PERCENT, 'name': 'Loadfactor N'},
    'car_status': {'unit': '', 'name': 'Status'}
}

_sensorStateClass = {
    'energy_total': STATE_CLASS_TOTAL_INCREASING,
    'energy_total_corrected': STATE_CLASS_TOTAL_INCREASING,
    'current_session_charged_energy': STATE_CLASS_TOTAL_INCREASING,
    'current_session_charged_energy_corrected': STATE_CLASS_TOTAL_INCREASING
}

_sensorDeviceClass = {
    'energy_total': DEVICE_CLASS_ENERGY,
    'energy_total_corrected': DEVICE_CLASS_ENERGY,
    'current_session_charged_energy': DEVICE_CLASS_ENERGY,
    'current_session_charged_energy_corrected': DEVICE_CLASS_ENERGY
}

_sensors = [
    'car_status',
    'charger_max_current',
    'charger_absolute_max_current',
    'charger_err',
    'charger_access',
    'stop_mode',
    'cable_lock_mode',
    'cable_max_current',
    'pre_contactor_l1',
    'pre_contactor_l2',
    'pre_contactor_l3',
    'post_contactor_l1',
    'post_contactor_l2',
    'post_contactor_l3',
    'charger_temp',
    'charger_temp0',
    'charger_temp1',
    'charger_temp2',
    'charger_temp3',
    'current_session_charged_energy',
    'current_session_charged_energy_corrected',
    'charge_limit',
    'adapter',
    'unlocked_by_card',
    'energy_total',
    'energy_total_corrected',
    'wifi',

    'u_l1',
    'u_l2',
    'u_l3',
    'u_n',
    'i_l1',
    'i_l2',
    'i_l3',
    'p_l1',
    'p_l2',
    'p_l3',
    'p_n',
    'p_all',
    'lf_l1',
    'lf_l2',
    'lf_l3',
    'lf_n',

    'firmware',
    'serial_number',
    'wifi_ssid',
    'wifi_enabled',
    'timezone_offset',
    'timezone_dst_offset',
]


def _create_sensors_for_charger(chargerName, hass, correctionFactor):
    entities = []

    for sensor in _sensors:

        _LOGGER.debug(f"adding Sensor: {sensor} for charger {chargerName}")
        sensorUnit = _sensorUnits.get(sensor).get('unit') if _sensorUnits.get(sensor) else ''
        sensorName = _sensorUnits.get(sensor).get('name') if _sensorUnits.get(sensor) else sensor
        sensorStateClass = _sensorStateClass[sensor] if sensor in _sensorStateClass else ''
        sensorDeviceClass = _sensorDeviceClass[sensor] if sensor in _sensorDeviceClass else ''
        entities.append(
            GoeChargerSensor(
                hass.data[DOMAIN]["coordinator"],
                f"sensor.goecharger_{chargerName}_{sensor}",
                chargerName, sensorName, sensor, sensorUnit, sensorStateClass, sensorDeviceClass, correctionFactor
            )
        )

    return entities


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    _LOGGER.debug("setup sensors...")
    config = config_entry.as_dict()["data"]

    chargerName = config[CONF_NAME]

    _LOGGER.debug(f"charger name: '{chargerName}'")
    _LOGGER.debug(f"config: '{config}'")
    async_add_entities(_create_sensors_for_charger(chargerName, hass, config[CONF_CORRECTION_FACTOR]))


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up go-eCharger Sensor platform."""
    _LOGGER.debug("setup_platform")
    if discovery_info is None:
        return

    chargers = discovery_info[CONF_CHARGERS]

    entities = []
    for charger in chargers:
        chargerName = charger[0][CONF_NAME]
        _LOGGER.debug(f"charger name: '{chargerName}'")
        _LOGGER.debug(f"charger[0]: '{charger[0]}'")
        
        entities.extend(_create_sensors_for_charger(chargerName, hass, charger[0][CONF_CORRECTION_FACTOR]))

    async_add_entities(entities)


class GoeChargerSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entity_id, chargerName, name, attribute, unit, stateClass, deviceClass, correctionFactor):
        """Initialize the go-eCharger sensor."""

        super().__init__(coordinator)
        self._chargername = chargerName
        self.entity_id = entity_id
        self._name = name
        self._attribute = attribute
        self._unit = unit
        self._attr_state_class = stateClass
        self._attr_device_class = deviceClass
        self.correctionFactor = correctionFactor


    @property
    def device_info(self):
        return {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self._chargername)
            },
            "name": self._chargername,
            "manufacturer": "go-e",
            "model": "HOME",
        }

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique_id of the sensor."""
        return f"{self._chargername}_{self._attribute}"

    @property
    def state(self):
        """Return the state of the sensor."""
        if (self._attribute == 'energy_total_corrected'):
            return self.coordinator.data[self._chargername]['energy_total'] * self.correctionFactor
        if (self._attribute == 'current_session_charged_energy_corrected'):
            return self.coordinator.data[self._chargername]['current_session_charged_energy'] * self.correctionFactor   
        return self.coordinator.data[self._chargername][self._attribute]

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit
