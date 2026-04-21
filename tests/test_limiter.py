import time

from pyrate_limiter import Duration, Limiter, Rate
from pyrate_limiter.limiter_factory import create_inmemory_limiter

from pixiv._utils.net import PixivClientSession


async def main():
    session = PixivClientSession(
        limiter=create_inmemory_limiter(
            rate_per_duration=100,
            duration=Duration.SECOND,
        )
    )
    num = 1000
    start_time = time.time()
    for i in range(1, num + 1):
        async with session.get("http://127.0.0.1:7890"):
            if i and i % 100 == 0:
                print(
                    f"{i} requests completed. Elapsed time: {time.time() - start_time}s."
                )
    end_time = time.time()
    elapsed_time = end_time - start_time
    print()
    print(f"Elapsed time: {elapsed_time}s. Rate: {num / elapsed_time}r/s.")


def __main__():
    import asyncio

    asyncio.run(main())


if __name__ == "__main__":
    __main__()
