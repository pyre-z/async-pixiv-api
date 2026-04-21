from pixiv._abc._client import PixivClient
from pixiv.web.config import PixivWebAPISettings

__all__ = ("PixivWebClient",)


class PixivWebClient(PixivClient):
    _settings: PixivWebAPISettings

    @property
    def settings(self) -> PixivWebAPISettings:
        return self._settings

    def __init__(self, settings: PixivWebAPISettings | None = None) -> None:
        self._settings = settings or PixivWebAPISettings()
