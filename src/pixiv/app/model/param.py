from enum import StrEnum


class SearchFilter(StrEnum):
    IOS = "for_ios"
    Android = "for_android"


class SearchRestrict(StrEnum):
    Public = "public"
    Private = "private"


class SearchMode(StrEnum):
    Day = "day"
    Week = "week"
    Month = "month"
    DayMale = "day_male"
    DayFemale = "day_female"
    WeekOriginal = "week_original"
    WeekRookie = "week_rookie"
    DayR18 = "day_r18"
    DayMaleR18 = "day_male_r18"
    DayFemaleR18 = "day_female_r18"
    WeekR18 = "week_r18"
    WeekR18G = "week_r18g"
    DayManga = "day_manga"
    WeekManga = "week_manga"
    MonthManga = "month_manga"
    WeekRookieManga = "week_rookie_manga"
    DayR18Manga = "day_r18_manga"
    WeekR18Manga = "week_r18_manga"
    WeekR18GManga = "week_r18g_manga"


class SearchSort(StrEnum):
    DateDesc = "date_desc"
    DateAsc = "date_asc"
    PopularDesc = "popular_desc"
