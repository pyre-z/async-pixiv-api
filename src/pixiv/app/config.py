from pydantic import Field
from pydantic_settings import SettingsConfigDict

from pixiv._abc._config import (
    PixivAPIHeadersSettings,
    PixivRateLimitSettings,
    PixivSettings,
)

__all__ = (
    "PixivAPPAPISettings",
    "PixivAppApiHeadersSettings",
    "PixivRateLimitSettings",
)


class PixivAppApiHeadersSettings(PixivAPIHeadersSettings):
    model_config = SettingsConfigDict(extra="allow")

    user_agent: str = "PixivAndroidApp/5.0.234 (Android 11; Pixel 5)"

    app_os: str = "IOS"
    app_os_version: str = "17.5.1"
    app_version: str = "7.20.6"


class PixivAPPAPISettings(PixivSettings):
    model_config = SettingsConfigDict(env_prefix="pixiv_app_")

    api_host: str = "https://app-api.pixiv.net/"
    """APP API 基础请求地址"""

    client_id: str = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
    client_secret: str = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"
    hash_secret: str = (
        "28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c"
    )

    refresh_token: str | None = None
    """Pixiv APP API Refresh Token"""

    headers: PixivAppApiHeadersSettings = Field(
        default_factory=PixivAppApiHeadersSettings
    )
    """请求的额外 Headers（APP API 与 Web API 公共的）"""

    timeout: float = 30
    """请求超时时间"""

    rate_limit: PixivRateLimitSettings = PixivRateLimitSettings(
        max_rate=5, time_period=1
    )
    """请求频率限制"""
