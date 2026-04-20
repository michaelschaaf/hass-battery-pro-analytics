from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .rctclient_logic import RctDataFetcher
from .const import DOMAIN

async def async_setup_entry(hass, entry):
    host = entry.data["host"]
    fetcher = RctDataFetcher(host)

    async def async_update_data():
        # Das hier ist die Brücke zu deiner Logik
        return await fetcher.fetch_all_data()

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="RCT Battery Analytics",
        update_method=async_update_data,
        update_interval=timedelta(seconds=60), # HIER: Ohne das wird nie wieder abgefragt
    )

    # Ersten Abruf sofort erzwingen
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True