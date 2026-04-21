import ssl
from abc import ABC, abstractmethod
from threading import RLock
from typing import Any

from aiohttp import TCPConnector
from pyrate_limiter import Duration
from pyrate_limiter.limiter_factory import create_inmemory_limiter

from pixiv._abc._config import PixivSettings
from pixiv._utils.net import ByPassResolver, PixivClientSession

__all__ = ("PixivClient",)


class PixivClient(ABC):
    _lock: RLock = RLock()
    _session: PixivClientSession | None = None

    _settings: PixivSettings

    @property
    def session(self) -> PixivClientSession:
        if self._session is None:
            with self._lock:
                if self._session is None:
                    self._session = self._new_session()
        return self._session

    @property
    def settings(self) -> PixivSettings:
        return self._settings

    def _new_session(self) -> PixivClientSession:
        kwargs: dict[str, Any] = {}
        if self._settings.bypass:
            ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE

            kwargs.update({"ssl": ssl_ctx, "resolver": ByPassResolver()})

        use_proxy = False
        if self._settings.proxy:
            try:
                from aiohttp_socks import ProxyConnector

                connector = ProxyConnector.from_url(self._settings.proxy, **kwargs)
            except ModuleNotFoundError as e:
                if self._settings.proxy.startswith("socks"):
                    raise e
                else:
                    connector = TCPConnector(**kwargs)
                    use_proxy = True
        else:
            connector = TCPConnector(**kwargs)

        return PixivClientSession(
            self._settings.api_host,
            limiter=create_inmemory_limiter(
                rate_per_duration=self._settings.rate_limit.max_rate or -1,
                duration=Duration.SECOND * self._settings.rate_limit.time_period,
            ),
            connector=connector,
            headers={
                "-".join(map(lambda s: s.title(), k.split("_"))): str(v)
                for k, v in self._settings.headers.model_dump().items()
                if v
            },
            proxy=self._settings.proxy if use_proxy and self._settings.proxy else None,
        )

    @abstractmethod
    async def auth(self):
        pass

    @abstractmethod
    async def set_auth(self, auth_content: str):
        pass