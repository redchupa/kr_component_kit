"""한국 컴포넌트 키트 - unified Korean public data integration."""
from __future__ import annotations
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from .const import *
from .llm_api import async_cleanup_llm_api, async_setup_llm_api

PLATFORM_MAP = {
    ENTRY_WEATHER: [Platform.EVENT, Platform.CALENDAR, Platform.BINARY_SENSOR],
    ENTRY_TRANSIT: [Platform.SENSOR],
    ENTRY_FUEL: [Platform.SENSOR],
    ENTRY_SCHOOL: [Platform.SENSOR, Platform.CALENDAR],
    ENTRY_DISASTER: [Platform.SENSOR, Platform.EVENT],
    ENTRY_SAFETY_ALERT: [Platform.BINARY_SENSOR, Platform.SENSOR, Platform.EVENT],
    ENTRY_KEPCO: [Platform.SENSOR],
    ENTRY_GASAPP: [Platform.SENSOR],
    ENTRY_ARISU: [Platform.SENSOR],
    ENTRY_PHARMACY: [Platform.SENSOR],
    ENTRY_AIRKOREA: [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.EVENT, Platform.CALENDAR],
    ENTRY_KMA_WEATHER: [Platform.WEATHER],
    ENTRY_EARTHQUAKE: [Platform.EVENT],
    ENTRY_SEOUL_BUS: [Platform.SENSOR, Platform.BUTTON, Platform.SWITCH],
    ENTRY_KOREA_BUS: [Platform.SENSOR, Platform.BUTTON, Platform.SWITCH],
}

async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate older config entries forward.

    v1 -> v2  (kr_component_kit 4.4.0): rename `kakao_bus` entries to
    `korea_bus` in-place, and translate their entity unique_ids + device
    identifiers so statistics and automations stay attached.  All other
    entry types are a no-op v1->v2 bump.

    Returning True lets HA continue setup with the patched entry.
    Returning False marks the entry as unmigratable.
    """
    if entry.version == 1:
        if entry.data.get(CONF_ENTRY_TYPE) == "kakao_bus":
            from homeassistant.helpers import device_registry as dr
            from homeassistant.helpers import entity_registry as er

            new_data = {**entry.data, CONF_ENTRY_TYPE: "korea_bus"}
            hass.config_entries.async_update_entry(
                entry, data=new_data, version=2)

            ent_reg = er.async_get(hass)
            for ent in er.async_entries_for_config_entry(
                    ent_reg, entry.entry_id):
                if "_kakao_bus_" in ent.unique_id:
                    ent_reg.async_update_entity(
                        ent.entity_id,
                        new_unique_id=ent.unique_id.replace(
                            "_kakao_bus_", "_korea_bus_"),
                    )
            dev_reg = dr.async_get(hass)
            for dev in dr.async_entries_for_config_entry(
                    dev_reg, entry.entry_id):
                new_ids = {
                    (domain, ident.replace("kakao_bus_", "korea_bus_"))
                    if ident.startswith("kakao_bus_") else (domain, ident)
                    for domain, ident in dev.identifiers
                }
                if new_ids != dev.identifiers:
                    dev_reg.async_update_device(
                        dev.id, new_identifiers=new_ids)
        else:
            # All non-kakao_bus entries just bump their version forward —
            # nothing else changed in the v1->v2 step.
            hass.config_entries.async_update_entry(entry, version=2)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    etype = entry.data.get(CONF_ENTRY_TYPE) or entry.data.get("service")
    store: dict = {}

    if etype == ENTRY_WEATHER:
        from .weather.coordinator import WeatherWarningCoordinator
        api_key = entry.data["api_key"]
        c = WeatherWarningCoordinator(hass, api_key, entry.data.get("area_codes", []))
        await c.async_config_entry_first_refresh()
        store = {"coordinator": c, "area_codes": entry.data.get("area_codes", [])}

    elif etype == ENTRY_TRANSIT:
        from .transit.subway_coordinator import SubwayCoordinator
        from .transit.bus_coordinator import BusCoordinator
        from .transit.services import async_register_services
        seoul_key = entry.data.get("seoul_api_key", "")
        bus_key = entry.data.get("bus_api_key", "")
        sg: dict[str, list] = {}
        for item in entry.data.get("subway_items", []):
            sg.setdefault(item["station"], []).append(item)
        sc = {}
        for station, subs in sg.items():
            c = SubwayCoordinator(hass, seoul_key, station, subs)
            await c.async_config_entry_first_refresh()
            sc[station] = c
        bus_coords = {}
        for stop in entry.data.get("bus_stops", []):
            bc = BusCoordinator(hass, stop["stop_id"], stop["stop_name"])
            await bc.async_config_entry_first_refresh()
            bus_coords[stop["stop_id"]] = bc
        store = {"subway_coords": sc, "bus_coords": bus_coords,
                 "subway_items": entry.data.get("subway_items", []),
                 "bus_stops": entry.data.get("bus_stops", [])}
        if bus_key:
            async_register_services(hass, bus_key)

    elif etype == ENTRY_FUEL:
        from .fuel.coordinator import FuelCoordinator
        api_key = entry.data["api_key"]
        configs = entry.data.get("configs", [])
        if not configs and "sido_code" in entry.data:
            configs = [{"sido_code": entry.data["sido_code"], "fuel_code": entry.data["fuel_code"]}]
        c = FuelCoordinator(hass, api_key, configs)
        await c.async_config_entry_first_refresh()
        store = {"coordinator": c, "configs": configs}

    elif etype == ENTRY_SCHOOL:
        from .school.coordinator import SchoolCoordinator
        c = SchoolCoordinator(hass, entry)
        await c.async_config_entry_first_refresh()
        store = {"coordinator": c}

    elif etype == ENTRY_DISASTER:
        from .disaster.coordinator import DisasterCoordinator
        api_key = entry.data["api_key"]
        region = entry.data.get("region_filter", "")
        c = DisasterCoordinator(hass, api_key, region)
        await c.async_config_entry_first_refresh()
        store = {"coordinator": c, "region": region}

    elif etype == ENTRY_SAFETY_ALERT:
        from .safety_alert.coordinator import SafetyAlertCoordinator
        regions = entry.data.get("regions", [])
        # Backward-compat: single area_code schema (older saved entries).
        if not regions and entry.data.get("area_code"):
            regions = [{
                "code": entry.data["area_code"],
                "name": entry.data.get("area_name", ""),
                "code2": entry.data.get("area_code2"),
                "code3": entry.data.get("area_code3"),
            }]
        # Backward-compat: even older area_codes (plural, bare list of strings)
        # schema — produced 17-sensor entity layout that's now orphaned. Map
        # each bare code into the current {"code", "name"} shape so the entry
        # auto-heals on next HA start instead of staying empty.
        if not regions and entry.data.get("area_codes"):
            legacy = entry.data["area_codes"]
            if isinstance(legacy, list):
                regions = [
                    {"code": c, "name": ""} if isinstance(c, str)
                    else {"code": c.get("code", ""), "name": c.get("name", "")}
                    for c in legacy if c
                ]
        coordinators = {}
        for region in regions:
            c = SafetyAlertCoordinator(
                hass,
                region["code"],
                region.get("code2"),
                region.get("code3"),
            )
            await c.async_config_entry_first_refresh()
            coordinators[region["code"]] = c
        store = {"coordinators": coordinators, "regions": regions}

    elif etype == ENTRY_KEPCO:
        from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
        from .kepco.coordinator import KepcoCoordinator
        from .kepco.exceptions import KepcoAuthError
        c = KepcoCoordinator(hass, entry.data["username"], entry.data["password"])
        try:
            await c.async_login()
        except KepcoAuthError as e:
            raise ConfigEntryAuthFailed(f"KEPCO 로그인 실패: {e}") from e
        except Exception as e:  # noqa: BLE001
            raise ConfigEntryNotReady(f"KEPCO 연결 실패: {e}") from e
        await c.async_config_entry_first_refresh()
        store = {"coordinator": c}

    elif etype == ENTRY_GASAPP:
        from .gasapp.coordinator import GasAppCoordinator
        c = GasAppCoordinator(hass, entry.data["token"],
                               entry.data["member_id"], entry.data["contract_num"])
        await c.async_config_entry_first_refresh()
        store = {"coordinator": c}

    elif etype == ENTRY_ARISU:
        from .arisu.coordinator import ArisuCoordinator
        c = ArisuCoordinator(hass, entry.data["customer_number"], entry.data["customer_name"])
        await c.async_config_entry_first_refresh()
        store = {"coordinator": c}

    elif etype == ENTRY_PHARMACY:
        from .pharmacy.coordinator import PharmacyCoordinator
        from .pharmacy.services import async_register_pharmacy_service
        api_key = entry.data["api_key"]
        c = PharmacyCoordinator(hass, api_key,
                                 entry.data["q0"], entry.data.get("q1", ""))
        await c.async_config_entry_first_refresh()
        store = {"coordinator": c}
        async_register_pharmacy_service(hass, api_key)

    elif etype == ENTRY_AIRKOREA:
        from .airkorea.coordinator import AirKoreaCoordinator
        api_key = entry.data["api_key"]
        living_key = entry.data.get("living_api_key", "") or api_key
        stations = entry.data.get("stations", [])
        sido = entry.data.get("sido", "서울")
        c = AirKoreaCoordinator(hass, api_key, stations,
                                 living_api_key=living_key, sido=sido)
        await c.async_config_entry_first_refresh()
        store = {"coordinator": c, "stations": stations}
        from .airkorea.services import async_register_airkorea_services
        async_register_airkorea_services(hass, api_key, living_key, sido)

    elif etype == ENTRY_KMA_WEATHER:
        from .kma_weather.coordinator import KMAWeatherCoordinator
        api_key = entry.data["api_key"]
        regions = entry.data.get("regions", [])
        c = KMAWeatherCoordinator(
            hass, api_key, regions,
            air_api_key=api_key,
            air_station=entry.data.get("air_station", ""),
            living_api_key=api_key,
            area_no=entry.data.get("area_no", ""),
        )
        await c.async_config_entry_first_refresh()
        store = {"coordinator": c, "regions": regions}

    elif etype == ENTRY_EARTHQUAKE:
        from .earthquake.coordinator import EarthquakeCoordinator
        api_key = entry.data["api_key"]
        c = EarthquakeCoordinator(hass, api_key)
        await c.async_config_entry_first_refresh()
        store = {"coordinator": c}

    elif etype == ENTRY_SEOUL_BUS:
        from .seoul_bus.coordinator import SeoulBusCoordinator
        api_key = entry.data["api_key"]
        stations = entry.data.get("stations", [])
        coords: dict[str, SeoulBusCoordinator] = {}
        for st in stations:
            c = SeoulBusCoordinator(
                hass, api_key,
                ars_id=st["ars_id"],
                station_name=st.get("station_name") or st["ars_id"],
                include_routes=st.get("routes") or [],
            )
            # First refresh runs with api_enabled=True (default) so the
            # entities have data to show right after install.  We then
            # flip it OFF; SeoulBusActiveSwitch.async_added_to_hass will
            # restore the user's last choice via RestoreEntity.
            await c.async_config_entry_first_refresh()
            c.api_enabled = False
            coords[st["ars_id"]] = c
        store = {"coordinators": coords, "stations": stations}

    elif etype == ENTRY_KOREA_BUS:
        from .korea_bus.coordinator import KoreaBusCoordinator
        from .korea_bus import KOREA_BUS_SCAN_INTERVAL
        scan = entry.options.get("scan_interval",
                                 entry.data.get("scan_interval",
                                                KOREA_BUS_SCAN_INTERVAL))
        stops = entry.data.get("stops", [])
        kbus_coords: dict[str, KoreaBusCoordinator] = {}
        for stop in stops:
            c = KoreaBusCoordinator(
                hass,
                stop_id=stop["stop_id"],
                stop_name=stop.get("stop_name") or stop["stop_id"],
                include_routes=stop.get("routes") or [],
                scan_interval=scan,
            )
            # Same first-refresh-then-OFF pattern as seoul_bus.
            await c.async_config_entry_first_refresh()
            c.api_enabled = False
            kbus_coords[stop["stop_id"]] = c
        store = {"coordinators": kbus_coords, "stops": stops}

    hass.data[DOMAIN][entry.entry_id] = store
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORM_MAP.get(etype, []))
    store["unregister_llm"] = await async_setup_llm_api(hass, entry, etype)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    etype = entry.data.get(CONF_ENTRY_TYPE) or entry.data.get("service")
    store = hass.data.get(DOMAIN, {}).get(entry.entry_id, {}) or {}
    async_cleanup_llm_api(store.get("unregister_llm"))
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORM_MAP.get(etype, [])):
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
