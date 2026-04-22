import ssl
from abc import ABC, abstractmethod
from contextvars import ContextVar, Token
from threading import RLock
from typing import Any

from aiohttp import TCPConnector
from httpx import AsyncClient
from pyrate_limiter import Duration
from pyrate_limiter.limiter_factory import create_inmemory_limiter

from pixiv._abc._config import PixivSettings
from pixiv._utils.net import PixivRequestClient

__all__ = ("PixivClient",)

PixivClientContextVar: ContextVar["PixivClient"] = ContextVar("PixivClient")
PixivClientContextToken: Token["PixivClient"] | None = None


class PixivClient(ABC):
    _lock: RLock = RLock()
    _request_client: PixivRequestClient | None = None
    _settings: PixivSettings | None = None

    @property
    def request_client(self) -> PixivRequestClient:
        if self._request_client is None:
            with self._lock:
                if self._request_client is None:
                    self._request_client = self._new_request_client()
        return self._request_client

    @property
    def settings(self) -> PixivSettings:
        if self._settings is None:
            with self._lock:
                if self._settings is None:
                    raise RuntimeError("Settings not set")
        return self._settings

    @property
    @abstractmethod
    def is_authed(self) -> bool: ...

    def __init__(self) -> None:
        global PixivClientContextToken
        with self._lock:
            PixivClientContextToken = PixivClientContextVar.set(self)

    def __delete__(self) -> None:
        if PixivClientContextToken is not None:
            with self._lock:
                if PixivClientContextToken is not None:
                    PixivClientContextVar.reset(PixivClientContextToken)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({'' if self.is_authed else 'not '}authed) of {id(self):#x}>"

    def _new_request_client(self) -> PixivRequestClient:
        return PixivRequestClient(
            base_url=self.settings.api_host,
            rate_limiter=create_inmemory_limiter(
                rate_per_duration=self.settings.rate_limit.max_rate or -1,
                duration=Duration.SECOND * self.settings.rate_limit.time_period,
            ),
            headers={
                "-".join(map(lambda s: s.title(), k.split("_"))): str(v)
                for k, v in self.settings.headers.model_dump().items()
                if v
            },
            proxy=self.settings.proxy,
            bypass=self.settings.bypass,
        )

    @abstractmethod
    async def auth(self):
        pass

    @abstractmethod
    async def set_auth(self, auth_content):
        pass
