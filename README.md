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

# Sample UI-Config

Important: Replace `111111` with your chargers serial number.

```yaml
cards:
  - entities:
      - entity: switch.goecharger_111111_allow_charging
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
