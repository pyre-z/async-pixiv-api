from pydantic import Field, computed_field
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

    rate_limit_max_rate: int | None = Field(default=9)
    rate_limit_time_period: int = Field(default=2)

    @computed_field
    @property
    def rate_limit(self) -> PixivRateLimitSettings:
        return PixivRateLimitSettings(
            max_rate=self.rate_limit_max_rate,
            time_period=self.rate_limit_time_period,
        )
