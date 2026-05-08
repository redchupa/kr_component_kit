"""Constants for 한국 컴포넌트 키트 integration."""
import logging
from zoneinfo import ZoneInfo

DOMAIN = "kr_component_kit"
CONF_ENTRY_TYPE = "entry_type"

LOGGER = logging.getLogger(__package__)
TZ_ASIA_SEOUL = ZoneInfo("Asia/Seoul")

ENTRY_WEATHER = "weather_warning"
ENTRY_TRANSIT = "transit"
ENTRY_FUEL = "fuel"
ENTRY_SCHOOL = "school"
ENTRY_DISASTER = "disaster"
ENTRY_SAFETY_ALERT = "safety_alert"
ENTRY_KEPCO = "kepco"
ENTRY_GASAPP = "gasapp"
ENTRY_ARISU = "arisu"
ENTRY_PHARMACY = "pharmacy"
ENTRY_AIRKOREA = "airkorea"
ENTRY_KMA_WEATHER = "kma_weather"
ENTRY_EARTHQUAKE = "earthquake"
