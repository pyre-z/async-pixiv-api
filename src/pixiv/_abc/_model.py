from typing import Optional

from pydantic import BaseModel

from pixiv._abc._client import PixivClient, PixivClientContextVar

__all__ = ("BasePixivModel",)


class BasePixivModel[T: PixivClient](BaseModel):
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
        self._pixiv_client = PixivClientContextVar.get()  # ty:ignore[invalid-assignment]
