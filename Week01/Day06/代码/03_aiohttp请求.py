"""
Day 06 - 异步编程
示例3：aiohttp 异步HTTP请求
"""

import asyncio
import aiohttp


async def fetch_url(session, url: str) -> dict:
    """异步获取URL内容"""
    async with session.get(url) as resp:
        return {"url": url, "status": resp.status}


async def main():
    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/ip",
        "https://httpbin.org/headers"
    ]
    
    async with aiohttp.ClientSession() as session:
        # 并发请求
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        for r in results:
            print(f"{r['url']}: {r['status']}")


asyncio.run(main())