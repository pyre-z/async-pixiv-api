import dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ("PixivSettings", "PixivRateLimitSettings", "PixivAPIHeadersSettings")

dotenv.load_dotenv()


class PixivRateLimitSettings(BaseSettings):
    max_rate: int | None = None
    time_period: int = 60


class PixivAPIHeadersSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="allow")

    user_agent: str
    accept_language: str = "zh-CN,zh;q=0.9"
    referer: str = "https://www.pixiv.net/"


class PixivRetrySettings(BaseSettings):
    times: int | None = None
    sleep_time: float = 5


class PixivSettings(BaseSettings):
    api_host: str
    """基础请求地址"""

    proxy: str | None = None
    """代理服务器"""

    bypass: bool = False
    """是否绕过 SSL"""

    headers: PixivAPIHeadersSettings
    """请求头"""

    timeout: float = 30
    """请求超时时间"""

    rate_limit: PixivRateLimitSettings = Field(default_factory=PixivRateLimitSettings)
    """请求频率限制"""

    retry: PixivRetrySettings = Field(default_factory=PixivRetrySettings)
    """请求失败重试设置"""
