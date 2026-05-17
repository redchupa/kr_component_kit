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
ENTRY_SEOUL_BUS = "seoul_bus"
ENTRY_KAKAO_BUS = "kakao_bus"

# Donation info — surfaced via every device's manufacturer/model/sw_version
# fields so users browsing the device panel see a small support prompt.
# Original provider names live in each device's `name` so semantic info
# is preserved.
DONATION_MANUFACTURER = "우*만"
DONATION_MODEL = "토스 1000-1261-7813"
DONATION_SW_VERSION = "커피 한잔은 사랑입니다 ☕"

