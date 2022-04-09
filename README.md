# Home Assistant integration for the go-eCharger (WIP)

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![Validate with hassfest](https://github.com/cathiele/homeassistant-goecharger/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/cathiele/homeassistant-goecharger/actions/workflows/hassfest.yaml)

Integration for Homeassistant to view and Control the go-eCharger for electric Vehicles via the local ip-interface via API Version 1. In newer chargers the V1 API has to be enabled via the App first.

## Features
- attributes from charger available as sensors
- switch to turn off/on charger
- set charge limit in kWh (0.1 kWh steps)
- set max current for charging in ampere (6-32A)
- set absolute maximum current for charging (max can not be set higher than "absolute max")
- no cloud connection needed to control the charger - only local ip-access needed.
- correction factor for older devices which often present 5-10% lower voltage and therefore energy values

# Warning: WIP - Breaking changes possible
This is the first version of the Integration so there are still breaking changes possible.

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

* setup your Charger in the `configuration.yaml` (for always connected chargers):

```yaml
goecharger:
  chargers:
    - name: charger1
      host: <ip of your charger>
    - name: charger2
      host: <ip or hostname of charger 2>
      correction_factor: factor for correction for total and session charged 
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

**Important: Replace `111111` with your chargers name.**

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

**Important: Replace `111111` with your chargers name.**

```yaml
cards:
entities:
  - entity: switch.goecharger_111111_allow_charging
  - entity: input_number.goecharger_charge_limit
  - entity: input_select.goecharger_max_current
  - entity: sensor.goecharger_111111_car_status
  - entity: sensor.goecharger_111111_charger_temp
  - entity: sensor.goecharger_111111_current_session_charged_energy
  - entity: sensor.goecharger_111111_current_session_charged_energy_corrected
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
  - entity: sensor.goecharger_111111_energy_total_corrected
show_header_toggle: false
title: EV Charger (go-eCharger)
type: entities
```
