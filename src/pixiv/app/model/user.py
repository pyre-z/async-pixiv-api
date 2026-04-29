from datetime import date
from enum import StrEnum
from typing import TYPE_CHECKING, Iterator

from pydantic import EmailStr, field_validator
from yarl import URL

from pixiv.app.model.base import PixivBaseModel
from pixiv.app.model.other import PageResult

if TYPE_CHECKING:
    from pixiv.app.model import Illust, Novel


class UserGender(StrEnum):
    Unknown = "unknown"
    Male = "male"
    Female = "female"


class Publicity(StrEnum):
    Public = "public"
    Private = "private"


class UserProfileImageUrls(PixivBaseModel):
    medium: URL


class User(PixivBaseModel):
    id: int
    name: str
    account: str
    profile_image_urls: UserProfileImageUrls
    comment: str | None = None
    is_followed: bool
    is_access_blocking_user: bool | None = None


class Profile(PixivBaseModel):
    @field_validator("gender", mode="before")
    @classmethod
    def none_to_gender(cls, value: str | None) -> UserGender:
        """所有空字符串转为 None"""
        if value is None:
            return UserGender.Unknown
        return UserGender(value)

    webpage: URL | None
    gender: UserGender = UserGender.Unknown
    birth: date | None = None
    birth_year: int | None = None
    region: str
    address_id: int | None = None
    country_code: str | None = None
    job: str | None = None
    job_id: int | None = None
    total_follow_users: int
    total_mypixiv_users: int
    total_illusts: int
    total_manga: int
    total_novels: int
    total_illust_bookmarks_public: int
    total_illust_series: int
    total_novel_series: int
    background_image_url: URL | None
    twitter_account: str | None = None
    twitter_url: URL | None
    pawoo_url: URL | None
    is_premium: bool
    is_using_custom_profile_image: bool


class ProfilePublicity(PixivBaseModel):
    gender: Publicity
    region: Publicity
    birth_day: Publicity
    birth_year: Publicity
    job: Publicity
    pawoo: bool


class Workspace(PixivBaseModel):
    pc: str | None
    monitor: str | None
    tool: str | None
    scanner: str | None
    tablet: str | None
    mouse: str | None
    printer: str | None
    desktop: str | None
    music: str | None
    desk: str | None
    chair: str | None
    comment: str | None
    workspace_image_url: URL | None


class UserDetail(PixivBaseModel):
    user: User
    profile: Profile
    profile_publicity: ProfilePublicity
    workspace: Workspace


class AccountProfileImageUrls(PixivBaseModel):
    px_16x16: URL
    px_50x50: URL
    px_170x170: URL


class Account(PixivBaseModel):
    id: int
    name: str
    account: str
    profile_image_urls: AccountProfileImageUrls
    mail_address: EmailStr
    is_premium: bool
    x_restrict: int
    is_mail_authorized: bool
    require_policy_agreement: bool


class AuthInfo(PixivBaseModel):
    access_token: str
    expires_in: int
    token_type: str
    scope: str | None
    refresh_token: str
    user: Account


class UserPreview(PixivBaseModel):
    user: User
    illusts: list["Illust"]
    novels: list["Novel"]
    is_muted: bool


class UserSearchResult(PageResult[UserPreview]):
    user_previews: list[UserPreview]

    def __iter__(self) -> Iterator[UserPreview]:
        return iter(self.user_previews)


class UserRecommendedResult(UserSearchResult):
    pass
