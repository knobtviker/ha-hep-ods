"""The HEP integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD
from .api import HepApiClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

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

    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
