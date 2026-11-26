"""Register per-route entities when a station first reports a route."""
from homeassistant.core import callback


def register_routes(entry, coordinator, selected, device, add_entities, factories):
    registered = set()

    @callback
    def discover():
        entities = []
        for route in selected or coordinator.data or ():
            if route in registered:
                continue
            entities.extend(make(coordinator, route, device_info=device) for make in factories)
            registered.add(route)
        if entities:
            add_entities(entities)

    if not selected:
        entry.async_on_unload(coordinator.async_add_listener(discover))
    discover()
