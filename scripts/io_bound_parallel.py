#!/usr/bin/env python3
"""Template for I/O-bound parallel execution using asyncio + aiohttp."""

import asyncio
from pathlib import Path

async def fetch(session, url: str) -> str:
    # Placeholder: import aiohttp in real use
    await asyncio.sleep(0.1)  # simulate
    return f"data from {url}"

async def main(urls: list[str]) -> list[str]:
    tasks = [fetch(None, url) for url in urls]
    return await asyncio.gather(*tasks)

if __name__ == "__main__":
    urls = [f"https://api.example.com/item/{i}" for i in range(10)]
    results = asyncio.run(main(urls))
    print(f"✅ Fetched {len(results)} URLs concurrently")
