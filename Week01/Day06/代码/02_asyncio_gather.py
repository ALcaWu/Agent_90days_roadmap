"""
Day 06 - 异步编程
示例2：并发执行多个任务 - asyncio.gather
"""

import asyncio


async def fetch_data(id: int) -> str:
    """模拟异步获取数据"""
    await asyncio.sleep(1)  # 模拟I/O延迟
    return f"Data from task {id}"


async def main():
    # 创建多个任务
    tasks = [fetch_data(i) for i in range(1, 4)]
    
    # 并发执行
    results = await asyncio.gather(*tasks)
    
    for r in results:
        print(r)


asyncio.run(main())
# 输出：并发执行，总耗时约1秒（不是3秒）