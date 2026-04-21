import asyncio
import socket
from functools import lru_cache
from threading import RLock
from typing import Any, Awaitable, Callable, Iterable, Pattern, Sequence

from aiohttp import (
    BaseConnector,
    BasicAuth,
    ClientRequest,
    ClientResponse,
    ClientSession,
    ClientTimeout,
    ClientWebSocketResponse,
    HttpVersion,
    HttpVersion11,
    TraceConfig,
)
from aiohttp.abc import AbstractCookieJar, AbstractResolver, ResolveResult
from aiohttp.client_middlewares import ClientMiddlewareType
from aiohttp.helpers import _SENTINEL, sentinel
from aiohttp.typedefs import JSONEncoder, LooseCookies, LooseHeaders, StrOrURL
from pyrate_limiter import Limiter

try:
    import ujson as json  # ty:ignore[unresolved-import]
except ImportError:
    import json

__all__ = (
    "PixivClientSession",
    "ByPassResolver",
)

class ByPassResolver(AbstractResolver):
    """DNS-over-HTTPS (DoH) resolver for bypassing censorship.

    Uses Cloudflare/Google public DoH endpoints to resolve DNS queries,
    with support for forcing certain hosts through the resolver.
    """

    # Public DoH endpoints (Cloudflare primary, with fallbacks)
    DEFAULT_ENDPOINTS: list[str]

    # Hosts that should be resolved through DoH (circumventing ISP blocking)
    BYPASS_HOSTS: frozenset[str]

    # Regex pattern for validating IPv4 addresses
    _IPV4_PATTERN: Pattern[str]

    _lock: RLock
    _session: ClientSession | None

    @property
    def session(self) -> ClientSession: ...

    endpoints: list[str]
    force_hosts: bool

    def __init__(
        self,
        endpoints: list[str] | None = None,
        force_hosts: bool = True,
    ) -> None: ...
    def __repr__(self) -> str: ...
    @lru_cache
    async def resolve(
        self,
        host: str,
        port: int = 0,
        family: socket.AddressFamily = socket.AF_INET,
    ) -> list[ResolveResult]: ...
    async def _collect_results(
        self, tasks: set[asyncio.Task[list[str]]]
    ) -> list[str]: ...
    def _map_host(self, host: str) -> str: ...
    async def close(self) -> None: ...
    def parse_result(self, data: dict[str, Any]) -> list[str]: ...
    def _is_valid_ip(self, ip: str) -> bool: ...
    async def _resolve(
        self,
        endpoint: str,
        hostname: str,
        family: socket.AddressFamily,
        timeout: float = 5.0,
    ) -> list[str]: ...

class PixivClientSession(ClientSession):
    # noinspection PyTypeHints
    def __init__(
        self,
        base_url: StrOrURL | None = None,
        *,
        limiter: Limiter | None = None,
        connector: BaseConnector | None = None,
        loop: asyncio.AbstractEventLoop | None = None,
        cookies: LooseCookies | None = None,
        headers: LooseHeaders | None = None,
        proxy: StrOrURL | None = None,
        proxy_auth: BasicAuth | None = None,
        skip_auto_headers: Iterable[str] | None = None,
        auth: BasicAuth | None = None,
        json_serialize: JSONEncoder = json.dumps,
        request_class: type[ClientRequest] = ClientRequest,
        response_class: type[ClientResponse] = ClientResponse,
        ws_response_class: type[ClientWebSocketResponse] = ClientWebSocketResponse,
        version: HttpVersion = HttpVersion11,
        cookie_jar: AbstractCookieJar | None = None,
        connector_owner: bool = True,
        raise_for_status: bool | Callable[[ClientResponse], Awaitable[None]] = False,
        read_timeout: float | _SENTINEL = sentinel,
        conn_timeout: float | None = None,
        timeout: ClientTimeout | Any = sentinel,
        auto_decompress: bool = True,
        trust_env: bool = False,
        requote_redirect_url: bool = True,
        trace_configs: list[TraceConfig] | None = None,
        read_bufsize: int = 2**16,
        max_line_size: int = 8190,
        max_field_size: int = 8190,
        max_headers: int = 128,
        fallback_charset_resolver: Callable[
            [ClientResponse, bytes], str
        ] = lambda r, b: "utf-8",
        middlewares: Sequence[ClientMiddlewareType] = (),
        ssl_shutdown_timeout: _SENTINEL | float | None = sentinel,
    ) -> None: ...
    def __repr__(self) -> str: ...
