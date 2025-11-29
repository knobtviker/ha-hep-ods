"""Binary sensor platform for HEP."""
import logging
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .models import HepAccount

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the HEP binary sensor platform."""
    # Get the coordinator from sensor platform
    client = hass.data[DOMAIN][entry.entry_id]
    
    # The coordinator is created in sensor.py, we need to access it
    # For now, binary sensors are created in sensor.py directly
    pass
