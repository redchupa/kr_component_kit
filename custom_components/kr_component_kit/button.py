"""Button platform dispatcher."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import *


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback) -> None:
    etype = entry.data.get(CONF_ENTRY_TYPE)
    store = hass.data[DOMAIN][entry.entry_id]
    entities = []

    if etype == ENTRY_SEOUL_BUS:
        from .seoul_bus.button import SeoulBusRefreshButton
        from .seoul_bus.device import seoul_bus_station_device
        for st in store.get("stations", []):
            coord = store["coordinators"].get(st["ars_id"])
            if not coord:
                continue
            di = seoul_bus_station_device(st["ars_id"], st.get("station_name") or st["ars_id"])
            entities.append(SeoulBusRefreshButton(coord, di))

    elif etype == ENTRY_KAKAO_BUS:
        from .kakao_bus.button import KakaoBusRefreshButton
        from .kakao_bus.device import kakao_bus_station_device
        for stop in store.get("stops", []):
            coord = store["coordinators"].get(stop["stop_id"])
            if not coord:
                continue
            di = kakao_bus_station_device(stop["stop_id"], stop.get("stop_name") or stop["stop_id"])
            entities.append(KakaoBusRefreshButton(coord, di))

    if entities:
        async_add_entities(entities)
