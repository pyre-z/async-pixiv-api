# async-pixiv-api ✨

一个面向异步编程的 Pixiv API Python 客户端库，基于 `aiohttp`、`pydantic` 和 `pyrate-limiter` 构建。

[![PyPI](https://img.shields.io/pypi/v/async-pixiv-api.svg)](https://pypi.org/project/async-pixiv-api/)
[![Python](https://img.shields.io/pypi/pyversions/async-pixiv-api.svg)](https://pypi.org/project/async-pixiv-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 特性

- ✅ **全异步支持** - 基于 `asyncio` + `aiohttp`，高并发友好
- ✅ **类型安全** - 完整的类型提示，`pydantic` 数据模型校验
- ✅ **双 API 支持** - APP API (OAuth Refresh Token) 和 Web API (Cookie)
- ✅ **内置速率限制** - 基于 `pyrate-limiter`，防止请求过于频繁
- ✅ **DNS 绕过 (DoH)** - 内置 `ByPassResolver`，绕过 DNS 劫持
- ✅ **代理支持** - 支持 SOCKS 和 HTTP 代理
- ✅ **环境变量配置** - 基于 `pydantic-settings`，支持 `.env` 文件

---

## 安装

### 使用 pip

```bash
# 基础安装
pip install async-pixiv-api

# 启用 speedups 优化（推荐）
pip install "async-pixiv-api[speedups]"
```

### 使用 Poetry

```bash
poetry add async-pixiv-api
```

### 从源码安装

```bash
git clone https://github.com/PyreZ/async-pixiv-api.git
cd async-pixiv-api
pip install -e .
```

---

## 快速开始

### 环境变量配置

#### APP API 配置（OAuth 认证）

```env
# Pixiv APP API 设置（前缀: pixiv_app_）
pixiv_app_refresh_token=your_refresh_token_here
pixiv_app_proxy=http://127.0.0.1:7890
pixiv_app_bypass=true
pixiv_app_timeout=30
```

#### Web API 配置（Cookie 认证）

```env
# Pixiv Web API 设置（前缀: pixiv_web_）
pixiv_web_cookie=your_cookie_string_here
pixiv_web_proxy=http://127.0.0.1:7890
pixiv_web_timeout=30
```

### 基础使用示例

```python
import asyncio
from pixiv.app import PixivAPPClient, PixivAPPAPISettings


async def main():
    # 方式 1: 从环境变量加载配置
    client = PixivAPPClient()

    # 方式 2: 代码中直接配置
    settings = PixivAPPAPISettings(
        refresh_token="your_refresh_token",
        bypass=True,
        timeout=60.0,
    )
    client = PixivAPPClient(settings=settings)

    # 认证
    await client.auth()

    # 使用 session 发起请求
    response = await client.request_client.get(
        "https://app-api.pixiv.net/v1/illust/ranking"
    )
    data = await response.json()
    print(data)

    # 关闭会话
    await client.request_client.close()


if __name__ == "__main__":
    asyncio.run(main())
```

### Web API 使用

```python
from pixiv.web import PixivWebClient, PixivWebAPISettings


async def main():
    settings = PixivWebAPISettings(
        cookie="your_cookie_string",
    )
    client = PixivWebClient(settings=settings)

    response = await client.request_client.get(
        "https://www.pixiv.net/ajax/user/123456/profile"
    )
    data = await response.json()
    print(data)

    await client.request_client.close()
```

#### Web API 配置（Cookie 认证）

```env
# Pixiv Web API 设置（前缀: pixiv_web_）
pixiv_web_cookie=your_cookie_string_here
pixiv_web_proxy=http://127.0.0.1:7890
pixiv_web_timeout=30
```

### 基础使用示例

```python
import asyncio
from pixiv.app import PixivAPPClient
from pixiv.web import PixivWebClient


async def app_api_example():
    """使用 APP API（推荐）- 支持 refresh_token 自动刷新"""
    async with PixivAPPClient() as client:
        # 链式调用: client.app.user().illusts()
        illusts = await client.app.user().illusts()
        print(illusts)


async def web_api_example():
    """使用 Web API - 需要手动提供 cookie"""
    async with PixivWebClient() as client:
        # 链式调用: client.web.user().bookmarks()
        bookmarks = await client.web.user().bookmarks()
        print(bookmarks)


async def main():
    await app_api_example()
    await web_api_example()


if __name__ == "__main__":
    asyncio.run(main())
```

### 链式 API 调用

项目采用链式调用风格设计 API：

```python
# APP API 链式调用
client.app.user().illusts()
client.app.illust().details(illust_id=123456)
client.app.search().illust(word="星空")

# Web API 链式调用
client.web.user().bookmarks(user_id=123456)
client.web.illust().details(illust_id=123456)
```

---

## 配置说明

### APP API 环境变量（前缀: `pixiv_app_`）

| 变量名                       | 类型      | 默认值                          | 说明            |
|---------------------------|---------|------------------------------|---------------|
| `pixiv_app_api_host`      | `str`   | `https://app-api.pixiv.net/` | API 基础地址      |
| `pixiv_app_proxy`         | `str`   | `None`                       | 代理服务器         |
| `pixiv_app_bypass`        | `bool`  | `False`                      | 是否启用 DoH 绕过   |
| `pixiv_app_timeout`       | `float` | `30.0`                       | 请求超时时间（秒）     |
| `pixiv_app_refresh_token` | `str`   | `None`                       | Refresh Token |

### Web API 环境变量（前缀: `pixiv_web_`）

| 变量名                  | 类型      | 默认值                           | 说明          |
|----------------------|---------|-------------------------------|-------------|
| `pixiv_web_api_host` | `str`   | `https://www.pixiv.net/ajax/` | API 基础地址    |
| `pixiv_web_proxy`    | `str`   | `None`                        | 代理服务器       |
| `pixiv_web_bypass`   | `bool`  | `False`                       | 是否启用 DoH 绕过 |
| `pixiv_web_timeout`  | `float` | `30.0`                        | 请求超时时间（秒）   |
| `pixiv_web_cookie`   | `str`   | `None`                        | Cookie 字符串  |

### 代码中直接配置

```python
from pixiv.app import PixivAPPClient
from pixiv.app.config import PixivAPPAPISettings

# 方式 1: 直接传入设置
settings = PixivAPPAPISettings(
    refresh_token="your_token",
    bypass=True,
    timeout=60.0,
)
client = PixivAPPClient(settings=settings)

# 方式 2: 从环境变量加载
settings = PixivAPPAPISettings()  # 自动从环境变量读取
client = PixivAPPClient(settings=settings)
```

---

## API 参考

### 客户端类

#### PixivAPPClient

APP API 客户端，支持 OAuth Refresh Token 认证。

```python
from pixiv.app import PixivAPPClient

client = PixivAPPClient(settings=None)  # settings 可选，默认从环境变量加载
```

#### PixivWebClient

Web API 客户端，支持 Cookie 认证。

```python
from pixiv.web import PixivWebClient

client = PixivWebClient(settings=None)  # settings 可选，默认从环境变量加载
```

### 速率限制设置

| 变量名                      | 类型    | APP API 默认值 | Web API 默认值 | 说明         |
|--------------------------|-------|-------------|-------------|------------|
| `rate_limit.max_rate`    | `int` | 5           | 9           | 每时间周期最大请求数 |
| `rate_limit.time_period` | `int` | 1 秒         | 2 秒         | 时间周期（秒）    |

---

## 核心组件

### ByPassResolver

DNS-over-HTTPS (DoH) 解析器，用于绕过 DNS 劫持。

- 使用 Cloudflare/Google 公共 DoH 端点
- 自动将 Pixiv 相关域名解析到替代域名
- 支持并行查询多个 DoH 端点

```python
from pixiv._utils.net import ByPassResolver

resolver = ByPassResolver()
```

### PixivClientSession

扩展的 `aiohttp.ClientSession`，内置请求速率限制。

```python
from pixiv._utils.net import PixivRequestClient
from pyrate_limiter import Duration

session = PixivRequestClient(
    "https://api.example.com/",
    rate_limiter=create_inmemory_limiter(rate_per_duration=10, duration=Duration.SECOND),
)
```

---

## 认证指南

### APP API 认证（推荐）

使用 Refresh Token 进行 OAuth 认证：

1. 从 [Pixiv OAuth 工具](https://github.com/upbit/pixivpy/wiki) 获取 Refresh Token
2. 配置环境变量 `pixiv_app_refresh_token`
3. 调用 `await client.auth()` 获取访问令牌

```python
from pixiv.app import PixivAPPClient

client = PixivAPPClient()
await client.auth()  # 自动获取并存储 access_token
```

### Web API 认证

使用浏览器 Cookie 进行认证：

1. 登录 Pixiv 网站
2. 从开发者工具复制 Cookie 字符串
3. 配置环境变量 `pixiv_web_cookie`

```python
from pixiv.web import PixivWebClient

client = PixivWebClient()
# 直接使用 session 发起请求
response = await client.request_client.get("https://www.pixiv.net/ajax/user/123456/profile")
```

> ⚠️ **安全提示**: 永远不要将 Token 或 Cookie 硬编码在代码中！

---

## 项目结构

```
async-pixiv-api/
├── src/
│   └── pixiv/
│       ├── __init__.py              # dotenv 加载
│       ├── exceptions.py            # 异常类定义（待实现）
│       ├── _abc/                    # 抽象基类
│       │   ├── _client.py          # PixivClient 抽象类
│       │   └── _config.py          # 基础配置模型
│       ├── _utils/                  # 工具模块
│       │   ├── net.py              # ByPassResolver + PixivClientSession
│       │   └── net.pyi             # 类型存根
│       ├── app/                     # APP API 模块
│       │   ├── client.py           # PixivAPPClient (OAuth)
│       │   └── config.py           # PixivAPPAPISettings
│       └── web/                     # Web API 模块
│           ├── client.py           # PixivWebClient
│           └── config.py           # PixivWebAPISettings
├── tests/
│   └── test_limiter.py             # 速率限制测试
├── pyproject.toml                   # 项目配置
├── uv.lock                          # 依赖锁定
├── main.py                          # 示例代码
└── README.md                        # 项目文档
```

---

## 依赖说明

| 依赖                  | 版本       | 说明          |
|---------------------|----------|-------------|
| `aiohttp`           | >=3.13.5 | 异步 HTTP 客户端 |
| `aiohttp-socks`     | >=0.11.0 | SOCKS 代理支持  |
| `pydantic-settings` | >=2.14.0 | 配置管理        |
| `pydantic`          | >=2.13.3 | 数据验证        |
| `pyrate-limiter`    | >=4.1.0  | 速率限制        |

---

## 开发指南

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/PyreZ/async-pixiv-api.git
cd async-pixiv-api

# 安装依赖
pip install -e .

# 运行测试
python -m tests.test_limiter
```

---

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

---

## 路线图

- [x] 核心客户端架构 (PixivClient ABC)
- [x] 双 API 支持 (APP API + Web API)
- [x] DoH 绕过解析器 (ByPassResolver)
- [x] 内置速率限制 (pyrate-limiter)
- [x] 代理支持 (SOCKS + HTTP)
- [ ] 完整的异常类体系
- [ ] 公开 API 方法封装
- [ ] 数据模型 (Pydantic)
- [ ] 完整单元测试
- [ ] CLI 工具

---

## 许可证

本项目采用 [MIT License](LICENSE) 许可证。

---

**如果这个项目对你有帮助，请给一个 ⭐！**

欢迎开启 [Issue](https://github.com/PyreZ/async-pixiv-api/issues) 讨论！
