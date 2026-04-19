import logging
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .rctclient import RctDataFetcher
from .const import DOMAIN, SCAN_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry):
    """Setzt die Integration über die Benutzeroberfläche auf."""
    host = entry.data["host"]
    fetcher = RctDataFetcher(host)

    async def async_update_data():
        """Holt die Daten vom Inverter."""
        # Wir lassen den subprocess im executor laufen, damit HA nicht blockt
        return await hass.async_add_executor_job(fetcher.fetch_all_data)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="RCT Battery Analytics",
        update_method=async_update_data,
        update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
    )

    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Leitet das Setup an die Sensoren weiter (kommt als nächstes)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    
    return True