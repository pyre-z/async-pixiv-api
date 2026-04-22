from pixiv._abc._client import PixivClient
from pixiv.app.api.user import PixivUserAPI
from pixiv.app.config import PixivAPPAPISettings
from pixiv.app.model import AuthInfo

__all__ = ("PixivAPPClient",)


class PixivAPPClient(PixivClient):
    USER: PixivUserAPI

    _settings: PixivAPPAPISettings

    _access_token: str | None
    _auth_info: AuthInfo | None

    @property
    def settings(self) -> PixivAPPAPISettings:
        return self._settings

    def is_authed(self) -> bool:
        return self._access_token is not None

    def __init__(self, settings: PixivAPPAPISettings | None = None) -> None:
        super().__init__()
        self._settings = settings or PixivAPPAPISettings()
        self._access_token = None
        self._auth_info = None

        self.USER = PixivUserAPI(self)

    async def auth(self) -> AuthInfo:
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
        self._auth_info = AuthInfo.model_validate(data)
        self._access_token = self._auth_info.access_token
        self.request_client.headers.setdefault(
            "Authorization", f"Bearer {self._access_token}"
        )
        return self._auth_info

    async def set_auth(self, auth_content: str) -> AuthInfo:
        self.settings.refresh_token = auth_content
        return await self.auth()
