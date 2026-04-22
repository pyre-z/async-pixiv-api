from typing import TYPE_CHECKING

from pixiv._abc._api import AbstractPixivAPIBase

if TYPE_CHECKING:
    from pixiv.app import PixivAPPClient  # noqa: F401

__all__ = ("PixivAPIBase",)


class PixivAPIBase(AbstractPixivAPIBase["PixivAPPClient"]):
    API_PATH = {"detail": "v1/{type}/detail?{type}_id={id}"}
