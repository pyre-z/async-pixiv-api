from enum import StrEnum


class SearchSortParam(StrEnum):
    DateDesc = "date_desc"
    DateAsc = "date_asc"
    PopularDesc = "popular_desc"


class SearchDurationParam(StrEnum):
    WithinLastDay = "within_last_day"
    WithinLastWeek = "within_last_week"
    WithinLastMonth = "within_last_month"
    WithinLastYear = "within_last_year"


class SearchFilterParam(StrEnum):
    IOS = "for_ios"
    Android = "for_android"


class SearchTargetParam(StrEnum):
    TagsPartial = "partial_match_for_tags"
    TagsExact = "exact_match_for_tags"
    TitleCaption = "title_and_caption"
