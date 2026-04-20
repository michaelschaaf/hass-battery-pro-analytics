import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN
from .rctclient_logic import RctDataFetcher

# DIESE ZEILE FEHLT:
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
    host = entry.data["host"]
    fetcher = RctDataFetcher(host)

    async def async_update_data():
        """Methode, die vom Coordinator aufgerufen wird."""
        try:
            return await fetcher.fetch_all_data()
        except Exception as err:
            _LOGGER.error("Fehler beim Abrufen der RCT Daten: %s", err)
            raise

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="RCT Battery Analytics",
        update_method=async_update_data,
        update_interval=timedelta(seconds=60),
    )

    # Ersten Abruf beim Start machen
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True