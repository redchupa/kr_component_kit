"""Binary sensor platform dispatcher."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import *

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback) -> None:
    etype = entry.data.get(CONF_ENTRY_TYPE)
    store = hass.data[DOMAIN][entry.entry_id]
    entities = []

    if etype == ENTRY_WEATHER:
        from .weather.sensor import WeatherWarningBinarySensor
        c = store["coordinator"]
        for ac in store.get("area_codes", []):
            entities.append(WeatherWarningBinarySensor(c, ac))

    elif etype == ENTRY_SAFETY_ALERT:
        from .safety_alert.sensor import SafetyAlertBinarySensor
        for region in store.get("regions", []):
            coord = store["coordinators"].get(region["code"])
            if coord:
                entities.append(SafetyAlertBinarySensor(coord, region["code"], region["name"]))

    elif etype == ENTRY_AIRKOREA:
        from .airkorea.sensor import AirAlertBinarySensor
        c = store["coordinator"]
        sido = entry.data.get("sido", "")
        for st in store.get("stations", []):
            entities.append(AirAlertBinarySensor(c, st["stationName"], sido))

    elif etype == ENTRY_SEOUL_BUS:
        from .seoul_bus.binary_sensor import (
            SeoulBusFullSensor, SeoulBusLowFloorSensor)
        from .seoul_bus.device import seoul_bus_station_device
        for st in store.get("stations", []):
            coord = store["coordinators"].get(st["ars_id"])
            if not coord:
                continue
            di = seoul_bus_station_device(
                st["ars_id"], st.get("station_name") or st["ars_id"])
            routes = st.get("routes") or list((coord.data or {}).keys())
            for rt in routes:
                entities.append(SeoulBusLowFloorSensor(coord, rt, di))
                entities.append(SeoulBusFullSensor(coord, rt, di))

    if entities:
        async_add_entities(entities)
