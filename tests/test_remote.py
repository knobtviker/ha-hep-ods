import asyncio
import aiohttp
import logging
import os
import sys
from unittest.mock import MagicMock
from dotenv import load_dotenv

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

    
    load_dotenv()
    username = os.getenv("HEP_USERNAME")
    password = os.getenv("HEP_PASSWORD")
    omm_id = os.getenv("HEP_OMM")

    print(f"Testing with user: {username}")

    async with aiohttp.ClientSession() as session:
        client = HepApiClient(username, password, session)
        # Point to real API
        client.set_base_url("https://mojracun.hep.hr/elektra/v1/api")
        client.set_mojamreza_url("https://mojamreza.hep.hr")

        print("\n[1] Authenticating...")
        if await client.authenticate():
            print("Authentication SUCCESS")
            
            # Display captured cookies from the API client
            print(f"\n[DEBUG] Captured Cookies (stored in client): {len(client._cookies)}")
            for key, value in client._cookies.items():
                print(f"  {key}: {value}")
            
            # Also show session cookie jar for comparison
            print(f"\n[DEBUG] Session Cookie Jar Size: {len(session.cookie_jar)}")
            for cookie in session.cookie_jar:
                print(f"  {cookie.key} (Domain: {cookie['domain']})")
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


        # OMM check - now using auto-token fetching
        if user_data and user_data.accounts:
            account = user_data.accounts[0]
            omm_id = account.broj_brojila
            
            print(f"\n[7] Checking OMM status for {omm_id}...")
            try:
                # The client will automatically fetch tokens from the OMM page
                omm_check = await client.check_omm(omm_id)
                if omm_check:
                    print("OMM check successful!")
                    print(f"  OMM: {omm_check.omm}")
                    print(f"  Number of tariffs: {omm_check.br_tarifa}")
                    print(f"  Status: {omm_check.status.opis} (code: {omm_check.status.status})")
                    if omm_check.br_tarifa >= 1:
                        print(f"  Tariff 1 range: {omm_check.tarifa1_od} - {omm_check.tarifa1_do}")
                    if omm_check.br_tarifa >= 2:
                        print(f"  Tariff 2 range: {omm_check.tarifa2_od} - {omm_check.tarifa2_do}")
                else:
                    print("OMM check returned None")
            except Exception as e:
                print(f"Error checking OMM: {e}")
        else:
            print("\n[7] OMM check - skipped (no account data)")


    print("\n--- Test Finished ---")

if __name__ == "__main__":
    asyncio.run(main())
