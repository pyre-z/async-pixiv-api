import datetime
from typing import TYPE_CHECKING, Iterable

from pixiv._abc._api import AbstractPixivAPIBase
from pixiv.app.model import (
    Duration,
    Sort,
    Target,
    UserDetail,
    UserRecommendedResult,
    UserSearchResult,
)

if TYPE_CHECKING:
    from pixiv.app import PixivAPPClient  # noqa: F401

__all__ = ("PixivUserAPI",)

class PixivUserAPI(AbstractPixivAPIBase["PixivAPPClient"]):
    API_PATH: dict[str, str]

    async def __call__(self, id: int | str) -> UserDetail: ...
    async def detail(self, id: int | str) -> UserDetail: ...
    async def search(
        self, word: str | Iterable[str], offset: int | None = None, **kwargs
    ) -> UserSearchResult: ...
    async def recommended(
        self, offset: int | None = None, **kwargs
    ) -> UserRecommendedResult: ...
