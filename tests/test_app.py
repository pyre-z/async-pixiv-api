import pytest

from pixiv.app import PixivAPPClient


@pytest.fixture
async def client() -> PixivAPPClient:
    client = PixivAPPClient()
    await client.auth()
    return client


@pytest.mark.asyncio
async def test_auth(client: PixivAPPClient):
    assert client.is_authed
    assert client._auth_info is not None
    assert client._auth_info.user.id


@pytest.mark.asyncio
async def test_user_info(client: PixivAPPClient):
    user_info = await client.User(11)
    assert user_info.user.name == "pixiv事務局"


@pytest.mark.asyncio
async def test_user_search(client: PixivAPPClient):
    user_search_result = await client.User.search("pixiv")
    count = 0
    async for user in user_search_result:
        while count < 50:
            assert user.user.name
            count += 1
        break


@pytest.mark.asyncio
async def test_user_recommended(client: PixivAPPClient):
    user_recommended_result = await client.User.recommended()
    count = 0
    async for user in user_recommended_result:
        while count < 50:
            assert user.user.name
            count += 1
        break
