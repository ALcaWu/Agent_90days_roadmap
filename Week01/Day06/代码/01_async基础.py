"""
Day 06 - 异步编程
示例1：async/await 基础
"""

import asyncio


# 定义异步函数
async def say_hello():
    await asyncio.sleep(1)  # 模拟I/O操作，不阻塞
    return "Hello!"


async def main():
    # 运行异步函数
    result = await say_hello()
    print(result)


# 入口
asyncio.run(main())