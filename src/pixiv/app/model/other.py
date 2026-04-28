from typing import AsyncIterator

from yarl import URL

from pixiv.app.model.base import PixivBaseModel


class Tag(PixivBaseModel):
    name: str
    translated_name: str | None


class PageResult[T](PixivBaseModel):
    previews: list[T]
    next_url: URL | None

    async def __aiter__(self) -> AsyncIterator[T]:
        for item in self.previews:
            yield item

        if self.next_url is not None:
            response = await self.pixiv_client.get(self.next_url)
            data = response.raise_for_status().raise_for_data().json()
            async for item in self.__class__.model_validate(data):
                yield item
