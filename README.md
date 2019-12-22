# Home Assistant integration for the go-eCharger (WIP)

Integration for Homeassistant to view and Control the go-eCharger for electric Vehicles

## Features
- attributes from charger available as sensors
- switch to turn off/on charger

# Warning: WIP - Breaking changes possible
This is the first version of the Integration so there are still breaking chnages possible.


# Installation

- clone this repository
```
git clone https://github.com/cathiele/homeassistant-goecharger.git
```
- copy the content of the `custom_components`-Folder to the `custom_components` folder of your home-assistant installation

```
# mkdir -p <your-ha-config-dir>/custom_components
# cp -r custom_components/goecharger <your-ha-config-dir>/custom_components
```

* setup your Charger in the `configuration.yml`

```yml
goecharger:
  host: <ip of your charger>
```

# Sample View
![screenshot of Home Assistant](doc/ha_entity_view.png)

# Example Config

## `configuration.yaml`

```yaml
input_number:
  goecharger_charge_limit:
    name: Charge limit (kWh)
    min: 0
    max: 10
    step: 1

input_select:
  goecharger_max_current:
    name: Max current
    options:
      - 6
      - 10
      - 16
      - 20
      - 24
      - 32
```

## `automations.yaml`

**Important: Replace `111111` with your chargers serial number.**

```yaml
- id: '1576914483212'
  alias: 'goecharger: set max current on charger based on input select'
  description: ''
  trigger:
  - entity_id: input_select.goecharger_max_current
    platform: state
  condition: []
  action:
  - data_template:
      max_current: '{{ states(''input_select.goecharger_max_current'') }}'
    service: goecharger.set_max_current
- id: '1576915266692'
  alias: 'goecharger: set max_current input_select based on charger value'
  description: ''
  trigger:
  - entity_id: sensor.goecharger_111111_charger_max_current
    platform: state
  condition: []
  action:
  - data_template:
      entity_id: input_select.goecharger_max_current
      option: '{{ states.sensor.goecharger_111111_charger_max_current.state }}'
    service: input_select.select_option
- id: '1577036409850'
  alias: 'goecharger: set charge limit based on input'
  description: ''
  trigger:
  - entity_id: input_number.goecharger_charge_limit
    platform: state
  condition: []
  action:
  - data_template:
      charge_limit: '{{ states(''input_number.goecharger_charge_limit'') }}'
    service: goecharger.set_charge_limit
- id: '1577036687192'
  alias: 'goecharger: set charge_limit input based on charger'
  description: ''
  trigger:
  - entity_id: sensor.goecharger_111111_charge_limit
    platform: state
  condition: []
  action:
  - data_template:
      entity_id: input_number.goecharger_charge_limit
      value: '{{ states.sensor.goecharger_111111_charge_limit.state }}'
    service: input_number.set_value
```

## Lovcelace-UI Card Example

**Important: Replace `111111` with your chargers serial number.**

```yaml
cards:
entities:
  - entity: switch.goecharger_111111_allow_charging
  - entity: input_number.goecharger_charge_limit
  - entity: input_select.goecharger_max_current
  - entity: sensor.goecharger_111111_car_status
  - entity: sensor.goecharger_111111_charger_temp
  - entity: sensor.goecharger_111111_current_session_charged_energy
  - entity: sensor.goecharger_111111_p_all
  - entity: sensor.goecharger_111111_p_l1
  - entity: sensor.goecharger_111111_p_l2
  - entity: sensor.goecharger_111111_p_l3
  - entity: sensor.goecharger_111111_u_l1
  - entity: sensor.goecharger_111111_u_l2
  - entity: sensor.goecharger_111111_u_l3
  - entity: sensor.goecharger_111111_i_l1
  - entity: sensor.goecharger_111111_i_l2
  - entity: sensor.goecharger_111111_i_l3
  - entity: sensor.goecharger_111111_energy_total
show_header_toggle: false
title: EV Charger  (go-eCharger)
type: entities
```
