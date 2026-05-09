"""KEPCO device."""
from __future__ import annotations
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from ..const import DOMAIN, DONATION_MANUFACTURER, DONATION_MODEL, DONATION_SW_VERSION

def kepco_device_info(username: str) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, f"kepco_{username}")},
        name=f"한전 ({username})",
        manufacturer=DONATION_MANUFACTURER,
        model=DONATION_MODEL,
        sw_version=DONATION_SW_VERSION,
        entry_type=DeviceEntryType.SERVICE,
    )
