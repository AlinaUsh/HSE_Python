import asyncio
import aiohttp

import argparse
import os


async def load_photo(url, filename, session):
    response = await session.get(url)
    img = await response.read()
    with open(filename, 'wb') as f:
        f.write(img)


async def main(n, dir, url):
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*(load_photo(url, f'{dir}_{i}.jpg', session) for i in range(n)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', default='img/')
    parser.add_argument('--n', type=int, default=3)

    args = parser.parse_args()

    os.makedirs(args.dir, exist_ok=True)

    url = 'https://picsum.photos/200/300.jpg'

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args.n, args.dir, url))
