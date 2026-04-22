from typing import TYPE_CHECKING

from pixiv.app.api.base import PixivAPIBase

if TYPE_CHECKING:
    from pixiv.app import PixivAPPClient  # noqa: F401

__all__ = ("PixivUserAPI", )


class PixivUserAPI(PixivAPIBase):
    pass
