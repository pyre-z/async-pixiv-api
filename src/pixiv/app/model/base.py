from typing import TYPE_CHECKING, Any

from pydantic import ConfigDict, model_validator

from pixiv._abc._model import AbstractPixivBaseModel

if TYPE_CHECKING:
    from pixiv.app.client import PixivAPPClient  # noqa: F401

__all__ = ("PixivBaseModel",)


class PixivBaseModel(AbstractPixivBaseModel["PixivAPPClient"]):
    model_config = ConfigDict()

    @model_validator(mode="before")
    @classmethod
    def empty_str_to_none(cls, values: dict[str, Any]) -> dict[str, Any]:
        """所有空字符串转为 None"""
        if isinstance(values, dict):
            return {k: (None if v == "" else v) for k, v in values.items()}
        return values
