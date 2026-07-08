# FANN Config for Home Assistant

Custom Home Assistant integration for FANN Config devices.

## Supported devices

- EkoTreat
- Biobed Control Unit

## Features

- Wake / sleep control
- Status sensor
- Connected binary sensor
- People sensor for EkoTreat
- Schedule sensor for Biobed
- Automatic login and session handling
- Config flow setup through the Home Assistant UI

## Installation

Copy this folder:

```text
custom_components/fann
```

to your Home Assistant configuration folder:

```text
/config/custom_components/fann
```

Restart Home Assistant.

Then go to:

```text
Settings → Devices & services → Add integration → FANN Config
```

## Entities

Typical entities:

```text
switch.ekotreat
sensor.ekotreat_status
sensor.ekotreat_people
binary_sensor.ekotreat_connected

switch.biobed
sensor.biobed_status
sensor.biobed_schedule
binary_sensor.biobed_connected
```

## Notes

This integration uses the same web endpoints as `fannconfig.se`.