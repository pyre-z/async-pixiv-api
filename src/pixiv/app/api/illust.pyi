from pixiv.app.api.base import PixivAPIBase
from pixiv.app.model import IllustDetail

__all__ = ("PixivIllustAPI",)

class PixivIllustAPI(PixivAPIBase):
    async def __call__(self, id: int | str) -> IllustDetail: ...
    async def detail(self, id: int | str) -> IllustDetail: ...
