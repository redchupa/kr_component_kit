from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from ..const import DOMAIN, DONATION_MANUFACTURER, DONATION_MODEL, DONATION_SW_VERSION

def school_device(entry) -> DeviceInfo:
    """Device per school. Name = school name."""
    return DeviceInfo(
        identifiers={(DOMAIN, f"school_{entry.data['region_code']}_{entry.data['school_code']}")},
        name=entry.data.get("school_name", "학교"),
        manufacturer=DONATION_MANUFACTURER,
        model=DONATION_MODEL,
        sw_version=DONATION_SW_VERSION,
        entry_type=dr.DeviceEntryType.SERVICE,
    )
