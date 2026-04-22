import asyncio
import logging
import re
import ssl
from functools import lru_cache
from threading import RLock
from typing import Any, Iterable, Self

from aiocache import cached
from httpx import (
    USE_CLIENT_DEFAULT,
    AsyncBaseTransport,
    AsyncClient,
    AsyncHTTPTransport,
    HTTPStatusError,
    Limits,
    Proxy,
    Request,
    Response,
)
from httpx._client import UseClientDefault
from httpx._config import DEFAULT_LIMITS
from httpx._transports.default import SOCKET_OPTION
from httpx._types import AuthTypes, CertTypes, ProxyTypes
from pyrate_limiter import Limiter

from pixiv.exceptions import PixivError

try:
    import ujson as json
except ImportError:
    import json

__all__ = ("PixivRequestClient", "ClientResponse")

logger = logging.getLogger(__name__)


class AsyncByPassHTTPTransport(AsyncHTTPTransport):
    # Public DoH endpoints (Cloudflare primary, with fallbacks)
    DEFAULT_ENDPOINTS = [
        "https://cloudflare-dns.com/dns-query",
        "https://1.1.1.1/dns-query",
        "https://1.0.0.1/dns-query",
        "https://[2606:4700:4700::1001]/dns-query",
        "https://[2606:4700:4700::1111]/dns-query",
    ]

    # Hosts that should be resolved through DoH (circumventing ISP blocking)
    BYPASS_HOSTS = frozenset(
        {
            "app-api.pixiv.net",
            "public-api.secure.pixiv.net",
            "www.pixiv.net",
            "oauth.secure.pixiv.net",
        },
    )

    # Regex pattern for validating IPv4 addresses
    _IPV4_PATTERN = re.compile(
        r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})\.){3}"
        r"(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})$"
    )

    _lock: RLock = RLock()
    _request_client: "PixivRequestClient | None" = None
    _proxy: ProxyTypes | None = None

    @property
    def request_client(self) -> "PixivRequestClient":
        if self._request_client is None:
            with self._lock:
                if self._request_client is None:
                    self._request_client = PixivRequestClient(
                        headers={"accept": "application/dns-json"},
                        proxy=self._proxy,
                    )
        return self._request_client

    # noinspection PyUnusedLocal
    def __init__(
        self,
        verify: ssl.SSLContext | str | bool = True,
        cert: CertTypes | None = None,
        trust_env: bool = True,
        http1: bool = True,
        http2: bool = False,
        limits: Limits = DEFAULT_LIMITS,
        proxy: ProxyTypes | None = None,
        uds: str | None = None,
        local_address: str | None = None,
        retries: int = 0,
        socket_options: Iterable[SOCKET_OPTION] | None = None,
        endpoints: list[str] | None = None,
        force_hosts: bool = False,
    ) -> None:
        # Disable cert verification for bypass mode (SNI mismatch issue with DoH IPs)
        # We only do DoH resolution when not using a proxy to avoid SNI issues
        super().__init__(
            False,
            cert,
            trust_env,
            http1,
            http2,
            limits,
            proxy,
            uds,
            local_address,
            retries,
            socket_options,
        )
        self._proxy = proxy
        self.endpoints = endpoints or self.DEFAULT_ENDPOINTS
        self.force_hosts = force_hosts

    async def query_endpoint(self, endpoint: str, host: str) -> str | None:
        """Query DoH endpoints in parallel, first successful result wins"""
        try:
            # Build DoH URL with query parameters
            url = f"{endpoint}?name={host}&type=A"
            response = await self.request_client.get(url)
            response.raise_for_status()
            data = response.json()

            # Parse dns-json response format
            # Response schema: {"Status": 0, "Answer": [{"data": "1.2.3.4", ...}]}
            if data.get("Status") != 0:
                return None  # DNS query failed (NXDOMAIN, SERVFAIL, etc.)

            answers = data.get("Answer", [])
            for answer in answers:
                ip = answer.get("data", "")
                if self._IPV4_PATTERN.match(ip):
                    return ip
            return None
        except Exception:
            return None

    async def read_result(self, tasks: set[asyncio.Task]) -> list[str]:
        result = []
        if len(tasks) == 0:
            return result

        task = tasks.pop()
        try:
            await task
            result.append(task.result())
        except Exception as e:
            logger.warning("caught:", repr(e))
            result.extend(await self.read_result(tasks))
        return result

    @cached(30)
    async def resolve(self, host: str) -> str | None:
        """
        Resolve hostname via DNS-over-HTTPS (DoH) using configured endpoints.

        Only resolves hosts in BYPASS_HOSTS or when force_hosts is True.
        Returns IPv4 address if resolution succeeds, None otherwise.
        """
        # Skip DoH when using proxy: proxy handles DNS, and avoids SNI issues
        if self._proxy is not None:
            return None

        # Skip resolution for non-bypass hosts unless force_hosts is enabled
        if host not in self.BYPASS_HOSTS and not self.force_hosts:
            return None

        # Try all endpoints concurrently, return first valid result
        done, pending = await asyncio.wait(
            [
                asyncio.create_task(self.query_endpoint(ep, host))
                for ep in self.endpoints
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )
        results = await self.read_result(done.union(pending))
        for task in pending:
            task.cancel()

        for result in results:
            if isinstance(result, str) and result:
                return result

        return None

    async def handle_async_request(self, request: Request) -> ClientResponse:
        host = request.url.host
        ip = await self.resolve(host)
        if ip is not None:
            # Replace URL host with resolved IP for socket connection
            request.url = request.url.copy_with(host=ip)
            # Keep Host header as original hostname for proper virtual hosting
            request.headers.setdefault("Host", host)
        return ClientResponse.from_httpx_response(
            await super().handle_async_request(request)
        )


class ClientResponse(Response):
    _lock: RLock = RLock()

    @classmethod
    def from_httpx_response(cls, response: Response) -> Self:
        """
        Convert a httpx Response to our custom Response subclass.

        This preserves all response data including status code, headers, content,
        cookies, history, etc.
        """
        # Create new instance and copy all attributes via __dict__
        self = cls.__new__(cls)
        self.__dict__.update(response.__dict__)
        return self

    @lru_cache(maxsize=4)
    def json(self, **kwargs: Any) -> Any:
        """Parse response body as JSON, using ujson if available."""
        return json.loads(self.text, **kwargs)

    def raise_for_status(self) -> Self:
        request = self._request
        if request is None:
            raise RuntimeError(
                "Cannot call `raise_for_status` as the request "
                "instance has not been set on this response."
            )

        if self.is_success:
            return self

        if self.has_redirect_location:
            message = (
                "{error_type} '{0.status_code} {0.reason_phrase}' for url '{0.url}'\n"
                "Redirect location: '{0.headers[location]}'\n"
                "For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/{0.status_code}"
            )
        else:
            message = (
                "{error_type} '{0.status_code} {0.reason_phrase}' for url '{0.url}'\n"
                "For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/{0.status_code}"
            )

        status_class = self.status_code // 100
        error_types = {
            1: "Informational response",
            3: "Redirect response",
            4: "Client error",
            5: "Server error",
        }
        error_type = error_types.get(status_class, "Invalid status code")
        message = message.format(self, error_type=error_type)
        raise HTTPStatusError(message, request=request, response=self)

    def raise_for_data(self) -> Self:
        response_data: dict[str, Any] = self.json()
        if response_data.get("error", {}):
            raise PixivError(response_data["error"]["message"])
        return self


class PixivRequestClient(AsyncClient):
    def __init__(
        self,
        *,
        bypass: bool = False,
        rate_limiter: Limiter | None = None,
        verify: ssl.SSLContext | str | bool = True,
        **kwargs,
    ) -> None:
        self._bypass = bypass
        if bypass:
            verify = False
        super().__init__(verify=verify, **kwargs)
        self._rate_limiter = rate_limiter

    def _init_transport(
        self,
        verify: ssl.SSLContext | str | bool = True,
        cert: CertTypes | None = None,
        trust_env: bool = True,
        http1: bool = True,
        http2: bool = False,
        limits: Limits = DEFAULT_LIMITS,
        transport: AsyncBaseTransport | None = None,
    ) -> AsyncBaseTransport:
        if transport is not None:
            return transport

        return (AsyncByPassHTTPTransport if self._bypass else AsyncHTTPTransport)(
            verify=verify,
            cert=cert,
            trust_env=trust_env,
            http1=http1,
            http2=http2,
            limits=limits,
        )

    def _init_proxy_transport(
        self,
        proxy: Proxy,
        verify: ssl.SSLContext | str | bool = True,
        cert: CertTypes | None = None,
        trust_env: bool = True,
        http1: bool = True,
        http2: bool = False,
        limits: Limits = DEFAULT_LIMITS,
    ) -> AsyncBaseTransport:
        return (AsyncByPassHTTPTransport if self._bypass else AsyncHTTPTransport)(
            verify=verify,
            cert=cert,
            trust_env=trust_env,
            http1=http1,
            http2=http2,
            limits=limits,
            proxy=proxy,
        )

    async def send(
        self,
        request: Request,
        *,
        stream: bool = False,
        auth: AuthTypes | UseClientDefault | None = USE_CLIENT_DEFAULT,
        follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
    ) -> ClientResponse:
        if self._rate_limiter is not None:
            await self._rate_limiter.try_acquire_async("async-pixiv-api")
        return ClientResponse.from_httpx_response(
            await super().send(
                request,
                stream=stream,
                auth=auth,
                follow_redirects=follow_redirects,
            )
        )

    async def request(self, *args, **kwargs) -> ClientResponse:
        return ClientResponse.from_httpx_response(
            await super().request(*args, **kwargs)
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}{'(closed)' if self.is_closed else ''} of {id(self):#x}>"
