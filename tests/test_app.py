import pytest

from pixiv.app import PixivAPPClient


@pytest.fixture
def client() -> PixivAPPClient:
    return PixivAPPClient()

@pytest.mark.asyncio
async def test_auth(client: PixivAPPClient):
    auth_info = await client.auth()
    assert auth_info.user.id

@pytest.mark.asyncio
async def test_user_info(client: PixivAPPClient):
    user_info = await client.USER(11)
    assert user_info.user.name == "pixiv事務局"