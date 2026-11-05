# Austroflamm Mo Duo – Home Assistant custom integration

This repository contains two separate integrations:

- `fumis`: the original Fumis integration, kept in its existing folder.
- `austroflamm_mo_duo`: a separate, read-only first development version for the Austroflamm Mo Duo.

The new integration uses its own Home Assistant domain (`austroflamm_mo_duo`). It does not overwrite or replace the existing `fumis` integration.

## Development status

**Early development / testing required.** The integration currently connects to the Fumis cloud API and exposes status values that are already understood from the existing Fumis implementation.

Included so far:

- Fumis cloud connection using the device MAC address and password/PIN
- Room and combustion-chamber temperature, where reported
- Current power value, fan RPM and pressure, where reported
- Fumis counters and fuel fields, kept without guessed units where the unit is not confirmed
- Operating-state binary sensor
- Sanitized Home Assistant diagnostics

Not implemented yet:

- Weekly schedules (weekday, Saturday and Sunday profiles)
- External room-temperature sensor selection
- Wood-mode power selection
- Manual fan control
- Reliable measured pellet consumption / service-menu extraction

**Safety:** No fan, combustion, auger or diagnostic parameter write commands are sent by this development integration. Do not use undocumented parameter IDs for testing. Control functions will only be added after the protocol and safe operating ranges have been verified.

## Provisional pellet estimate

The device owner supplied a pellet heating value of **4.9 kWh/kg** and the following nominal power levels:

| Level | Nominal power |
|---:|---:|
| 1 | 1.9 kW |
| 2 | 3.8 kW |
| 3 | 5.7 kW |
| 4 | 7.6 kW |
| 5 | 9.5 kW |

The integration contains a provisional calculation of `kW / 4.9` kg/h, but only when the API's current-power field reports a level from 1 to 5. This is an estimate, **not a measured fuel-consumption value**. It is valid as written only if the supplied kW figures represent fuel-input power. If they are useful heat output, the stove efficiency must also be included. The units and meaning of the API's `actualPower` field still need confirmation.

## Installation for development

1. In HACS, add this repository as a custom repository of category **Integration**.
2. Install the **Austroflamm Mo Duo** integration if HACS offers it.
3. Restart Home Assistant.
4. Open **Settings → Devices & services → Add integration**.
5. Search for **Austroflamm Mo Duo**.
6. Enter the Fumis MAC address and password/PIN.

If HACS does not detect the nested integration from this repository layout, install the folder `custom_components/austroflamm_mo_duo` manually into the matching directory in your Home Assistant configuration and restart.

## Diagnostics for further development

The integration provides a diagnostics download with the MAC address and password/PIN redacted. If you share diagnostics or API responses for protocol analysis, inspect the file first and remove any remaining personal or network information.

## Existing Fumis integration

The original `custom_components/fumis` folder remains present and is not replaced by this new integration.
