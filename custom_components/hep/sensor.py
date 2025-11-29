"""Sensor platform for HEP."""
import logging
from datetime import timedelta, datetime
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, CURRENCY_EURO
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .models import HepUser, HepAccount

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=24)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the HEP sensor platform."""
    client = hass.data[DOMAIN][entry.entry_id]

    coordinator = HepDataUpdateCoordinator(hass, client)
    
    # Force immediate data fetch on setup (including when integration is reloaded)
    # This ensures fresh data is available immediately after reload
    await coordinator.async_config_entry_first_refresh()

    entities = []
    if coordinator.data and coordinator.data.user and coordinator.data.user.accounts:
        for account in coordinator.data.user.accounts:
            # Current meter readings
            entities.append(HepMeterReadingSensor(coordinator, account, "Tarifa 1", "br_tarifa1"))
            entities.append(HepMeterReadingSensor(coordinator, account, "Tarifa 2", "br_tarifa2"))
            
            # Balance sensor
            entities.append(HepBalanceSensor(coordinator, account))
            
            # Pricing sensors
            entities.append(HepPricingSensor(coordinator, account, "VT", "vt"))
            entities.append(HepPricingSensor(coordinator, account, "NT", "nt"))
            
            # Consumption sensors (last period)
            entities.append(HepConsumptionHistorySensor(coordinator, account, "T1", "tarifa1"))
            entities.append(HepConsumptionHistorySensor(coordinator, account, "T2", "tarifa2"))
            
            # Warning binary sensor
            entities.append(HepWarningBinarySensor(coordinator, account))

    async_add_entities(entities)


class HepDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching HEP data."""

    def __init__(self, hass, client):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            # Fetch user data
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
                
                try:
                    billing_data = await self.client.get_billing(kupac_id)
                except Exception as e:
                    _LOGGER.warning("Failed to fetch billing data: %s", e)
                
                try:
                    consumption_data = await self.client.get_consumption(kupac_id)
                except Exception as e:
                    _LOGGER.warning("Failed to fetch consumption data: %s", e)
                
                try:
                    warnings_data = await self.client.get_warnings(kupac_id)
                except Exception as e:
                    _LOGGER.warning("Failed to fetch warnings data: %s", e)
                
                try:
                    prices_data = await self.client.get_prices()
                except Exception as e:
                    _LOGGER.warning("Failed to fetch prices data: %s", e)
            
            return {
                "user": user_data,
                "billing": billing_data,
                "consumption": consumption_data,
                "warnings": warnings_data,
                "prices": prices_data,
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")


class HepBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for HEP sensors."""

    def __init__(self, coordinator, account: HepAccount, name: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._account = account
        self._attr_name = f"HEP {account.naziv} {name}"
        self._attr_unique_id = f"hep_{account.kupac_id}_{name.lower().replace(' ', '_')}"
        
        # Device info - group all sensors under one device per account
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(account.kupac_id))},
            name=f"HEP {account.naziv}",
            manufacturer="HEP Elektra",
            model="Electricity Account",
            configuration_url="https://mojracun.hep.hr",
        )

    def _get_account_data(self):
        """Get account data from coordinator."""
        if not self.coordinator.data or not self.coordinator.data.get("user"):
            return None
        
        for account in self.coordinator.data["user"].accounts:
            if account.kupac_id == self._account.kupac_id:
                return account
        return None


class HepMeterReadingSensor(HepBaseSensor):
    """Sensor for current meter readings."""

    def __init__(self, coordinator, account: HepAccount, tariff_name: str, attribute: str):
        """Initialize the meter reading sensor."""
        super().__init__(coordinator, account, f"{tariff_name} Reading")
        self._attribute = attribute
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_suggested_display_precision = 0

    @property
    def native_value(self):
        """Return the state of the sensor."""
        account = self._get_account_data()
        if account:
            return getattr(account, self._attribute, None)
        return None

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        account = self._get_account_data()
        if not account:
            return {}
        
        return {
            "meter_number": account.broj_brojila,
            "tariff_model": account.tarifni_model,
            "contract_account": account.ugovorni_racun.strip() if account.ugovorni_racun else None,
            "last_reading_date": account.datum_web_ocitanja,
        }


class HepBalanceSensor(HepBaseSensor):
    """Sensor for account balance."""

    def __init__(self, coordinator, account: HepAccount):
        """Initialize the balance sensor."""
        super().__init__(coordinator, account, "Balance")
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_native_unit_of_measurement = CURRENCY_EURO
        self._attr_suggested_display_precision = 2

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.get("billing"):
            return None
        
        billing = self.coordinator.data["billing"]
        if billing and billing.balance:
            return billing.balance.iznos
        return None

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        if not self.coordinator.data or not self.coordinator.data.get("billing"):
            return {}
        
        billing = self.coordinator.data["billing"]
        if not billing or not billing.balance:
            return {}
        
        attrs = {
            "description": billing.balance.opis,
            "currency": billing.balance.iznos_val,
        }
        
        # Add latest bill info
        if billing.bills and len(billing.bills) > 0:
            latest_bill = billing.bills[0]
            attrs["latest_bill_date"] = latest_bill.datum
            attrs["latest_bill_description"] = latest_bill.opis
            attrs["latest_bill_amount"] = latest_bill.iznos_ispis
            attrs["latest_bill_due_date"] = latest_bill.dospijeva
            attrs["latest_bill_status"] = latest_bill.status
        
        return attrs


class HepPricingSensor(HepBaseSensor):
    """Sensor for electricity pricing."""

    def __init__(self, coordinator, account: HepAccount, tariff_type: str, attribute: str):
        """Initialize the pricing sensor."""
        super().__init__(coordinator, account, f"Price {tariff_type}")
        self._tariff_type = tariff_type
        self._attribute = attribute
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_native_unit_of_measurement = f"{CURRENCY_EURO}/kWh"
        self._attr_suggested_display_precision = 6

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.get("prices"):
            return None
        
        prices = self.coordinator.data["prices"]
        account = self._get_account_data()
        
        if not prices or not account:
            return None
        
        # Determine tariff model (bijeli, plavi, crveni)
        tariff_model = account.tarifni_model.lower() if account.tarifni_model else "bijeli"
        if "bijeli" in tariff_model:
            model = prices.bijeli
        elif "plavi" in tariff_model:
            model = prices.plavi
        elif "crveni" in tariff_model:
            model = prices.crveni
        else:
            model = prices.bijeli
        
        # Calculate total price
        proizvodnja = getattr(model.proizvodnja, self._attribute, 0)
        prijenos = getattr(model.prijenos, self._attribute, 0)
        distribucija = getattr(model.distribucija, self._attribute, 0)
        
        total = proizvodnja + prijenos + distribucija + prices.oie + prices.opskrba
        total_with_pdv = total * (1 + prices.pdv)
        
        return round(total_with_pdv, 6)

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        if not self.coordinator.data or not self.coordinator.data.get("prices"):
            return {}
        
        prices = self.coordinator.data["prices"]
        account = self._get_account_data()
        
        if not prices or not account:
            return {}
        
        tariff_model = account.tarifni_model.lower() if account.tarifni_model else "bijeli"
        if "bijeli" in tariff_model:
            model = prices.bijeli
        elif "plavi" in tariff_model:
            model = prices.plavi
        elif "crveni" in tariff_model:
            model = prices.crveni
        else:
            model = prices.bijeli
        
        proizvodnja = getattr(model.proizvodnja, self._attribute, 0)
        prijenos = getattr(model.prijenos, self._attribute, 0)
        distribucija = getattr(model.distribucija, self._attribute, 0)
        
        return {
            "tariff_model": account.tarifni_model,
            "production": round(proizvodnja, 6),
            "transmission": round(prijenos, 6),
            "distribution": round(distribucija, 6),
            "renewable_energy_fee": round(prices.oie, 6),
            "supply": round(prices.opskrba, 6),
            "vat_rate": prices.pdv,
        }


class HepConsumptionHistorySensor(HepBaseSensor):
    """Sensor for consumption history."""

    def __init__(self, coordinator, account: HepAccount, tariff_name: str, attribute: str):
        """Initialize the consumption history sensor."""
        super().__init__(coordinator, account, f"Last Period {tariff_name}")
        self._attribute = attribute
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_suggested_display_precision = 0

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.get("consumption"):
            return None
        
        consumption_list = self.coordinator.data["consumption"]
        if consumption_list and len(consumption_list) > 0:
            latest = consumption_list[0]
            return getattr(latest, self._attribute, 0)
        
        return None

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        if not self.coordinator.data or not self.coordinator.data.get("consumption"):
            return {}
        
        consumption_list = self.coordinator.data["consumption"]
        if not consumption_list or len(consumption_list) == 0:
            return {}
        
        latest = consumption_list[0]
        return {
            "period": latest.razdoblje,
            "tariff_1": latest.tarifa1,
            "tariff_2": latest.tarifa2,
            "tariff_3": latest.tarifa3,
            "production_1": latest.proizv1,
            "production_2": latest.proizv2,
        }


class HepWarningBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for payment warnings."""

    def __init__(self, coordinator, account: HepAccount):
        """Initialize the warning binary sensor."""
        super().__init__(coordinator)
        self._account = account
        self._attr_name = f"HEP {account.naziv} Payment Warning"
        self._attr_unique_id = f"hep_{account.kupac_id}_payment_warning"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        
        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(account.kupac_id))},
            name=f"HEP {account.naziv}",
            manufacturer="HEP Elektra",
            model="Electricity Account",
            configuration_url="https://mojracun.hep.hr",
        )

    @property
    def is_on(self):
        """Return true if there are warnings."""
        if not self.coordinator.data or not self.coordinator.data.get("warnings"):
            return False
        
        warnings = self.coordinator.data["warnings"]
        return warnings and len(warnings) > 0

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        if not self.coordinator.data or not self.coordinator.data.get("warnings"):
            return {}
        
        warnings = self.coordinator.data["warnings"]
        if not warnings or len(warnings) == 0:
            return {}
        
        attrs = {
            "warning_count": len(warnings),
        }
        
        # Add latest warning details
        latest = warnings[0]
        attrs["latest_warning_date"] = latest.datum_izdavanja
        attrs["latest_warning_level"] = latest.razina
        attrs["latest_warning_amount"] = latest.stanje
        if latest.broj_dokumenta:
            attrs["latest_warning_document"] = latest.broj_dokumenta
        
        return attrs
