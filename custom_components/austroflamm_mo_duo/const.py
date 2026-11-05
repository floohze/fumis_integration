"""Constants for the Austroflamm Mo Duo integration."""
from datetime import timedelta

DOMAIN = "austroflamm_mo_duo"
MANUFACTURER = "Austroflamm"
MODEL = "Mo Duo"
API_URL = "https://api.fumis.si/v1/status"
UPDATE_INTERVAL = timedelta(seconds=30)

CONF_NAME = "name"
CONF_MAC = "mac"
CONF_PASSWORD = "password"

# Nominal values supplied by the device owner. Whether these are fuel-input
# or useful-output ratings still needs confirmation before consumption is
# presented as a measured value.
PELLET_HEATING_VALUE_KWH_KG = 4.9
POWER_LEVELS_KW = {
    1: 1.9,
    2: 3.8,
    3: 5.7,
    4: 7.6,
    5: 9.5,
}

def estimated_pellet_rate_kg_h(level: int) -> float | None:
    """Return a provisional kg/h estimate for a nominal power level."""
    power = POWER_LEVELS_KW.get(level)
    if power is None:
        return None
    return round(power / PELLET_HEATING_VALUE_KWH_KG, 3)
