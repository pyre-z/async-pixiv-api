import datetime
from typing import TYPE_CHECKING

from yarl import URL

from pixiv.app.model.base import PixivBaseModel
from pixiv.app.model.other import Request, Tag

if TYPE_CHECKING:
    from pixiv.app.model import User


class NovelImageUrls(PixivBaseModel):
    square_medium: URL
    medium: URL
    large: URL


class NovelTag(Tag):
    added_by_uploaded_user: bool


class NovelSeries(PixivBaseModel):
    pass


class Novel(PixivBaseModel):
    id: int
    title: str
    caption: str | None = None
    restrict: int
    x_restrict: int
    is_original: bool
    image_urls: NovelImageUrls
    create_date: datetime.datetime
    tags: list[NovelTag]
    page_count: int
    text_length: int
    user: "User"
    series: NovelSeries | None
    visible: bool
    total_bookmarks: int
    total_view: int
    total_comments: int
    is_bookmarked: bool
    is_muted: bool
    is_mypixiv_only: bool
    is_x_restricted: bool
    novel_ai_type: int
    request: Request | None
