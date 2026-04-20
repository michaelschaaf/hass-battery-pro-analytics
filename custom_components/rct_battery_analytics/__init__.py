import logging
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .rctclient_logic import RctDataFetcher

_LOGGER = logging.getLogger(__name__)
DOMAIN = "rct_battery_analytics"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    host = entry.data.get("host")
    fetcher = RctDataFetcher(host)

    async def _async_update_data():
        data = await fetcher.fetch_all_data()
        if not data or data.get("soc") is None:
            raise UpdateFailed("Ungültige Daten vom Inverter")
        return data

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Battery Pro Analytics",
        update_method=_async_update_data,
        update_interval=timedelta(seconds=60),
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok