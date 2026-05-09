"""Weather device helpers."""
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from ..const import DOMAIN, DONATION_MANUFACTURER, DONATION_MODEL, DONATION_SW_VERSION
from . import AREA_CODES

def weather_device(area_code: str) -> DeviceInfo:
    name = AREA_CODES.get(area_code, area_code)
    return DeviceInfo(
        identifiers={(DOMAIN, f"weather_{area_code}")},
        name=f"기상특보 - {name}",
        manufacturer=DONATION_MANUFACTURER,
        model=DONATION_MODEL,
        sw_version=DONATION_SW_VERSION,
        entry_type=DeviceEntryType.SERVICE,
    )
