"""Korea Bus device helpers."""
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from ..const import DOMAIN, DONATION_MANUFACTURER, DONATION_MODEL, DONATION_SW_VERSION


def korea_bus_station_device(stop_id: str, stop_name: str) -> DeviceInfo:
    """One device per Korea Bus stop."""
    return DeviceInfo(
        identifiers={(DOMAIN, f"korea_bus_{stop_id}")},
        name=f"한국 버스 - {stop_name}",
        manufacturer=DONATION_MANUFACTURER,
        model=DONATION_MODEL,
        sw_version=DONATION_SW_VERSION,
        entry_type=DeviceEntryType.SERVICE,
    )
