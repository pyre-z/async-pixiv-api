import importlib
from abc import ABC
from collections.abc import Awaitable, Callable
from enum import Enum
from functools import lru_cache
from types import ModuleType
from typing import TYPE_CHECKING, Any, Iterable, TypedDict, TypeVar, cast

if TYPE_CHECKING:
    from pixiv._abc._client import PixivClient
    from pixiv.app.model import PixivBaseModel


__all__ = ("AbstractPixivAPIBase", "need_auth")


ClientType = TypeVar("ClientType", bound="PixivClient")


class PixivAPIPath(TypedDict):
    detail: str
    search: str
    recommended: str


@lru_cache
def _parse_value(value):
    if isinstance(value, Enum):
        return _parse_value(value.value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (str, int, float)):
        return str(value)
    if hasattr(value, "__iter__"):
        return " ".join(map(_parse_value, value))
    return str(value)


def need_auth[**P, R](method: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        self = cast("AbstractPixivAPIBase[PixivClient]", args[0])
        if not self.client.is_authed:
            raise RuntimeError("Not authenticated")
        return await method(*args, **kwargs)

    return wrapper


class AbstractPixivAPIBase[ClientType: "PixivClient"](ABC):
    type: str

    API_PATH: PixivAPIPath

    _client: ClientType

    @property
    def client(self) -> ClientType:
        return self._client

    def __init__(self, client: ClientType) -> None:
        self._client = client

    def __init_subclass__(cls, **_) -> None:
        cls.type = cls.__name__.removesuffix("API").removeprefix("Pixiv").lower()

    async def __call__(self, id: int | str) -> "PixivBaseModel":
        return await self.detail(id)

    def _model_module(self) -> ModuleType:
        return importlib.import_module(
            self.client.__class__.__module__.replace("client", "model")
        )

    @staticmethod
    def _build_params(**kwargs) -> dict[str, Any]:
        params = {}
        for name, value in kwargs.items():
            if value is None:
                continue
            params[name] = _parse_value(value)
        return params

    async def detail(self, id: int | str) -> "PixivBaseModel":
        url_path = self.API_PATH["detail"].format(id=id, type=self.type)
        response = await self.client.get(url_path)
        data = response.raise_for_data_and_status().json()
        cls: type["PixivBaseModel"] = getattr(
            self._model_module(), f"{self.type.title()}Detail"
        )
        return cls.model_validate(data)

    async def search(self, word: str | Iterable[str], **kwargs) -> "PixivBaseModel":
        word = word if isinstance(word, str) else " ".join(word)
        url_path = self.API_PATH["search"].format(type=self.type)
        response = await self.client.get(
            url_path, params=self._build_params(word=word, **kwargs)
        )
        data = response.raise_for_data_and_status().json()
        cls: type["PixivBaseModel"] = getattr(
            self._model_module(), f"{self.type.title()}SearchResult"
        )
        return cls.model_validate(data)

    @need_auth
    async def recommended(self, **kwargs) -> "PixivBaseModel":
        url_path = self.API_PATH["recommended"].format(type=self.type)
        response = await self.client.get(url_path, params=self._build_params(**kwargs))
        data = response.raise_for_data_and_status().json()
        cls: type["PixivBaseModel"] = getattr(
            self._model_module(), f"{self.type.title()}RecommendedResult"
        )
        return cls.model_validate(data)
