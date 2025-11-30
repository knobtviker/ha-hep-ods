"""Config flow for HEP integration."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD
from .api import HepApiClient

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)

async def validate_input(hass: HomeAssistant, data: dict) -> dict:
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    hub = HepApiClient(data[CONF_USERNAME], data[CONF_PASSWORD])

    if not await hub.authenticate():
        raise InvalidAuth

    user_data = await hub.get_data()
    
    # Default title
    title = data[CONF_USERNAME]
    
    # Try to get a better title from the first account
    if user_data.accounts:
        account = user_data.accounts[0]
        title = f"{account.naziv} ({account.ugovorni_racun})"
    elif user_data.first_name and user_data.last_name:
        title = f"{user_data.first_name} {user_data.last_name}"

    # Return info that you want to store in the config entry.
    return {"title": title}


class HepConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HEP."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return HepOptionsFlow(config_entry)


class HepOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for HEP."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=24)),
                }
            ),
        )


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
