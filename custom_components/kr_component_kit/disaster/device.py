from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from ..const import DOMAIN, DONATION_MANUFACTURER, DONATION_MODEL, DONATION_SW_VERSION
def disaster_device(region=""):
    label = f"재난문자 - {region}" if region else "재난문자"
    did = f"disaster_{region}" if region else "disaster"
    return DeviceInfo(identifiers={(DOMAIN, did)}, name=label,
                      manufacturer=DONATION_MANUFACTURER,
                      model=DONATION_MODEL,
                      sw_version=DONATION_SW_VERSION,
                      entry_type=DeviceEntryType.SERVICE)
