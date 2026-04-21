from pydantic import Field
from pydantic_settings import SettingsConfigDict

from pixiv._abc._config import (
    PixivAPIHeadersSettings,
    PixivRateLimitSettings,
    PixivSettings,
)

__all__ = (
    "PixivWebAPISettings",
    "PixivWebAPIHeadersSettings",
    "PixivRateLimitSettings",
)


class PixivWebAPIHeadersSettings(PixivAPIHeadersSettings):
    model_config = SettingsConfigDict(extra="allow")

    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.2.6121.317 Safari/537.36"


class PixivWebAPISettings(PixivSettings):
    model_config = SettingsConfigDict(env_prefix="pixiv_web_")

    api_host: str = "https://www.pixiv.net/ajax/"
    """Web API 基础请求地址"""

    cookie: str | None = None
    """Pixiv Web Cookies"""

    headers: PixivWebAPIHeadersSettings = Field(
        default_factory=PixivWebAPIHeadersSettings
    )
    """请求的额外 Headers"""

    rate_limit: PixivRateLimitSettings = PixivRateLimitSettings(
        max_rate=9, time_period=2
    )
    """请求频率限制"""
