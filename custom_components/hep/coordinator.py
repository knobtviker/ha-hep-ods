"""DataUpdateCoordinator for HEP integration."""
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

class HepDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching HEP data."""

    def __init__(self, hass: HomeAssistant, client):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            # Re-authenticate to get fresh session cookies
            if not await self.client.authenticate():
                raise UpdateFailed("Authentication failed")
            
            # Fetch user data (already fetched during authenticate, but this ensures consistency)
            user_data = await self.client.get_data()
            if not user_data:
                raise UpdateFailed("No user data returned from API")
            
            # Fetch additional data for first account
            billing_data = None
            consumption_data = None
            warnings_data = None
            prices_data = None
            
            if user_data.accounts:
                kupac_id = user_data.accounts[0].kupac_id
            if user_data.accounts:
                kupac_id = user_data.accounts[0].kupac_id
                
                try:
                    billing_data = await self.client.get_billing(kupac_id)
                except Exception as e:
                    _LOGGER.error("Failed to fetch billing data: %s", e, exc_info=True)
                
                try:
                    consumption_data = await self.client.get_consumption(kupac_id)
                except Exception as e:
                    _LOGGER.error("Failed to fetch consumption data: %s", e, exc_info=True)
                
                try:
                    warnings_data = await self.client.get_warnings(kupac_id)
                except Exception as e:
                    _LOGGER.error("Failed to fetch warnings data: %s", e, exc_info=True)
                
                try:
                    prices_data = await self.client.get_prices()
                except Exception as e:
                    _LOGGER.error("Failed to fetch prices data: %s", e, exc_info=True)
            
            return {
                "user": user_data,
                "billing": billing_data,
                "consumption": consumption_data,
                "warnings": warnings_data,
                "prices": prices_data,
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
