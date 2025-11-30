import asyncio
import aiohttp
import logging
import os
import sys
from unittest.mock import MagicMock

# Mock Home Assistant modules
# Mock Home Assistant modules
sys.modules["homeassistant"] = MagicMock()
sys.modules["homeassistant.core"] = MagicMock()
sys.modules["homeassistant.config_entries"] = MagicMock()
sys.modules["homeassistant.const"] = MagicMock()
sys.modules["homeassistant.helpers"] = MagicMock()
sys.modules["homeassistant.helpers.aiohttp_client"] = MagicMock()

# Add parent directory to path to find custom_components
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import after mocking
from custom_components.hep.api import HepApiClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)
_LOGGER = logging.getLogger(__name__)

async def main():
    print("--- Starting HEP Remote API Test ---")

    # Using credentials from mock_server.py (Index 1)
    username = "bojan.komljenovic@gmail.com"
    password = "uWKrB.J62nN2zP3Xh8qd@B6KtYDkw7TH"
    omm_id = "0126535651"

    print(f"Testing with user: {username}")

    async with aiohttp.ClientSession() as session:
        client = HepApiClient(username, password, session)
        # Point to real API
        client.set_base_url("https://mojracun.hep.hr/elektra/v1/api")
        client.set_mojamreza_url("https://mojamreza.hep.hr")

        print("\n[1] Authenticating...")
        if await client.authenticate():
            print("Authentication SUCCESS")
            print(f"\n[DEBUG] Cookie Jar Size: {len(session.cookie_jar)}")
            for cookie in session.cookie_jar:
                print(f"  {cookie.key}: {cookie.value} (Domain: {cookie['domain']})")
            
            # Check if we have tokens in user_data
            # We need to access the raw dict if possible, but we have the object.
            # Let's just inspect the object properties we have.
            # HepUser doesn't store the raw token if it was in the response but not in the model.
            # But we can check if the response had it.
            # For now, let's rely on cookies.
        else:
            print("Authentication FAILED")
            return

        print("\n[2] Fetching User Data...")
        try:
            user_data = await client.get_data()
            print(f"User: {user_data.first_name} {user_data.last_name} ({user_data.email})")
            for acc in user_data.accounts:
                print(f"  - Account: {acc.naziv} ({acc.kupac_id})")
                print(f"    Contract Account: {acc.ugovorni_racun}")
                print(f"    Meter Number: {acc.broj_brojila}")
                print(f"    Tariffs: T1={acc.br_tarifa1}, T2={acc.br_tarifa2}")
        except Exception as e:
            print(f"Error fetching user data: {e}")

        print("\n[3] Fetching Prices...")
        try:
            prices = await client.get_prices()
            if prices:
                print("Prices fetched successfully.")
                print(f"  PDV: {prices.pdv}")
                print(f"  Bijeli VT Proizvodnja: {prices.bijeli.proizvodnja.vt}")
            else:
                print("Prices fetch returned None")
        except Exception as e:
            print(f"Error fetching prices: {e}")

        if user_data and user_data.accounts:
            account = user_data.accounts[0]
            kupac_id = account.kupac_id
            print(f"\nUsing Account ID: {kupac_id} for further tests")

            print("\n[4] Fetching Billing Info...")
            try:
                billing = await client.get_billing(kupac_id)
                if billing:
                    print("Billing info fetched successfully.")
                    print(f"  Balance: {billing.balance.iznos_val}")
                    print(f"  Latest bill: {billing.bills[0].opis} - {billing.bills[0].iznos_ispis} ({billing.bills[0].datum})")
                else:
                    print("Billing info fetch returned None")
            except Exception as e:
                print(f"Error fetching billing info: {e}")

            print("\n[5] Fetching Consumption Info...")
            try:
                consumption = await client.get_consumption(kupac_id)
                if consumption:
                    print("Consumption info fetched successfully.")
                    print(f"  Records found: {len(consumption)}")
                    if len(consumption) > 0:
                        latest = consumption[0]
                        print(f"  Latest: {latest.razdoblje} - T1: {latest.tarifa1}, T2: {latest.tarifa2}")
                else:
                    print("Consumption info fetch returned None or empty")
            except Exception as e:
                print(f"Error fetching consumption info: {e}")

            print("\n[6] Fetching Warnings...")
            try:
                warnings = await client.get_warnings(kupac_id)
                if warnings:
                    print("Warnings fetched successfully.")
                    print(f"  Warnings found: {len(warnings)}")
                    if len(warnings) > 0:
                        latest_w = warnings[0]
                        print(f"  Latest: {latest_w.datum_izdavanja} - {latest_w.razina} ({latest_w.stanje})")
                else:
                    print("Warnings fetch returned None or empty (Good!)")
            except Exception as e:
                print(f"Error fetching warnings: {e}")

        # OMM check skipped - requires separate authentication flow
        print("\n[7] OMM check - skipped (requires browser session tokens)")

    print("\n--- Test Finished ---")

if __name__ == "__main__":
    asyncio.run(main())
