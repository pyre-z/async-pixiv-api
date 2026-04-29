import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from yarl import URL

from pixiv.app.model import PixivBaseModel
from pixiv.app.model.other import Request, Tag

if TYPE_CHECKING:
    from pixiv.app.model import User


class IllustType(StrEnum):
    Illust = "illust"
    Manga = "manga"
    Ugoira = "ugoira"


class IllustImageUrls(PixivBaseModel):
    square_medium: URL
    medium: URL
    large: URL


class IllustSeries(PixivBaseModel):
    id: int
    title: str


class IllustMetaSinglePage(PixivBaseModel):
    pass


class IllustMetaPageImageUrls(IllustImageUrls):
    original: URL


class IllustMetaPage(PixivBaseModel):
    image_urls: IllustMetaPageImageUrls


class Illust(PixivBaseModel):
    id: int
    title: str
    type: IllustType
    image_urls: IllustImageUrls
    caption: str | None = None
    restrict: int
    user: "User"
    tags: list[Tag]
    tools: list[str]
    create_date: datetime.datetime
    page_count: int
    width: int
    height: int
    sanity_level: int
    x_restrict: int
    series: IllustSeries | None
    meta_single_page: IllustMetaSinglePage | None
    meta_pages: list[IllustMetaPage] | None
    total_view: int
    total_bookmarks: int
    is_bookmarked: bool
    visible: bool
    is_muted: bool
    seasonal_effect_animation_urls: None
    event_banners: URL | None
    illust_ai_type: int
    illust_book_style: int
    request: Request | None
    restriction_attributes: list[str] | None = None
    comment_access_control: int = 0


class IllustDetail(PixivBaseModel):
    illust: Illust
