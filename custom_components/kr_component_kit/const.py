from logging import getLogger

import pytz
from homeassistant.const import Platform

DOMAIN = "kr_component_kit"
LOGGER = getLogger(__package__)

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]

CURRENCY_KRW = "KRW"
ENERGY_KILO_WATT_HOUR = "kWh"
TZ_ASIA_SEOUL = pytz.timezone("Asia/Seoul")
