import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
import socket

from .const import DOMAIN

class RctBatteryAnalyticsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            
            try:
                # Verbindungstest ohne Blockieren des Event-Loops
                await self.hass.async_add_executor_job(self._test_connection, host)
                
                return self.async_create_entry(
                    title=f"RCT Inverter ({host})", 
                    data=user_input
                )
            except Exception:
                # Dies korrespondiert mit dem Fehler-Key in der strings.json
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user", 
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str, # Leer lassen erzwingt Eingabe
            }),
            errors=errors
        )

    def _test_connection(self, host):
        """Versucht eine kurze Socket-Verbindung auf Port 8899."""
        # Wir versuchen nur zu verbinden. Wenn das klappt, ist der Inverter da.
        with socket.create_connection((host, 8899), timeout=3):
            return True