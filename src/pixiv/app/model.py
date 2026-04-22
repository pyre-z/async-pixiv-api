from typing import TYPE_CHECKING

from pydantic import EmailStr
from yarl import URL

from pixiv._abc._model import BasePixivModel

if TYPE_CHECKING:
    from pixiv.app.client import PixivAPPClient  # noqa: F401


class PixivModel(BasePixivModel["PixivAPPClient"]):
    pass


class ProfileImageUrls(PixivModel):
    px_16x16: URL
    px_50x50: URL
    px_170x170: URL


class Account(PixivModel):
    id: int
    name: str
    account: str
    mail_address: EmailStr
    profile_image_urls: ProfileImageUrls
    is_premium: bool
    x_restrict: int
    is_mail_authorized: bool
    require_policy_agreement: bool
