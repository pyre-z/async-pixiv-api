from pydantic import Field
from pydantic_settings import SettingsConfigDict

from pixiv._abc._config import PixivAPIHeadersSettings, PixivSettings
from pixiv._abc._config import PixivRateLimitSettings as _PixivRateLimitSettings
from pixiv._abc._config import PixivRetrySettings as _PixivRetrySettings

__all__ = (
    "PixivAPPAPISettings",
    "PixivAppApiHeadersSettings",
    "PixivRateLimitSettings",
    "PixivRetrySettings",
)


class PixivRateLimitSettings(_PixivRateLimitSettings):
    model_config = SettingsConfigDict(env_prefix="pixiv_app_rate_limit_")

    max_rate: int | None = 5
    time_period: int = 1


class PixivRetrySettings(_PixivRetrySettings):
    model_config = SettingsConfigDict(env_prefix="pixiv_app_retry_")


class PixivAppApiHeadersSettings(PixivAPIHeadersSettings):
    model_config = SettingsConfigDict(env_prefix="pixiv_app_headers", extra="allow")

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

    rate_limit: PixivRateLimitSettings = Field(default_factory=PixivRateLimitSettings)
    """请求频率限制"""

    retry: PixivRetrySettings = Field(default_factory=PixivRetrySettings)
    """请求失败重试设置"""
