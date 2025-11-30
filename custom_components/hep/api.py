"""API Client for HEP."""
import logging
import aiohttp
import async_timeout
from typing import List
import re
from .models import HepUser, HepPrices, HepBillingInfo, HepConsumption, HepWarning, HepOmmCheck, HepReadingSubmissionResult

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
        # Real HEP API URL
        self._base_url = "https://mojracun.hep.hr/elektra/v1/api"
        self._mojamreza_url = "https://mojamreza.hep.hr"
        # For local testing, we might want to override this.
        # Ideally, we'd pass this in or have a way to configure it.
        # But for now, let's stick to the real one as default, and test_local can patch it or we can add a kwarg.
        self._headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        }

    def set_base_url(self, url):
        """Set base URL (for testing)."""
        self._base_url = url

    def set_mojamreza_url(self, url):
        """Set Moja Mreza URL (for testing)."""
        self._mojamreza_url = url


# We aren't setting Cookie header with these values and accessToken is one of them: 

# _ga_EV31QJNEL6=GS2.2.s1762104619$o2$g0$t1762104619$j60$l0$h0; _ga_6BQVKC4H63=GS2.2.s1762104619$o2$g0$t1762104619$j60$l0$h0; _ga=GA1.1.554793247.1762102536; _ga_DLRESD84RV=GS2.1.s1764433944$o1$g1$t1764434506$j60$l0$h0; accessToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJib2phbi5rb21samVub3ZpY0BnbWFpbC5jb20iLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1lIjoiYm9qYW4ua29tbGplbm92aWNAZ21haWwuY29tIiwiaWQiOiI5MDI3MTE0MyIsImp0aSI6ImRhYjVmZGM5LTEwNGMtNGMzNi05ZDk5LWRlNzI0Y2VjMDRmNSIsImV4cCI6MTc2NDQ0NDc4MCwiaXNzIjoibW9qcmFjdW4uaGVwLmhyIiwiYXVkIjoidXNlcnMifQ.RJdjS8on2uHp8gEEsRfdBF8V60esMi4PDhuofF3V3EY; TS0132729f=01e51bd9b2d61f4a1478d4db188bcd993d94a32a204fd67b62140c6b984616a6294eb51168f2c4839a1b139913bce2a493de7831a10e39bfad96ba57af137bfb1d61799cd2

# Authentication sets that token exatly in response headers set-cookie twice with different values.

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
                    _LOGGER.debug(f"Raw login response: {data}")
                    self._token = data.get("token")
                    self._user_data = HepUser.from_dict(data)
                    
                    # Capture cookies from the session cookie jar
                    # This is crucial because we might be using a temporary session
                    for cookie in session.cookie_jar:
                        self._cookies[cookie.key] = cookie.value
                    
                    _LOGGER.debug(f"Captured cookies: {self._cookies.keys()}")
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

    async def _get_omm_tokens(self, omm: str):
        """Fetch OMM page to extract tokens."""
        try:
            url = f"{self._mojamreza_url}/Dostava/{omm}"
            async with self._session.get(url) as response:
                if response.status == 200:
                    text = await response.text()
                    # Extract form token
                    match = re.search(r'name="__RequestVerificationToken" type="hidden" value="([^"]+)"', text)
                    form_token = match.group(1) if match else None
                    
                    # Extract session ID and cookie token from jar
                    session_id = None
                    cookie_token = None
                    for cookie in self._session.cookie_jar:
                        if cookie.key == "ASP.NET_SessionId":
                            session_id = cookie.value
                        elif cookie.key == "__RequestVerificationToken":
                            cookie_token = cookie.value
                            
                    return session_id, cookie_token, form_token
                else:
                    _LOGGER.error("Failed to fetch OMM page: %s", response.status)
                    return None, None, None
        except Exception as e:
            _LOGGER.error("Error fetching OMM tokens: %s", e)
            return None, None, None

    async def check_omm(self, omm: str, session_id: str = None, cookie_token: str = None, form_token: str = None) -> HepOmmCheck:
        """
        Check OMM status (Provjera_Omm).
        If tokens are not provided, attempts to fetch them automatically.
        """
        try:
            if self._session is None:
                async with aiohttp.ClientSession() as session:
                    # We can't easily auto-fetch with a fresh session as we lose context
                    # But for consistency we can try if user provided nothing
                    if not session_id or not form_token:
                         # This path is unlikely to work for OMM if auth is needed
                         pass
                    return await self._check_omm_with_session(session, omm, session_id, cookie_token, form_token)
            else:
                # Auto-fetch tokens if missing
                if not session_id or not form_token:
                    fetched_session, fetched_cookie, fetched_form = await self._get_omm_tokens(omm)
                    if fetched_form:
                        form_token = fetched_form
                        # If we found session cookies, use them. If not, use what we have (maybe None)
                        if fetched_session: session_id = fetched_session
                        if fetched_cookie: cookie_token = fetched_cookie
                
                return await self._check_omm_with_session(self._session, omm, session_id, cookie_token, form_token)
        except Exception as e:
            _LOGGER.error("Failed to check OMM: %s", e)
            raise

    async def _check_omm_with_session(self, session, omm: str, session_id: str, cookie_token: str, form_token: str) -> HepOmmCheck:
        """Internal OMM check logic."""
        try:
            async with async_timeout.timeout(10):
                url = f"{self._mojamreza_url}/Omm/Provjera_Omm"
                
                headers = {
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Origin": self._mojamreza_url,
                    "Referer": f"{self._mojamreza_url}//Dostava/{omm}",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
                    "X-Requested-With": "XMLHttpRequest"
                }
                
                # Add Cookie header if we have tokens
                cookies_list = []
                if session_id:
                    cookies_list.append(f"ASP.NET_SessionId={session_id}")
                if cookie_token:
                    cookies_list.append(f"__RequestVerificationToken={cookie_token}")
                
                if cookies_list:
                    headers["Cookie"] = "; ".join(cookies_list)
                
                payload = {
                    "AntiSpamVM.EventField": "true",
                    "AntiSpamVM.Gd_check": "",
                    "AntiSpamVM.IsBot": "false",
                    "AntiSpamVM.Time": "100",
                    "__RequestVerificationToken": form_token if form_token else "",
                    "Provjera_OmmVM.Omm": omm
                }
                
                response = await session.post(
                    url,
                    data=payload,
                    headers=headers
                )
                
                if response.status == 200:
                    data = await response.json()
                    # The response structure has "Provjera_OmmDto" key
                    dto = data.get("Provjera_OmmDto", {})
                    return HepOmmCheck.from_dict(dto)
                else:
                    _LOGGER.error("OMM check failed with status: %s", response.status)
                    return None
        except Exception as e:
             _LOGGER.error("Error checking OMM: %s", e)
             raise

    async def submit_reading(self, omm: str, session_id: str, cookie_token: str, form_token: str, enc_value: str, date: str, tarifa1: int, tarifa2: int, posalji: int = 0) -> HepReadingSubmissionResult:
        """
        Submit meter reading (Dostava).
        Requires tokens and encValue from check_omm.
        """
        try:
            if self._session is None:
                async with aiohttp.ClientSession() as session:
                    return await self._submit_reading_with_session(session, omm, session_id, cookie_token, form_token, enc_value, date, tarifa1, tarifa2, posalji)
            else:
                return await self._submit_reading_with_session(self._session, omm, session_id, cookie_token, form_token, enc_value, date, tarifa1, tarifa2, posalji)
        except Exception as e:
            _LOGGER.error("Failed to submit reading: %s", e)
            raise

    async def _submit_reading_with_session(self, session, omm: str, session_id: str, cookie_token: str, form_token: str, enc_value: str, date: str, tarifa1: int, tarifa2: int, posalji: int) -> HepReadingSubmissionResult:
        """Internal reading submission logic."""
        try:
            async with async_timeout.timeout(10):
                url = f"{self._mojamreza_url}/Omm/Dostava"
                
                headers = {
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Origin": self._mojamreza_url,
                    "Referer": f"{self._mojamreza_url}//Dostava/{omm}",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
                    "X-Requested-With": "XMLHttpRequest",
                    "Cookie": f"ASP.NET_SessionId={session_id}; __RequestVerificationToken={cookie_token}"
                }
                
                payload = {
                    "AntiSpamVM.EventField": "true",
                    "AntiSpamVM.Gd_check": "",
                    "AntiSpamVM.IsBot": "false",
                    "AntiSpamVM.Time": "100",
                    "__RequestVerificationToken": form_token,
                    "DostavaVM.Omm": omm,
                    "encValue": enc_value,
                    "DostavaVM.Posalji": str(posalji),
                    "DostavaVM.Datum_Ocitanja": date,
                    "DostavaVM.Tarifa1": str(tarifa1),
                    "DostavaVM.Tarifa2": str(tarifa2)
                }
                
                response = await session.post(
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
