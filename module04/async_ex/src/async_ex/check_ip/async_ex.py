import aiohttp
import asyncio
import time

url = "https://api.ipify.org/?format=json"

async def fetch_ip(session, i):
    async with session.get(url) as response:
        data = await response.json()
        print(f"Request #{i}: ip: {data.get("ip")}")


async def main(n=100):
    start = time.perf_counter()
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_ip(session, i) for i in range(n)]
        await asyncio.gather(*tasks)

    end = time.perf_counter()
    print(f"Async total time: {end - start:.2f} seconds")


asyncio.run(main(n=100))
