from pixiv._abc._client import PixivClient
from pixiv.app.config import PixivAPPAPISettings

__all__ = ("PixivAPPClient",)


class PixivAPPClient(PixivClient):
    _settings: PixivAPPAPISettings

    _access_token: str | None

    @property
    def settings(self) -> PixivAPPAPISettings:
        return self._settings

    def __init__(self, settings: PixivAPPAPISettings | None = None) -> None:
        self._settings = settings or PixivAPPAPISettings()
        self._access_token = None

    async def auth(self):
        async with self.session.post(
            "https://oauth.secure.pixiv.net/auth/token",
            data={
                "client_id": self.settings.client_id,
                "client_secret": self.settings.client_secret,
                "grant_type": "refresh_token",
                "include_policy": "true",
                "refresh_token": self.settings.refresh_token,
            }
        ) as response:
            response.raise_for_status()
            data = await response.json()
            self._access_token = data["access_token"]

    async def set_auth(self, auth_content: str):
        self.settings.refresh_token = auth_content
        await self.auth()
