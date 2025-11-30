"""Test script for HEP API Client."""
import asyncio
import logging
import sys
from unittest.mock import MagicMock

# Mock homeassistant modules to avoid ImportError when importing from custom_components.hep
sys.modules["homeassistant"] = MagicMock()
sys.modules["homeassistant.config_entries"] = MagicMock()
sys.modules["homeassistant.const"] = MagicMock()
sys.modules["homeassistant.core"] = MagicMock()
sys.modules["homeassistant.exceptions"] = MagicMock()
sys.modules["homeassistant.helpers"] = MagicMock()
sys.modules["homeassistant.helpers.aiohttp_client"] = MagicMock()
sys.modules["homeassistant.helpers.entity_platform"] = MagicMock()
sys.modules["homeassistant.helpers.update_coordinator"] = MagicMock()
sys.modules["homeassistant.components"] = MagicMock()
sys.modules["homeassistant.components.sensor"] = MagicMock()

import os
# Add parent directory to path to find custom_components
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from custom_components.hep.api import HepApiClient

# Configure logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

async def main():
    print("--- Starting HEP API Test ---")
    
    # 1. Test with correct credentials
    print("\n[Test 1] Testing with correct credentials...")
    # Using the credentials provided by the user in the prompt for the mock
    client = HepApiClient("testuser", "password123")
    
    # Override base URL to point to local mock server
    client.set_base_url("http://localhost:5001/elektra/v1/api")
    
    print("Authenticating...")
    if await client.authenticate():
        print("Authentication SUCCESS")
        
        print("Fetching data...")
        user_data = await client.get_data()
        if user_data:
            print(f"User: {user_data.first_name} {user_data.last_name}")
            if user_data.accounts:
                acc = user_data.accounts[0]
                print(f"Proposed Entry Title: {acc.naziv} ({acc.ugovorni_racun})")
            
            for acc in user_data.accounts:
                print(f"Account: {acc.sifra}, Tarifa 1: {acc.br_tarifa1}, Tarifa 2: {acc.br_tarifa2}")
        else:
            print("Data fetch FAILED")
            
        print("Fetching prices...")
        prices = await client.get_prices()
        if prices:
            print(f"Prices fetched successfully.")
            print(f"PDV: {prices.pdv}")
            print(f"Bijeli VT Proizvodnja: {prices.bijeli.proizvodnja.vt}")
        else:
            print("Price fetch FAILED")

        print("Fetching billing info...")
        # Assuming we have at least one account
        if user_data and user_data.accounts:
            kupac_id = user_data.accounts[0].kupac_id
            billing = await client.get_billing(kupac_id)
            if billing:
                print(f"Billing info fetched successfully.")
                print(f"Balance: {billing.balance.iznos} {billing.balance.iznos_val}")
                print(f"Number of bills: {len(billing.bills)}")
                if billing.bills:
                    print(f"Latest bill: {billing.bills[0].opis} - {billing.bills[0].iznos_ispis}")
            else:
                print("Billing fetch FAILED")
        else:
            print("Skipping billing fetch (no account found)")

        print("Fetching consumption info...")
        if user_data and user_data.accounts:
            kupac_id = user_data.accounts[0].kupac_id
            consumption = await client.get_consumption(kupac_id)
            if consumption:
                print(f"Consumption info fetched successfully.")
                print(f"Number of consumption records: {len(consumption)}")
                if consumption:
                    print(f"Latest record: {consumption[0].razdoblje} - T1: {consumption[0].tarifa1}")
            else:
                print("Consumption fetch FAILED or empty")
        
        print("Fetching warnings...")
        if user_data and user_data.accounts:
            kupac_id = user_data.accounts[0].kupac_id
            warnings = await client.get_warnings(kupac_id)
            if warnings:
                print(f"Warnings fetched successfully.")
                print(f"Number of warnings: {len(warnings)}")
                if warnings:
                    print(f"Latest warning: {warnings[0].datum_izdavanja} - {warnings[0].razina} ({warnings[0].stanje})")
            else:
                print("Warnings fetch FAILED or empty")

        print("Checking OMM...")
        if user_data and user_data.accounts:
            # We need to set the mojamreza URL to the mock server for this test
            client.set_mojamreza_url("http://localhost:5001")
            
            # Using dummy tokens for testing
            omm_check = await client.check_omm(
                omm="0126535651", 
                session_id="dummy_session", 
                cookie_token="dummy_cookie_token", 
                form_token="dummy_form_token"
            )
            
            if omm_check:
                print(f"OMM check successful.")
                print(f"OMM: {omm_check.omm}")
                print(f"Status: {omm_check.status.opis} ({omm_check.status.status})")
            else:
                print("OMM check FAILED")

            # Test Submission Flow
            print("Submitting reading (Step 1)...")
            submission = await client.submit_reading(
                omm="0126535651",
                session_id="dummy_session",
                cookie_token="dummy_cookie_token",
                form_token="dummy_form_token",
                enc_value="dummy_enc_value",
                date="29.11.2025.",
                tarifa1=26122,
                tarifa2=11852,
                posalji=0
            )
            
            if submission:
                print(f"Submission Step 1 Result: Status={submission.status}, Posalji={submission.posalji}, Opis={submission.opis}")
                
                if submission.status == 0 and submission.posalji == 1:
                    print("Submitting reading confirmation (Step 2)...")
                    confirmation = await client.submit_reading(
                        omm="0126535651",
                        session_id="dummy_session",
                        cookie_token="dummy_cookie_token",
                        form_token="dummy_form_token",
                        enc_value="dummy_enc_value",
                        date="29.11.2025.",
                        tarifa1=26122,
                        tarifa2=11852,
                        posalji=1
                    )
                    if confirmation:
                        print(f"Submission Step 2 Result: Status={confirmation.status}, Opis={confirmation.opis}")
                    else:
                        print("Submission Step 2 FAILED")
            else:
                print("Submission Step 1 FAILED")

    else:
        print("Authentication FAILED")

    print("\n--- Test Finished ---")

if __name__ == "__main__":
    asyncio.run(main())
