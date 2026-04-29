from enum import StrEnum


class Sort(StrEnum):
    DateDesc = "date_desc"
    DateAsc = "date_asc"
    Popular = "popular_desc"


class Duration(StrEnum):
    WithinLastDay = "within_last_day"
    WithinLastWeek = "within_last_week"
    WithinLastMonth = "within_last_month"
    WithinLastSixMonth = "within_last_six_months"
    WithinLastYear = "within_last_year"


class SearchFilterParam(StrEnum):
    IOS = "for_ios"
    Android = "for_android"


class Target(StrEnum):
    TagsPartial = "partial_match_for_tags"
    """标签部分一致"""

    TagsExact = "exact_match_for_tags"
    """标签完全一致"""

    TitleCaption = "title_and_caption"
    """搜索标题与说明"""


class RankingMode(StrEnum):
    Safe = "safe"
    R18 = "r18"


class ContentType(StrEnum):
    Illust = "illust"
    Manga = "manga"
