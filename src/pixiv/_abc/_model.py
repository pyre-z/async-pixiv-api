from typing import Optional, TYPE_CHECKING, TypedDict

from pydantic import BaseModel

if TYPE_CHECKING:
    from pixiv._abc._client import PixivClient


class AbstractPixivBaseModel[T: "PixivClient"](BaseModel):
    _pixiv_client: Optional[T] = None

    @property
    def pixiv_client(self) -> Optional[T]:
        return self._pixiv_client

    @pixiv_client.setter
    def pixiv_client(self, client: T) -> None:
        self._pixiv_client = client

    def __str__(self) -> str:
        if hasattr(self, "id"):
            return f'<{self.__class__.__name__} id="{getattr(self, "id")}">'
        else:
            return f"<{self.__class__.__name__}>"

    def model_post_init(self, *_, **__) -> None:
        from pixiv._abc._client import PixivClientContextVar

        self._pixiv_client = PixivClientContextVar.get()  # ty:ignore[invalid-assignment]


class AbstractPixivBaseDetailModel[T: "PixivClient"](AbstractPixivBaseModel[T]):
    pass

class PixivParams(TypedDict, total=False):
    pass