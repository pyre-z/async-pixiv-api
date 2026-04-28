import importlib
from abc import ABC
from enum import Enum
from types import ModuleType
from typing import TYPE_CHECKING, Iterable, TypedDict

if TYPE_CHECKING:
    from pixiv._abc._client import PixivClient
    from pixiv.app.model import PixivBaseModel


__all__ = ("AbstractPixivAPIBase",)


class PixivAPIPath(TypedDict):
    detail: str
    search: str
    recommended: str


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

    async def detail(self, id: int | str) -> "PixivBaseModel":
        url_path = self.API_PATH["detail"].format(id=id, type=self.type)
        response = await self.client.get(url_path)
        data = response.raise_for_status().raise_for_data().json()
        detail_cls: type["PixivBaseModel"] = getattr(
            self._model_module(), f"{self.type.title()}Detail"
        )
        return detail_cls.model_validate(data)

    async def search(self, word: str | Iterable[str], **kwargs) -> "PixivBaseModel":
        word = word if isinstance(word, str) else " ".join(word)
        url_path = self.API_PATH["search"].format(type=self.type)
        response = await self.client.get(
            url_path,
            params={
                k: (str(v) if isinstance(v, (int, Enum)) else v)
                for k, v in {"word": word, **kwargs}.items()
                if v is not None
            },
        )
        data = response.raise_for_status().raise_for_data().json()
        detail_cls: type["PixivBaseModel"] = getattr(
            self._model_module(), f"{self.type.title()}SearchResult"
        )
        return detail_cls.model_validate(data)

    async def recommended(self, **kwargs) -> "PixivBaseModel":
        url_path = self.API_PATH["recommended"].format(type=self.type)
        response = await self.client.get(
            url_path,
            params={
                k: (str(v) if isinstance(v, (int, Enum)) else v)
                for k, v in kwargs.items()
                if v is not None
            },
        )
        data = response.raise_for_status().raise_for_data().json()
        detail_cls: type["PixivBaseModel"] = getattr(
            self._model_module(), f"{self.type.title()}RecommendedResult"
        )
        return detail_cls.model_validate(data)
