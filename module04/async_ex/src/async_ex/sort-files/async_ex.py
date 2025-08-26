"""
Sort files based on extensions
"""
from time import time
import asyncio
from aiopath import AsyncPath
from aioshutil import copyfile

source = "picture"
output = "Backup/"

async def read_folder(path):
    tasks = []
    async for el in path.iterdir():
        if await el.is_dir():
            tasks.append(read_folder(el))
        else:
            tasks.append(copy_file(el))

    await asyncio.gather(*tasks)


async def copy_file(file):
    pass

output_folder = AsyncPath(output)  # dist
start = time()
asyncio.run(read_folder(AsyncPath(source)))
print(f"Completed: {time() - start}")

