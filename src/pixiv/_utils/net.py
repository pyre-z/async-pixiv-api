import asyncio
import re
import socket
from functools import lru_cache
from threading import RLock
from typing import Any

from aiohttp import ClientResponse as ClientResponse
from aiohttp import ClientSession, ClientTimeout
from aiohttp.abc import AbstractResolver, ResolveResult
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
    DEFAULT_ENDPOINTS: list[str] = [
        "https://cloudflare-dns.com/dns-query",
        "https://1.1.1.1/dns-query",
        "https://1.0.0.1/dns-query",
    ]

    # Hosts that should be resolved through DoH (circumventing ISP blocking)
    BYPASS_HOSTS: frozenset[str] = frozenset(
        {
            "app-api.pixiv.net",
            "public-api.secure.pixiv.net",
            "www.pixiv.net",
            "oauth.secure.pixiv.net",
        }
    )

    # Regex pattern for validating IPv4 addresses
    _IPV4_PATTERN = re.compile(
        r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})\.){3}"
        r"(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})$"
    )

    _lock: RLock = RLock()
    _session: ClientSession | None = None

    @property
    def session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            with self._lock:
                if self._session is None or self._session.closed:
                    self._session = ClientSession(
                        headers={"accept": "application/dns-json"},
                        json_serialize=json.dumps,
                    )
        return self._session

    def __init__(
        self,
        endpoints: list[str] | None = None,
        force_hosts: bool = True,
    ) -> None:
        self.endpoints: list[str] = (
            endpoints if endpoints is not None else self.DEFAULT_ENDPOINTS
        )
        self.force_hosts: bool = force_hosts

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} of {id(self):#x}"

    @lru_cache
    async def resolve(
        self,
        host: str,
        port: int = 0,
        family: socket.AddressFamily = socket.AF_INET,
    ) -> list[ResolveResult]:
        # Apply host mapping if needed (for bypassing censorship)
        resolved_host = self._map_host(host) if self.force_hosts else host

        # Launch parallel DNS queries to all endpoints
        tasks = {
            asyncio.create_task(self._resolve(endpoint, resolved_host, family))
            for endpoint in self.endpoints
        }

        # Wait for first successful response
        done, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED,
        )

        # Cancel remaining tasks and wait for cancellation to complete
        for task in pending:
            task.cancel()
        if pending:
            await asyncio.wait(
                pending, timeout=1.0
            )  # Give cancelled tasks time to clean up

        # Collect results from completed tasks
        ips = await self._collect_results(done)

        if not ips:
            raise OSError(f"DNS resolution failed for {host}")

        return [
            {
                "hostname": "",
                "host": ip,
                "port": port,
                "family": family,
                "proto": 0,
                "flags": socket.AI_NUMERICHOST,
            }
            for ip in ips
        ]

    async def _collect_results(self, tasks: set[asyncio.Task[list[str]]]) -> list[str]:
        """Collect successful DNS results from completed tasks."""
        errors: list[Exception] = []

        for task in tasks:
            try:
                result = await task
                if result:  # Only return non-empty results
                    return result
            except asyncio.CancelledError:
                break  # Task was canceled, skip
            except Exception as e:
                errors.append(e)

        # All tasks failed or returned empty
        if errors:
            # Raise the first error for debugging
            raise errors[0]
        return []

    def _map_host(self, host: str) -> str:
        """Map a host to its alternative domain if in bypass list."""
        if host in self.BYPASS_HOSTS:
            return "www.pixivision.net"
        return host

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()

    def parse_result(self, data: dict[str, Any]) -> list[str]:
        """Parse DoH JSON response and extract IP addresses."""
        if "Answer" not in data:
            return []

        return [
            record["data"]
            for record in data["Answer"]
            if self._is_valid_ip(record["data"])
        ]

    def _is_valid_ip(self, ip: str) -> bool:
        """Check if string is a valid IPv4 address."""
        return bool(self._IPV4_PATTERN.match(ip))

    async def _resolve(
        self,
        endpoint: str,
        hostname: str,
        family: socket.AddressFamily,
        timeout: float = 5.0,
    ) -> list[str]:
        """Perform DNS query against a single DoH endpoint."""
        params = {
            "name": hostname,
            "type": "AAAA" if family == socket.AF_INET6 else "A",
            "do": "false",
            "cd": "false",
        }

        async with self.session.get(
            endpoint,
            ssl=False,
            params=params,
            timeout=ClientTimeout(total=timeout),
        ) as response:
            if response.status != 200:
                raise OSError(
                    f"DoH query failed for {hostname} via {endpoint}: "
                    f"HTTP {response.status}"
                )

            data = await response.json(content_type="application/dns-json")
            if data.get("Status") != 0:
                raise OSError(
                    f"DoH query returned error status for {hostname}: "
                    f"{data.get('Status')}"
                )

            return self.parse_result(data)


class PixivClientSession(ClientSession):
    def __init__(
        self,
        *args,
        json_serialize=json.dumps,
        limiter: Limiter | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, json_serialize=json_serialize, **kwargs)
        self._limiter = limiter

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.closed}) of {id(self):#x}>"

    async def _request(self, *args, **kwargs) -> ClientResponse:
        if self._limiter is not None:
            await self._limiter.try_acquire_async("async-pixiv-api")
        return await super()._request(*args, **kwargs)
