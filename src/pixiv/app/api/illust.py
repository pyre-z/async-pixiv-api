import calendar
import datetime
from typing import Iterable, cast

from pixiv.app.api.base import PixivAPIBase
from pixiv.app.model.illust import IllustSearchResult
from pixiv.app.model.param import Duration, Sort, Target

__all__ = ("PixivIllustAPI",)


class PixivIllustAPI(PixivAPIBase):
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
    ) -> IllustSearchResult:
        today = datetime.date.today()
        match duration:
            case Duration.WithinLastDay:
                start_date = today - datetime.timedelta(days=1)
            case Duration.WithinLastWeek:
                start_date = today - datetime.timedelta(weeks=1)
            case Duration.WithinLastMonth:
                month = today.month
                if month == 1:
                    new_year = today.year - 1
                    new_month = 12
                else:
                    new_year = today.year
                    new_month = month - 1
                new_day = (
                    monthrange[1]
                    if (new_day := today.day)
                    > (monthrange := calendar.monthrange(new_year, new_month))[1]
                    else new_day
                )
                start_date = datetime.date(new_year, new_month, new_day)
            case Duration.WithinLastSixMonth:
                month = today.month
                if month < 7:
                    new_year = today.year - 1
                    new_month = month + 6
                else:
                    new_year = today.year
                    new_month = month - 6
                new_day = (
                    monthrange[1]
                    if (new_day := today.day)
                    > (monthrange := calendar.monthrange(new_year, new_month))[1]
                    else new_day
                )
                start_date = datetime.date(new_year, new_month, new_day)
            case Duration.WithinLastYear:
                start_date = datetime.date(today.year - 1, today.month, today.day)
        end_date = end_date if duration is None else today

        start_date_param = end_date_param = None
        if end_date is not None:
            end_date_param = end_date.strftime("%Y-%m-%d")
        if start_date is not None:
            start_date_param = start_date.strftime("%Y-%m-%d")
            end_date_param = end_date_param or today.strftime("%Y-%m-%d")

        return cast(
            IllustSearchResult,
            await super().search(
                word,
                sort=sort,
                target=target,
                start_date=start_date_param,
                end_date=end_date_param,
                search_ai_type=filter_ai if filter_ai is None else int(filter_ai),
                offset=offset,
                **kwargs,
            ),
        )
