import datetime
from typing import TYPE_CHECKING, Iterable, cast

from pixiv.app.api.base import PixivAPIBase
from pixiv.app.model import (
    Duration,
    Sort,
    Target,
    UserSearchResult,
)

if TYPE_CHECKING:
    from pixiv.app import PixivAPPClient  # noqa: F401

__all__ = ("PixivUserAPI",)


class PixivUserAPI(PixivAPIBase):
    async def search(
        self, word: str | Iterable[str], offset: int | None = None, **kwargs
    ) -> UserSearchResult:
        return cast(
            UserSearchResult, await super().search(word, offset=offset, **kwargs)
        )
