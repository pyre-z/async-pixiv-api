import datetime
from typing import Iterable

from pixiv.app.api.base import PixivAPIBase
from pixiv.app.model.illust import (
    IllustDetail,
    IllustRecommendedResult,
    IllustSearchResult,
)
from pixiv.app.model.param import ContentType, Duration, Sort, Target

__all__ = ("PixivIllustAPI",)

class PixivIllustAPI(PixivAPIBase):
    async def __call__(self, id: int | str) -> IllustDetail: ...
    async def detail(self, id: int | str) -> IllustDetail: ...
    async def search(
        self,
        word: str | Iterable[str],
        target: Target | None = None,
        sort: Sort | None = None,
        duration: Duration | None = None,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
        filter_ai: bool | None = None,
        offset: int | None = None,
        **kwargs,
    ) -> IllustSearchResult: ...

    async def recommended(
        self,
        content_type: ContentType = ContentType.Illust,
        include_ranking_label: bool | None = None,
        max_bookmark_id_for_recommend: int | str | None = None,
        min_bookmark_id_for_recent_illust: int | str | None = None,
        offset: int | None = None,
        include_ranking_illusts: str | bool | None = None,
        bookmark_illust_ids: str | list[int | str] | None = None,
        include_privacy_policy: str | list[int | str] | None = None,
        viewed: str | list[str] | None = None,
        **kwargs,
    ) -> IllustRecommendedResult: ...
