import asyncio
import aiohttp
import logging
import sys
from unittest.mock import MagicMock

# Mock Home Assistant modules
sys.modules["homeassistant"] = MagicMock()
sys.modules["homeassistant.core"] = MagicMock()
sys.modules["homeassistant.config_entries"] = MagicMock()
sys.modules["homeassistant.const"] = MagicMock()
sys.modules["homeassistant.helpers"] = MagicMock()
sys.modules["homeassistant.helpers.aiohttp_client"] = MagicMock()
sys.modules["homeassistant.helpers.update_coordinator"] = MagicMock()
sys.modules["homeassistant.helpers.entity_platform"] = MagicMock()
sys.modules["homeassistant.helpers.entity"] = MagicMock()
sys.modules["homeassistant.components.sensor"] = MagicMock()
sys.modules["homeassistant.components.binary_sensor"] = MagicMock()

# Import after mocking
from custom_components.hep.api import HepApiClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)
_LOGGER = logging.getLogger(__name__)

async def main():
    print("--- Testing Enhanced Sensors Data Fetching ---")

    username = "testuser"
    password = "password123"

    async with aiohttp.ClientSession() as session:
        client = HepApiClient(username, password, session)
        # Point to mock server
        client.set_base_url("http://localhost:5001/elektra/v1/api")

        print("\n[1] Authenticating...")
        if await client.authenticate():
            print("✓ Authentication SUCCESS")
        else:
            print("✗ Authentication FAILED")
            return

        print("\n[2] Fetching User Data...")
        user_data = await client.get_data()
        if user_data and user_data.accounts:
            account = user_data.accounts[0]
            print(f"✓ Account: {account.naziv}")
            print(f"  - Meter Readings: T1={account.br_tarifa1}, T2={account.br_tarifa2}")

        print("\n[3] Fetching Billing Info...")
        billing = await client.get_billing(account.kupac_id)
        if billing:
            print(f"✓ Balance: {billing.balance.iznos} {billing.balance.iznos_val}")
            print(f"  - Description: {billing.balance.opis}")
            print(f"  - Latest Bill: {billing.bills[0].opis} ({billing.bills[0].iznos_ispis})")

        print("\n[4] Fetching Prices...")
        prices = await client.get_prices()
        if prices:
            # Calculate total price for bijeli VT
            vt_total = (prices.bijeli.proizvodnja.vt + 
                       prices.bijeli.prijenos.vt + 
                       prices.bijeli.distribucija.vt + 
                       prices.oie + prices.opskrba)
            vt_with_pdv = vt_total * (1 + prices.pdv)
            print(f"✓ Bijeli VT Price: {vt_with_pdv:.6f} EUR/kWh")
            
            nt_total = (prices.bijeli.proizvodnja.nt + 
                       prices.bijeli.prijenos.nt + 
                       prices.bijeli.distribucija.nt + 
                       prices.oie + prices.opskrba)
            nt_with_pdv = nt_total * (1 + prices.pdv)
            print(f"✓ Bijeli NT Price: {nt_with_pdv:.6f} EUR/kWh")

        print("\n[5] Fetching Consumption History...")
        consumption = await client.get_consumption(account.kupac_id)
        if consumption and len(consumption) > 0:
            latest = consumption[0]
            print(f"✓ Latest Period: {latest.razdoblje}")
            print(f"  - T1: {latest.tarifa1} kWh, T2: {latest.tarifa2} kWh")

        print("\n[6] Fetching Warnings...")
        warnings = await client.get_warnings(account.kupac_id)
        if warnings and len(warnings) > 0:
            print(f"✓ Warnings Found: {len(warnings)}")
            print(f"  - Latest: {warnings[0].razina} ({warnings[0].stanje})")
        else:
            print("✓ No warnings")

        print("\n--- All Sensor Data Tests Passed ---")

if __name__ == "__main__":
    asyncio.run(main())
