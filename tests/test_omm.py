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
    omm_id = os.getenv("HEP_OMM")

    # Create trace config
    trace_config = aiohttp.TraceConfig()
    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_chunk_sent.append(on_request_chunk_sent)
    trace_config.on_request_end.append(on_request_end)

    async with aiohttp.ClientSession(trace_configs=[trace_config]) as session:

        _LOGGER.debug(f"\n[1] Checking OMM initialize for {omm_id}...")
        try:
            omm_client = HepOmmClient(omm_id)
            omm_client.setSession(session)

            reading_date = "30.11.2025."
            tarifa1 = 26124
            tarifa2 = 11854
            force_send = False
            
            send_reading = await omm_client.send_reading(reading_date, tarifa1, tarifa2, force_send)
            
            if send_reading:
                _LOGGER.debug("OMM reading submitted successfully!")
            else:
                _LOGGER.error("OMM reading submission failed!")

                force_send_reading = await omm_client.send_reading(reading_date, tarifa1, tarifa2, True)
            
                if force_send_reading:
                    _LOGGER.debug("OMM FORCE reading submitted successfully!")
                else:
                    _LOGGER.error("OMM FORCE reading submission failed!")
        except Exception as e:
            _LOGGER.error(f"Error initialize OMM: {e}")

    _LOGGER.debug("\n--- Test Finished ---")

if __name__ == "__main__":
    asyncio.run(main())
