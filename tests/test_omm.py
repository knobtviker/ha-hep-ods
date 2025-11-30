import asyncio
import aiohttp
import logging
import os
import sys
from unittest.mock import MagicMock
from dotenv import load_dotenv

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
from custom_components.hep.api import HepOmmClient

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
_LOGGER = logging.getLogger(__name__)

# Specifically enable aiohttp trace logging
logging.getLogger('aiohttp.client').setLevel(logging.DEBUG)

async def on_request_start(session, trace_config_ctx, params):
    print(f"\n{'='*80}")
    print(f"{params.method} {params.url}")
    for key, value in params.headers.items():
        print(f"{key}: {value}")
    print()

async def on_request_chunk_sent(session, trace_config_ctx, params):
    """Capture request body chunks."""
    if not hasattr(trace_config_ctx, 'request_chunks'):
        trace_config_ctx.request_chunks = []
    trace_config_ctx.request_chunks.append(params.chunk)

async def on_request_end(session, trace_config_ctx, params):
    # Print request body if we captured chunks
    if hasattr(trace_config_ctx, 'request_chunks') and trace_config_ctx.request_chunks:
        body = b''.join(trace_config_ctx.request_chunks).decode('utf-8', errors='replace')
        print(body)
        print()
    
    print(f"\nHTTP/{params.response.version.major}.{params.response.version.minor} {params.response.status} {params.response.reason}")
    for key, value in params.response.headers.items():
        print(f"{key}: {value}")
    print()
    try:
        body = await params.response.text()
        if body:
            print(f"{body}")
        else:
            print("[Empty body]")
    except:
        print("[Unable to read body]")
    print(f"{'='*80}\n")

async def main():
    print("--- Starting HEP OMM API Test ---")

    load_dotenv()
    username = os.getenv("HEP_USERNAME")
    password = os.getenv("HEP_PASSWORD")
    omm_id = os.getenv("HEP_OMM")

    print(f"Testing with user: {username}")

    # Create trace config
    trace_config = aiohttp.TraceConfig()
    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_chunk_sent.append(on_request_chunk_sent)
    trace_config.on_request_end.append(on_request_end)

    async with aiohttp.ClientSession(trace_configs=[trace_config]) as session:
        client = HepApiClient(username, password, session)

        _LOGGER.debug("\n[1] Authenticating...")
        if await client.authenticate():
            _LOGGER.debug("Authentication SUCCESS")
        else:
            print("Authentication FAILED")
            return

        _LOGGER.debug(f"\n[2] Checking OMM initialize for {omm_id}...")
        try:
            omm_client = HepOmmClient(omm_id, session)
            omm_initialize_check = await omm_client.initialize_session()
            if omm_initialize_check:
                _LOGGER.debug("OMM initialize successful!")

                _LOGGER.debug(f"\n[3] Checking OMM status for {omm_id}...")
                try:
                    omm_check = await omm_client.check_omm()
                    if omm_check:
                        _LOGGER.debug(f"\n[4] Submitting reading for {omm_id}...")
                        try:
                            enc = omm_check.enc_value
                            reading_date = "30.11.2025."
                            tarifa1 = 26123
                            tarifa2 = 11853
                            force_send = False
                            omm_reading = await omm_client.submit_reading(enc, reading_date, tarifa1, tarifa2, force_send)
                            if omm_reading:
                                _LOGGER.debug("OMM reading submitted successfully!")
                                _LOGGER.debug(f"OMM reading result: {omm_reading}")
                            else:
                                _LOGGER.error("OMM reading submission failed!")
                        except Exception as e:
                            _LOGGER.error(f"Error submitting reading: {e}")    
                except Exception as e:
                    _LOGGER.error(f"Error checking OMM status: {e}")
            else:
                _LOGGER.error("OMM initialize returned None")
        except Exception as e:
            _LOGGER.error(f"Error initialize OMM: {e}")

    _LOGGER.debug("\n--- Test Finished ---")

if __name__ == "__main__":
    asyncio.run(main())
