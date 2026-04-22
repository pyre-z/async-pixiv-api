from pixiv._abc._client import PixivClient
from pixiv.app.config import PixivAPPAPISettings
from pixiv.app.model import Account

__all__ = ("PixivAPPClient",)


class PixivAPPClient(PixivClient):
    _settings: PixivAPPAPISettings

    _access_token: str | None
    _account: Account | None

    @property
    def settings(self) -> PixivAPPAPISettings:
        return self._settings

    def is_authed(self) -> bool:
        return self._access_token is not None

    def __init__(self, settings: PixivAPPAPISettings | None = None) -> None:
        super().__init__()
        self._settings = settings or PixivAPPAPISettings()
        self._access_token = None
        self._account = None

    async def auth(self) -> Account:
        response = await self.request_client.post(
            "https://oauth.secure.pixiv.net/auth/token",
            data={
                "client_id": self.settings.client_id,
                "client_secret": self.settings.client_secret,
                "grant_type": "refresh_token",
                "include_policy": "true",
                "refresh_token": self.settings.refresh_token,
            },
        )
        response.raise_for_status()
        data = response.json()
        self._account = Account.model_validate(data["user"])
        self._access_token = data["access_token"]
        return self._account

    async def set_auth(self, auth_content: str) -> Account:
        self.settings.refresh_token = auth_content
        return await self.auth()
