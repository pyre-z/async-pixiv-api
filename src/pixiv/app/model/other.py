from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, AsyncIterator, Iterator, Self

from yarl import URL

from pixiv.app.model.base import PixivBaseModel

if TYPE_CHECKING:
    from pixiv.app.model import User


class Tag(PixivBaseModel):
    name: str
    translated_name: str | None


class Result(PixivBaseModel):
    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        attr_name = self.__class__.__module__.split(".")[-1]
        attr_name = "previews" if hasattr(self, "previews") else attr_name
        attr_value = getattr(self, attr_name, None)
        if hasattr(attr_value, "__len__"):
            attr_value = f"[{', '.join(map(repr, attr_value[:3] if len(attr_value) > 3 else attr_value))}...]"
        return f"<{cls_name} {attr_name}={attr_value}>"


class PageResult[T](ABC, Result):
    next_url: URL | None

    @abstractmethod
    def __iter__(self) -> Iterator[T]: ...  # ty:ignore[invalid-method-override]

    def __len__(self) -> int:
        return len(list(self.__iter__()))

    async def __aiter__(self) -> AsyncIterator[T]:
        for item in self:
            yield item

        if (next := await self.get_next()) is not None:
            async for item in next:
                yield item

    async def get_next(self) -> Self | None:
        return (
            None
            if self.next_url is None
            else self.model_validate(
                (await self.pixiv_client.get(self.next_url))
                .raise_for_data_and_status()
                .json()
            )
        )


class DetailResult(Result):
    pass


class Request(PixivBaseModel):
    class RequestInfo(PixivBaseModel):
        class CollaborateStatus(PixivBaseModel):
            collaborate_anonymous_flag: bool
            collaborate_user_samples: list["User"]

        collaborate_status: CollaborateStatus
        fan_user_id: int | None
        role: str

    request_info: RequestInfo
    request_users: list["User"]
