from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from ..const import DOMAIN, DONATION_MANUFACTURER, DONATION_MODEL, DONATION_SW_VERSION
from . import SIDO_CODES, FUEL_TYPES

def fuel_device(sido_code: str, fuel_code: str) -> DeviceInfo:
    area = SIDO_CODES.get(sido_code, sido_code)
    fuel = FUEL_TYPES.get(fuel_code, fuel_code)
    return DeviceInfo(identifiers={(DOMAIN, f"fuel_{sido_code}_{fuel_code}")},
                      name=f"유가정보 - {area} {fuel}",
                      manufacturer=DONATION_MANUFACTURER,
                      model=DONATION_MODEL,
                      sw_version=DONATION_SW_VERSION,
                      entry_type=DeviceEntryType.SERVICE)
