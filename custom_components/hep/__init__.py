"""The HEP integration."""
import logging
from datetime import datetime
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD
from .api import HepApiClient, HepOmmClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

# Service schemas
SERVICE_SUBMIT_OMM_READING = "submit_omm_reading"
SERVICE_FORCE_SUBMIT_OMM_READING = "force_submit_omm_reading"

ATTR_OMM_ID = "omm_id"
ATTR_TARIFA1 = "tarifa1"
ATTR_TARIFA2 = "tarifa2"
ATTR_READING_DATE = "reading_date"

SERVICE_SUBMIT_SCHEMA = vol.Schema({
    vol.Required(ATTR_OMM_ID): cv.string,
    vol.Required(ATTR_TARIFA1): vol.All(vol.Coerce(int), vol.Range(min=1)),
    vol.Required(ATTR_TARIFA2): vol.All(vol.Coerce(int), vol.Range(min=1)),
})

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HEP from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]

    # Initialize API client
    # We can pass the shared aiohttp session from HA
    session = None # hass.helpers.aiohttp_client.async_get_clientsession(hass) # Not available in this mock env, but standard practice
    # For now, we let the client create its own session if None, or we could try to import the helper if we were in a real HA env.
    # To keep it simple and working with the mock requirements, we'll instantiate it.
    
    client = HepApiClient(username, password)
    
    # Store the client in hass.data for platforms to access
    hass.data[DOMAIN][entry.entry_id] = client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register options update listener
    entry.async_on_unload(entry.add_update_listener(update_listener))
    
    # Register services
    async def handle_submit_omm_reading(call: ServiceCall) -> None:
        """Handle submit OMM reading service call."""
        omm_id = call.data[ATTR_OMM_ID]
        tarifa1 = call.data[ATTR_TARIFA1]
        tarifa2 = call.data[ATTR_TARIFA2]
        reading_date = datetime.now().strftime("%d.%m.%Y.")
        
        # Create OMM client
        omm_client = HepOmmClient(omm_id)
        
        # Submit reading
        success = await omm_client.send_reading(reading_date, tarifa1, tarifa2, force_send=False)
        
        if not success:
            raise HomeAssistantError(
                f"Failed to submit OMM reading for {omm_id}. "
                "The reading may already exist or be invalid. "
                f"Use '{DOMAIN}.{SERVICE_FORCE_SUBMIT_OMM_READING}' to force submit."
            )
    
    async def handle_force_submit_omm_reading(call: ServiceCall) -> None:
        """Handle force submit OMM reading service call."""
        omm_id = call.data[ATTR_OMM_ID]
        tarifa1 = call.data[ATTR_TARIFA1]
        tarifa2 = call.data[ATTR_TARIFA2]
        reading_date = datetime.now().strftime("%d.%m.%Y.")
        
        # Create OMM client
        omm_client = HepOmmClient(omm_id)
        
        # Force submit reading
        success = await omm_client.send_reading(reading_date, tarifa1, tarifa2, force_send=True)
        
        if not success:
            raise HomeAssistantError(
                f"Failed to force submit OMM reading for {omm_id}. "
                "Please check the reading values and try again."
            )
    
    # Register services only once (for the first config entry)
    if not hass.services.has_service(DOMAIN, SERVICE_SUBMIT_OMM_READING):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SUBMIT_OMM_READING,
            handle_submit_omm_reading,
            schema=SERVICE_SUBMIT_SCHEMA,
        )
    
    if not hass.services.has_service(DOMAIN, SERVICE_FORCE_SUBMIT_OMM_READING):
        hass.services.async_register(
            DOMAIN,
            SERVICE_FORCE_SUBMIT_OMM_READING,
            handle_force_submit_omm_reading,
            schema=SERVICE_SUBMIT_SCHEMA,
        )

    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
