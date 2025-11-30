"""API Client for HEP."""
import logging
import aiohttp
import async_timeout
from typing import List
import re
import time
from .models import HepUser, HepPrices, HepBillingInfo, HepConsumption, HepWarning, HepOmmCheck, HepOmmCheckResult, HepReadingSubmissionResult

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
_LOGGER = logging.getLogger(__name__)

class HepApiClient:
    """HEP API Client."""

    def __init__(self, username, password, session=None):
        """Initialize the API client."""
        self._username = username
        self._password = password
        self._session = session
        self._user_data = None
        self._cookies = {}
        self._base_url = "https://mojracun.hep.hr/elektra/v1/api"
        self._headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        }

    async def authenticate(self) -> bool:
        """Authenticate with the API and fetch data."""
        try:
            if self._session is None:
                async with aiohttp.ClientSession() as session:
                    return await self._authenticate_with_session(session)
            else:
                return await self._authenticate_with_session(self._session)
        except Exception as e:
            _LOGGER.error("Authentication failed: %s", e)
            return False

    async def _authenticate_with_session(self, session) -> bool:
        """Internal authentication logic."""
        try:
            async with async_timeout.timeout(10):
                payload = {
                    "username": self._username,
                    "password": self._password,
                    "token": ""
                }
                response = await session.post(
                    f"{self._base_url}/korisnik/prijava",
                    json=payload,
                    headers=self._headers,
                )
                if response.status == 200:
                    data = await response.json()
                    self._token = data.get("token")
                    self._user_data = HepUser.from_dict(data)
                    
                    # Capture cookies from the session cookie jar
                    # This is crucial because we might be using a temporary session
                    for cookie in session.cookie_jar:
                        self._cookies[cookie.key] = cookie.value
                    
                    return True
                else:
                    _LOGGER.error("Login failed with status: %s", response.status)
                    return False
        except Exception as e:
            _LOGGER.error("Error during authentication: %s", e)
            raise

    async def get_data(self) -> HepUser:
        """Fetch data from the API."""
        # In this API, login returns the data.
        if not self._user_data:
            if not await self.authenticate():
                raise Exception("Not authenticated")
        
        return self._user_data

    async def get_prices(self) -> HepPrices:
        """Fetch pricing data from the API."""
        if not self._user_data:
             if not await self.authenticate():
                raise Exception("Not authenticated")

        try:
            if self._session is None:
                async with aiohttp.ClientSession() as session:
                    return await self._get_prices_with_session(session)
            else:
                return await self._get_prices_with_session(self._session)
        except Exception as e:
            _LOGGER.error("Failed to fetch prices: %s", e)
            raise

    async def _get_prices_with_session(self, session) -> HepPrices:
        """Internal price fetch logic."""
        try:
            async with async_timeout.timeout(10):
                headers = self._headers.copy()
                if self._cookies:
                    cookie_str = "; ".join([f"{k}={v}" for k, v in self._cookies.items()])
                    headers["Cookie"] = cookie_str

                response = await session.get(
                    f"{self._base_url}/obracun/cjenik",
                    headers=headers
                )
                
                if response.status == 200:
                    data = await response.json()
                    return HepPrices.from_dict(data)
                else:
                    _LOGGER.error("Price fetch failed with status: %s", response.status)
                    return None
        except Exception as e:
             _LOGGER.error("Error fetching prices: %s", e)
             raise

    async def get_billing(self, kupac_id: int) -> HepBillingInfo:
        """Fetch billing data (promet) from the API."""
        if not self._user_data:
             if not await self.authenticate():
                raise Exception("Not authenticated")

        try:
            if self._session is None:
                async with aiohttp.ClientSession() as session:
                    return await self._get_billing_with_session(session, kupac_id)
            else:
                return await self._get_billing_with_session(self._session, kupac_id)
        except Exception as e:
            _LOGGER.error("Failed to fetch billing info: %s", e)
            raise

    async def _get_billing_with_session(self, session, kupac_id: int) -> HepBillingInfo:
        """Internal billing fetch logic."""
        try:
            async with async_timeout.timeout(10):
                headers = self._headers.copy()
                if self._cookies:
                    cookie_str = "; ".join([f"{k}={v}" for k, v in self._cookies.items()])
                    headers["Cookie"] = cookie_str

                response = await session.get(
                    f"{self._base_url}/promet/{kupac_id}",
                    headers=headers
                )
                
                if response.status == 200:
                    data = await response.json()
                    return HepBillingInfo.from_dict(data)
                else:
                    _LOGGER.error("Billing fetch failed with status: %s", response.status)
                    return None
        except Exception as e:
             _LOGGER.error("Error fetching billing info: %s", e)
             raise
    async def get_consumption(self, kupac_id: int) -> List[HepConsumption]:
        """Fetch consumption data (potrosnja) from the API."""
        if not self._user_data:
             if not await self.authenticate():
                raise Exception("Not authenticated")

        try:
            if self._session is None:
                async with aiohttp.ClientSession() as session:
                    return await self._get_consumption_with_session(session, kupac_id)
            else:
                return await self._get_consumption_with_session(self._session, kupac_id)
        except Exception as e:
            _LOGGER.error("Failed to fetch consumption info: %s", e)
            raise

    async def _get_consumption_with_session(self, session, kupac_id: int) -> List[HepConsumption]:
        """Internal consumption fetch logic."""
        try:
            async with async_timeout.timeout(10):
                headers = self._headers.copy()
                if self._cookies:
                    cookie_str = "; ".join([f"{k}={v}" for k, v in self._cookies.items()])
                    headers["Cookie"] = cookie_str

                response = await session.get(
                    f"{self._base_url}/potrosnja/{kupac_id}",
                    headers=headers
                )
                
                if response.status == 200:
                    data = await response.json()
                    return [HepConsumption.from_dict(item) for item in data]
                else:
                    _LOGGER.error("Consumption fetch failed with status: %s", response.status)
                    return []
        except Exception as e:
             _LOGGER.error("Error fetching consumption info: %s", e)
             raise

    async def get_warnings(self, kupac_id: int) -> List[HepWarning]:
        """Fetch warnings (opomene) from the API."""
        if not self._user_data:
             if not await self.authenticate():
                raise Exception("Not authenticated")

        try:
            if self._session is None:
                async with aiohttp.ClientSession() as session:
                    return await self._get_warnings_with_session(session, kupac_id)
            else:
                return await self._get_warnings_with_session(self._session, kupac_id)
        except Exception as e:
            _LOGGER.error("Failed to fetch warnings: %s", e)
            raise

    async def _get_warnings_with_session(self, session, kupac_id: int) -> List[HepWarning]:
        """Internal warnings fetch logic."""
        try:
            async with async_timeout.timeout(10):
                headers = self._headers.copy()
                if self._cookies:
                    cookie_str = "; ".join([f"{k}={v}" for k, v in self._cookies.items()])
                    headers["Cookie"] = cookie_str

                response = await session.get(
                    f"{self._base_url}/opomene/{kupac_id}",
                    headers=headers
                )
                
                if response.status == 200:
                    data = await response.json()
                    return [HepWarning.from_dict(item) for item in data]
                else:
                    _LOGGER.error("Warnings fetch failed with status: %s", response.status)
                    return []
        except Exception as e:
             _LOGGER.error("Error fetching warnings: %s", e)
             raise

class HepOmmClient:
    """HEP OMM Client."""

    def __init__(self, omm_id, session):
        """Initialize the OMM client."""
        self._omm_id = omm_id
        self._session = session
        self._cookies = {}
        self._base_url = "https://mojamreza.hep.hr"
        self._headers = {
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Host": self._base_url.replace("https://", "").replace("http://", ""),
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Chromium";v="142", "Wavebox";v="142", "Not_A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "macOS"
        }
        self._check_form_token = ""
        self._delivery_form_token = ""

    async def initialize_session(self):
        """Initialize session by visiting the Dostava page to get cookies."""
        try:
            url = f"{self._base_url}/Dostava/{self._omm_id}"

            headers = self._headers.copy()
            headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
            headers["Sec-Fetch-Dest"] = "document"
            headers["Sec-Fetch-Mode"] = "navigate"
            headers["Sec-Fetch-Site"] = "cross-site"
            headers["Upgrade-Insecure-Requests"] = "1"

            async with self._session.get(url, headers=headers) as response:
                if response.status == 200:
                    text = await response.text()
                    
                    set_cookies = response.headers.getall("Set-Cookie", [])
                    for cookie_str in set_cookies:
                        cookie_parts = cookie_str.split(';')[0]
                        if '=' in cookie_parts:
                            key, value = cookie_parts.split('=', 1)
                            self._cookies[key.strip()] = value.strip()
                    
                    self._headers["Cookie"] = "; ".join([f"{k}={v}" for k, v in self._cookies.items()])
                    
                    check_match = re.search(r'id="Provjera_Omm_Form_Div".*?name="__RequestVerificationToken" type="hidden" value="([^"]+)"', text, re.DOTALL)
                    if check_match:
                        self._check_form_token = check_match.group(1)
                    
                    delivery_match = re.search(r'id="Dostava_Omm_Div".*?name="__RequestVerificationToken" type="hidden" value="([^"]+)"', text, re.DOTALL)
                    if delivery_match:
                        self._delivery_form_token = delivery_match.group(1)
                        
                    return True
                else:
                    _LOGGER.error("Failed to initialize OMM session: %s", response.status)
                    return False
        except Exception as e:
            _LOGGER.error("Error initializing OMM session: %s", e)
            return False

    async def check_omm(self) -> HepOmmCheck:
        """OMM check logic."""
        try:
            async with async_timeout.timeout(10):
                url = f"{self._base_url}/Omm/Provjera_Omm"
                
                headers = self._headers.copy()
                headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
                headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
                headers["Origin"] = self._base_url
                headers["Referer"] = f"{self._base_url}//Dostava/{self._omm_id}"
                headers["Sec-Fetch-Dest"] = "empty"
                headers["Sec-Fetch-Mode"] = "cors"
                headers["Sec-Fetch-Site"] = "same-origin"
                headers["X-Requested-With"] = "XMLHttpRequest"
                
                payload = {
                    "AntiSpamVM.EventField": "true",
                    "AntiSpamVM.Gd_check": "",
                    "AntiSpamVM.IsBot": "false",
                    "AntiSpamVM.Time": "100",
                    "AntiSpamVM.FormCreated": f"{time.time():.3f}",
                    "__RequestVerificationToken": self._check_form_token,
                    "Provjera_OmmVM.Omm": self._omm_id,
                }
                
                response = await self._session.post(
                    url,
                    data=payload,
                    headers=headers
                )
                
                if response.status == 200:
                    data = await response.json()
                    _LOGGER.debug("OMM check response: %s", data)
                    return HepOmmCheckResult.from_dict(data)
                else:
                    _LOGGER.error("OMM check failed with status: %s", response.status)
                    return None
        except Exception as e:
             _LOGGER.error("Error checking OMM: %s", e)
             raise

    async def submit_reading(self, enc_value: str, reading_date: str, tarifa1: int, tarifa2: int, force_send: bool = False) -> HepReadingSubmissionResult:
        """Submit reading logic."""
        try:
            async with async_timeout.timeout(10):
                url = f"{self._base_url}/Omm/Dostava"
                
                headers = self._headers.copy()
                headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
                headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
                headers["Origin"] = self._base_url
                headers["Referer"] = f"{self._base_url}//Dostava/{self._omm_id}"
                headers["Sec-Fetch-Dest"] = "empty"
                headers["Sec-Fetch-Mode"] = "cors"
                headers["Sec-Fetch-Site"] = "same-origin"
                headers["X-Requested-With"] = "XMLHttpRequest"
                
                payload = {
                    "AntiSpamVM.EventField": "true",
                    "AntiSpamVM.Gd_check": "",
                    "AntiSpamVM.IsBot": "false",
                    "AntiSpamVM.Time": "100",
                    "AntiSpamVM.FormCreated": f"{time.time():.3f}",
                    "__RequestVerificationToken": self._delivery_form_token,
                    "DostavaVM.Omm": self._omm_id,
                    "encValue": enc_value,
                    "DostavaVM.Posalji": str(1 if force_send else 0),
                    "DostavaVM.Datum_Ocitanja": reading_date,
                    "DostavaVM.Tarifa1": str(tarifa1),
                    "DostavaVM.Tarifa2": str(tarifa2)
                }
                
                response = await self._session.post(
                    url,
                    data=payload,
                    headers=headers
                )
                
                if response.status == 200:
                    data = await response.json()
                    return HepReadingSubmissionResult.from_dict(data)
                else:
                    _LOGGER.error("Reading submission failed with status: %s", response.status)
                    return None
        except Exception as e:
             _LOGGER.error("Error submitting reading: %s", e)
             raise
