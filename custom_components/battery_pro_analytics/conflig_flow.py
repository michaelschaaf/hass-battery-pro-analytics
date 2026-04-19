import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from .const import DOMAIN

class RctBatteryAnalyticsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handhabt den Konfigurations-Flow für RCT Advanced Battery Analytics."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Erster Schritt beim manuellen Hinzufügen durch den Benutzer."""
        errors = {}

        if user_input is not None:
            # Hier könnte man eine Validierung einbauen (z.B. Ping an die IP)
            # Für den Anfang vertrauen wir der Eingabe
            return self.async_create_entry(
                title=f"RCT Inverter ({user_input[CONF_HOST]})",
                data=user_input
            )

        # Das Formular, das dem User angezeigt wird
        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
        })

        return self.async_show_form(
            step_id="user", 
            data_schema=data_schema, 
            errors=errors
        )