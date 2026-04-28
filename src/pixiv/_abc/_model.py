from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel

if TYPE_CHECKING:
    from pixiv._abc._client import PixivClient

__all__ = ("AbstractPixivBaseDetailModel", "AbstractPixivBaseModel")


class AbstractPixivBaseModel[T: "PixivClient"](BaseModel):
    _pixiv_client: Optional[T] = None

    @property
    def pixiv_client(self) -> T:
        if self._pixiv_client is None:
            raise RuntimeError("PixivClient is not set.")
        return self._pixiv_client

    @pixiv_client.setter
    def pixiv_client(self, client: T) -> None:
        self._pixiv_client = client

    def __repr__(self) -> str:
        if hasattr(self, "id"):
            return f'<{self.__class__.__name__} id="{getattr(self, "id")}">'
        else:
            return f"<{self.__class__.__name__}>"

    def model_post_init(self, *_, **__) -> None:
        from pixiv._abc._client import PixivClientContextVar

        self._pixiv_client = PixivClientContextVar.get()  # ty:ignore[invalid-assignment]


class AbstractPixivBaseDetailModel[T: "PixivClient"](AbstractPixivBaseModel[T]):
    pass
