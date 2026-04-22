from typing import TYPE_CHECKING

from pixiv._abc._api import AbstractPixivAPIBase
from pixiv.app.model import UserDetail

if TYPE_CHECKING:
    from pixiv.app import PixivAPPClient  # noqa: F401

class PixivUserAPI(AbstractPixivAPIBase["PixivAPPClient"]):
    API_PATH: dict[str, str]

    async def __call__(self, id: int | str) -> UserDetail: ...
    async def detail(self, id: int | str) -> UserDetail: ...
