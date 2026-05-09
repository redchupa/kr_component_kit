"""Transit device helpers."""
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from ..const import DOMAIN, DONATION_MANUFACTURER, DONATION_MODEL, DONATION_SW_VERSION
from . import SUBWAY_LINES


def subway_device(station, direction, line_id=""):
    ln = SUBWAY_LINES.get(line_id, "")
    label = f"지하철 - {station}역 {ln} {direction}".strip()
    did = f"subway_{station}_{direction}_{line_id}"
    return DeviceInfo(identifiers={(DOMAIN, did)}, name=label,
                      manufacturer=DONATION_MANUFACTURER,
                      model=DONATION_MODEL,
                      sw_version=DONATION_SW_VERSION,
                      entry_type=DeviceEntryType.SERVICE)


def bus_stop_device(stop_id, stop_name):
    """One device per bus stop."""
    return DeviceInfo(
        identifiers={(DOMAIN, f"bus_{stop_id}")},
        name=f"버스 - {stop_name}",
        manufacturer=DONATION_MANUFACTURER,
        model=DONATION_MODEL,
        sw_version=DONATION_SW_VERSION,
        entry_type=DeviceEntryType.SERVICE,
    )
