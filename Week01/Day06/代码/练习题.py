# -*- coding: utf-8 -*-
"""
Day 06 - 练习题：异步编程综合练习

完成以下练习，巩固今日所学知识点。
运行测试：python 练习题.py

注意：练习1-3可独立完成，练习4需要aiohttp库（pip install aiohttp）
"""

import asyncio
import unittest
from typing import List


# ==================== 练习1：同步转异步 ====================
# 任务：将同步函数转换为异步函数
# 要求：
#   - async_fetch(urls: List[str]) -> List[dict]
#   - 使用 aiohttp 异步请求每个URL
#   - 返回 [{"url": url, "status": status, "body": body}, ...]

# 提示：先定义 async def fetch_one(session, url)，然后用 gather 并发

import aiohttp


async def async_fetch(urls: List[str]) -> List[dict]:
    """
    异步批量获取URL内容
    
    Args:
        urls: URL列表
    
    Returns:
        结果列表，每个元素包含url、status、body
    """
    # TODO: 实现此函数
    # 提示：
    #   async with aiohttp.ClientSession() as session:
    #       tasks = [fetch_one(session, url) for url in urls]
    #       return await asyncio.gather(*tasks)
    pass


async def fetch_one(session, url: str) -> dict:
    """辅助函数：获取单个URL"""
    # TODO: 实现此辅助函数
    pass


# ==================== 练习2：异步延迟控制 ====================
# 任务：实现一个带延迟控制的并发任务调度器
# 要求：
#   - async def run_tasks(tasks, max_concurrent=3)
#   - 最多同时运行 max_concurrent 个任务
#   - 使用 asyncio.Semaphore 控制并发数

async def dummy_task(i: int) -> str:
    """模拟耗时任务"""
    await asyncio.sleep(0.5)
    return f"Task {i} done"


async def run_tasks(tasks: List, max_concurrent: int = 3) -> List:
    """
    带并发限制的任务调度器
    
    Args:
        tasks: 异步任务列表
        max_concurrent: 最大并发数
    
    Returns:
        所有任务的结果列表
    """
    # TODO: 实现此函数
    # 提示：使用 asyncio.Semaphore(max_concurrent)
    #   async with semaphore:
    #       return await task
    pass


# ==================== 练习3：异步LLM批量调用 ====================
# 任务：实现异步批量调用LLM的简化版本
# 要求：
#   - async_call_llm(session, prompt) -> str
#   - batch_call_llm(prompts) -> List[str]
#   - 假设API端点为 https://api.openai.com/v1/chat/completions
#   - 使用环境变量 OPENAI_API_KEY

import os


async def async_call_llm(session, prompt: str) -> str:
    """
    异步调用LLM
    
    Args:
        session: aiohttp.ClientSession
        prompt: 用户prompt
    
    Returns:
        LLM回复内容
    """
    # TODO: 实现此函数
    # 提示：
    #   headers = {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
    #   payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
    #   async with session.post(URL, json=payload, headers=headers) as resp:
    #       data = await resp.json()
    #       return data["choices"][0]["message"]["content"]
    pass


async def batch_call_llm(prompts: List[str]) -> List[str]:
    """
    批量异步调用LLM
    
    Args:
        prompts: prompt列表
    
    Returns:
        回复列表
    """
    # TODO: 实现此函数
    pass


# ==================== 练习4：超时控制 ====================
# 任务：实现带超时控制的异步任务
# 要求：
#   - async def run_with_timeout(coro, timeout)
#   - 如果超时，抛出 asyncio.TimeoutError
#   - 如果正常完成，返回结果

async def run_with_timeout(coro, timeout: float):
    """
    带超时控制的异步执行
    
    Args:
        coro: 协程对象
        timeout: 超时时间（秒）
    
    Returns:
        协程执行结果
    
    Raises:
        asyncio.TimeoutError: 超时时抛出
    """
    # TODO: 实现此函数
    # 提示：使用 asyncio.wait_for(coro, timeout=timeout)
    pass


# ==================== 单元测试（不要修改） ====================

class TestAsyncFetch(unittest.IsolatedAsyncioTestCase):

    async def test_async_fetch(self):
        urls = ["https://httpbin.org/get", "https://httpbin.org/ip"]
        results = await async_fetch(urls)
        self.assertEqual(len(results), 2)
        self.assertIn("url", results[0])
        self.assertIn("status", results[0])


class TestRunTasks(unittest.IsolatedAsyncioTestCase):

    async def test_concurrent_limit(self):
        tasks = [dummy_task(i) for i in range(6)]
        # max_concurrent=2，6个任务分3批执行
        # 每批0.5秒，总约1.5秒（不是3秒）
        import time
        start = time.time()
        results = await run_tasks(tasks, max_concurrent=2)
        elapsed = time.time() - start
        self.assertEqual(len(results), 6)
        # 应该接近0.5 * 3 = 1.5秒，允许一点误差
        self.assertLess(elapsed, 2.0)


class TestBatchCallLLM(unittest.IsolatedAsyncioTestCase):

    async def test_batch_call_requires_key(self):
        # 如果没有API Key，应该优雅处理（不是崩溃）
        if not os.getenv("OPENAI_API_KEY"):
            self.skipTest("需要 OPENAI_API_KEY")
        
        prompts = ["你好", "天气"]
        results = await batch_call_llm(prompts)
        self.assertEqual(len(results), 2)


class TestRunWithTimeout(unittest.IsolatedAsyncioTestCase):

    async def test_timeout(self):
        async def slow_coro():
            await asyncio.sleep(2)
            return "done"
        
        # 超时0.5秒，应该抛TimeoutError
        with self.assertRaises(asyncio.TimeoutError):
            await run_with_timeout(slow_coro(), 0.5)

    async def test_no_timeout(self):
        async def fast_coro():
            return "done"
        
        result = await run_with_timeout(fast_coro(), 1.0)
        self.assertEqual(result, "done")


# ==================== 运行测试 ====================

if __name__ == "__main__":
    print("=" * 50)
    print("Day 06 练习题测试")
    print("=" * 50)
    print()
    unittest.main(verbosity=2)