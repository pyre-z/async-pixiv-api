from pixiv.app.model import (
    UserSearchResult,
    SearchSortParam,
    SearchDurationParam,
    SearchTargetParam,
)
from typing import TYPE_CHECKING, Iterable
import datetime
from pixiv.app.api.base import PixivAPIBase

if TYPE_CHECKING:
    from pixiv.app import PixivAPPClient  # noqa: F401

__all__ = ("PixivUserAPI",)


class PixivUserAPI(PixivAPIBase):
    async def search(
        self,
        word: str | Iterable[str],
        sort: SearchSortParam | None = None,
        duration: SearchDurationParam | None = None,
        target: SearchTargetParam | None = None,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
        offset: int | None = None,
        **kwargs,
    ) -> UserSearchResult:
        today = datetime.date.today()
        match duration:
            case SearchDurationParam.WithinLastDay:
                start_date = today - datetime.timedelta(days=1)
                end_date = today
            case SearchDurationParam.WithinLastWeek:
                start_date = today - datetime.timedelta(days=7)
                end_date = today
            case SearchDurationParam.WithinLastMonth:
                start_date = (
                    today.replace(month=today.month - 1)
                    if today.month > 1
                    else today.replace(year=today.year - 1, month=12)
                )
                end_date = today
        start_date_param = end_date_param = None
        if end_date is not None:
            end_date_param = end_date.strftime("%Y-%m-%d")
        if start_date is not None:
            start_date_param = start_date.strftime("%Y-%m-%d")
            end_date_param = end_date_param or today.strftime("%Y-%m-%d")

        return await super().search(
            word,
            sort=sort,
            target=target,
            start_date=start_date_param,
            end_date=end_date_param,
            offset=offset,
            **kwargs,
        )  # ty:ignore[invalid-return-type]
