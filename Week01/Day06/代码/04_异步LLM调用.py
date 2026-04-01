"""
Day 06 - 异步编程
示例4：异步批量调用LLM API（需API Key）
"""

import asyncio
import aiohttp
import os


API_KEY = os.getenv("OPENAI_API_KEY")
URL = "https://api.openai.com/v1/chat/completions"


async def call_llm(session, prompt: str) -> str:
    """调用OpenAI API"""
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100
    }
    
    async with session.post(URL, json=payload, headers=headers) as resp:
        if resp.status == 200:
            data = await resp.json()
            return data["choices"][0]["message"]["content"]
        return f"Error: {resp.status}"


async def batch_call_llm(prompts: list[str]) -> list[str]:
    """并发调用多个prompt"""
    async with aiohttp.ClientSession() as session:
        tasks = [call_llm(session, p) for p in prompts]
        return await asyncio.gather(*tasks)


if __name__ == "__main__":
    prompts = [
        "用一句话解释什么是大语言模型",
        "解释什么是Token",
        "解释什么是Transformer"
    ]
    
    # 注意：需设置环境变量 OPENAI_API_KEY
    if API_KEY:
        results = asyncio.run(batch_call_llm(prompts))
        for i, r in enumerate(results, 1):
            print(f"{i}. {r}")
    else:
        print("请设置 OPENAI_API_KEY 环境变量")