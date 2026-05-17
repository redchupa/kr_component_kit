"""Seoul Bus device helpers."""
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from ..const import DOMAIN, DONATION_MANUFACTURER, DONATION_MODEL, DONATION_SW_VERSION


def seoul_bus_station_device(ars_id: str, station_name: str) -> DeviceInfo:
    """One device per Seoul Bus station (ARS-ID)."""
    return DeviceInfo(
        identifiers={(DOMAIN, f"seoul_bus_{ars_id}")},
        name=f"서울버스 - {station_name}",
        manufacturer=DONATION_MANUFACTURER,
        model=DONATION_MODEL,
        sw_version=DONATION_SW_VERSION,
        entry_type=DeviceEntryType.SERVICE,
    )
