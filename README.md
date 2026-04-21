# async-pixiv-api ✨

一个面向异步编程的 Pixiv API Python 客户端库，基于 `aiohttp` 和 `pydantic` 构建，提供类型安全、直观易用的异步接口。

[![PyPI](https://img.shields.io/pypi/v/async-pixiv-api.svg)](https://pypi.org/project/async-pixiv-api/)
[![Python](https://img.shields.io/pypi/pyversions/async-pixiv-api.svg)](https://pypi.org/project/async-pixiv-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> ⚠️ **注意**: 本项目处于**早期开发阶段**，核心 API 正在实现中。欢迎提交 Issue 和 Pull Request！

---

## 特性

- ✅ **全异步支持** - 基于 `asyncio` + `aiohttp`，高并发友好
- ✅ **类型安全** - 完整的类型提示，`pydantic` 数据模型校验
- ✅ **多种认证方式** - 支持 Refresh Token 和 Cookie 认证
- ✅ **自动令牌刷新** - 自动处理访问令牌过期和刷新
- ✅ **环境变量配置** - 基于 `pydantic-settings`，支持 `.env` 文件
- ✅ **完善的错误处理** - 结构化的异常类型，便于捕获处理
- ✅ **内置下载功能** - 支持插画原图批量下载（带速率限制）

---

## 安装

### 使用 pip

```bash
# 基础安装
pip install async-pixiv-api

# 启用 speedups 优化（推荐，包含更快的 HTTP 解析库）
pip install "async-pixiv-api[speedups]"
```

### 使用 Poetry

```bash
poetry add async-pixiv-api

# 启用 speedups
poetry add "async-pixiv-api[speedups]"
```

### 从源码安装

```bash
git clone https://github.com/PyreZ/async-pixiv-api.git
cd async-pixiv-api
pip install -e ".[speedups]"
```

---

## 快速开始

### 环境变量配置

在项目根目录创建 `.env` 文件：

```env
# Pixiv 认证（二选一即可）
PIXIV_REFRESH_TOKEN=your_refresh_token_here
# PIXIV_COOKIE=your_cookie_string_here

# 可选配置
PIXIV_BASE_URL=https://app-api.pixiv.net
PIXIV_TIMEOUT=30
PIXIV_RATE_LIMIT=100
```

### 基础使用示例

```python
import asyncio
from pixiv import PixivClient

async def main():
    # 从环境变量自动加载配置
    async with PixivClient() as client:
        # 搜索插画
        results = await client.search_illust("星空", page=1, limit=10)
        
        for illust in results:
            print(f"ID: {illust.id}, 标题: {illust.title}, 作者: {illust.user.name}")

        # 获取插画详情
        illust_id = 12345678
        details = await client.get_illust_details(illust_id)
        print(f"\n详情: {details.title}")
        print(f"标签: {', '.join(tag.name for tag in details.tags)}")

        # 下载原图
        await client.download_illust(illust_id, path="./downloads/")

if __name__ == "__main__":
    asyncio.run(main())
```

### 获取用户收藏

```python
async with PixivClient() as client:
    bookmarks = await client.get_user_bookmarks(
        user_id=123456,
        restrict="public",  # 或 "private"
        limit=50
    )
    
    for item in bookmarks:
        print(item.illust.title)
```

---

## 配置说明

### 环境变量列表

| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `PIXIV_REFRESH_TOKEN` | `str` | `None` | Pixiv Refresh Token |
| `PIXIV_COOKIE` | `str` | `None` | 浏览器 Cookie 字符串 |
| `PIXIV_BASE_URL` | `str` | `https://app-api.pixiv.net` | API 基础地址 |
| `PIXIV_TIMEOUT` | `float` | `30.0` | 请求超时时间（秒） |
| `PIXIV_RATE_LIMIT` | `int` | `100` | 每分钟请求速率限制 |
| `PIXIV_USER_AGENT` | `str` | (内置) | 请求 User-Agent |

### 代码中直接配置

```python
from pixiv import PixivClient, PixivSettings

settings = PixivSettings(
    refresh_token="your_token",
    timeout=60.0,
    rate_limit=150
)

client = PixivClient(settings=settings)
```

---

## 认证指南

Pixiv API 认证主要有两种方式：

### 方式 1: Refresh Token（推荐）

1. 使用 [Pixiv OAuth 工具](https://github.com/upbit/pixivpy/wiki) 获取 Refresh Token
2. 将 Token 存入环境变量 `PIXIV_REFRESH_TOKEN`
3. 客户端会自动刷新访问令牌，无需手动处理

### 方式 2: Cookie

1. 登录 Pixiv 网站后，从浏览器开发者工具复制 Cookie
2. 将 Cookie 字符串存入 `PIXIV_COOKIE` 环境变量

> ⚠️ **安全提示**: 永远不要将 Token 或 Cookie 硬编码在代码中！使用环境变量或安全的密钥管理系统。

---

## API 参考

### PixivClient

主要客户端类，支持异步上下文管理器。

```python
class PixivClient:
    async def __aenter__(self) -> PixivClient: ...
    async def __aexit__(self, exc_type, exc, tb) -> None: ...
```

### 插画相关

#### `search_illust(query, page=1, limit=30, sort="date_desc", duration=None)`

搜索插画。

**参数:**
- `query: str` - 搜索关键词
- `page: int` - 页码（从 1 开始）
- `limit: int` - 每页数量（最大 50）
- `sort: str` - 排序方式: `"date_desc"`, `"date_asc"`, `"popular_desc"`
- `duration: str | None` - 时间范围: `"last_day"`, `"last_week"`, `"last_month"`

#### `get_illust_details(illust_id)`

获取单张插画详细信息。

**参数:**
- `illust_id: int` - 插画 ID

#### `download_illust(illust_id, path, filename=None, overwrite=False)`

下载插画原图。

**参数:**
- `illust_id: int` - 插画 ID
- `path: str | Path` - 保存目录
- `filename: str | None` - 自定义文件名（默认使用原文件名）
- `overwrite: bool` - 是否覆盖已存在的文件

### 用户相关

#### `get_user_bookmarks(user_id, restrict="public", page=1, limit=30)`

获取用户收藏列表。

**参数:**
- `user_id: int` - 用户 ID
- `restrict: str` - 可见性: `"public"`, `"private"`
- `page: int` - 页码
- `limit: int` - 每页数量

#### `get_user_profile(user_id)`

获取用户资料。

**参数:**
- `user_id: int` - 用户 ID

---

## 开发指南

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/PyreZ/async-pixiv-api.git
cd async-pixiv-api

# 安装开发依赖
pip install -e ".[dev,test]"

# 或使用 uv
uv sync
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并显示覆盖率
pytest --cov=pixiv --cov-report=html

# 类型检查
mypy src/

# 代码格式化
black src/ tests/

# 代码质量检查
ruff check src/ tests/
```

### 项目结构

```
async-pixiv-api/
├── src/
│   └── pixiv/
│       ├── __init__.py          # 公开 API 导出
│       ├── client.py            # 核心客户端实现
│       ├── models.py            # Pydantic 数据模型
│       ├── exceptions.py        # 异常类定义
│       ├── config.py            # 配置管理
│       ├── api/                 # API 端点实现
│       │   ├── __init__.py
│       │   ├── illust.py        # 插画相关 API
│       │   └── user.py          # 用户相关 API
│       └── utils/               # 工具函数
│           ├── __init__.py
│           ├── auth.py          # 认证工具
│           └── download.py      # 下载工具
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_client.py
│   └── test_api/
├── pyproject.toml               # 项目配置
└── README.md                    # 项目文档
```

---

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

提交前请确保：
- ✅ 代码通过 `mypy` 类型检查
- ✅ 代码通过 `ruff` 质量检查
- ✅ 代码使用 `black` 格式化
- ✅ 添加了必要的测试用例
- ✅ 所有测试通过

---

## 路线图

- [ ] 核心客户端与认证系统
- [ ] 插画搜索与详情 API
- [ ] 用户收藏与资料 API
- [ ] 图片下载功能
- [ ] 完整的 Pydantic 数据模型
- [ ] 错误处理与重试机制
- [ ] 速率限制与请求队列
- [ ] 单元测试与集成测试
- [ ] 完整的 API 文档
- [ ] 命令行工具 (CLI)

---

## 许可证

本项目采用 [MIT License](LICENSE) 许可证。

---

## 免责声明

- 本项目仅供学习和研究使用
- 使用本库时请遵守 Pixiv 的 [使用条款](https://www.pixiv.net/terms)
- 请勿滥用 API 或进行批量爬取
- 作者不对因使用本库造成的任何问题负责

---

## 致谢

- 感谢 [PixivPy](https://github.com/upbit/pixivpy) 提供的 API 研究参考
- 感谢所有为本项目贡献代码的开发者

---

**需要帮助？** 欢迎开启 [Issue](https://github.com/PyreZ/async-pixiv-api/issues) 讨论！
