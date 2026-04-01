# -*- coding: utf-8 -*-
"""
Day 05 - 模拟AI API调用
知识点：构造请求体、解析响应、错误码处理、重试机制
"""

import json
import time
import requests
from typing import List, Dict, Optional


# ==================== 1. 构造标准请求体 ====================

def build_request(
    messages: List[Dict[str, str]],
    model: str = "gpt-4",
    temperature: float = 0.7,
    max_tokens: int = 1000,
) -> dict:
    """构造OpenAI格式的请求体"""
    return {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

# 测试构造
messages = [
    {"role": "system", "content": "你是一个Python编程助手"},
    {"role": "user", "content": "什么是装饰器？"}
]
payload = build_request(messages)
print("构造的请求体:")
print(json.dumps(payload, ensure_ascii=False, indent=2))
print()


# ==================== 2. 重试机制 ====================

print("=" * 50)
print("2. 重试机制（生产环境必备）")
print("=" * 50)

def call_with_retry(
    func,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    retry_on: tuple = (429, 500, 503),
) -> dict:
    """
    带重试的函数调用装饰器
    
    Args:
        func: 要执行的函数
        max_retries: 最大重试次数
        retry_delay: 重试间隔（秒）
        retry_on: 需要重试的HTTP状态码
    """
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            result = func()

            # 检查是否需要重试
            if isinstance(result, dict) and result.get("status") in retry_on:
                raise Exception(f"状态码 {result['status']}，需要重试")

            print(f"  第{attempt}次尝试成功")
            return result

        except Exception as e:
            last_error = e
            if attempt < max_retries:
                wait = retry_delay * attempt  # 递增等待
                print(f"  第{attempt}次尝试失败: {e}，{wait}秒后重试...")
                time.sleep(wait)
            else:
                print(f"  第{attempt}次尝试失败: {e}，已达最大重试次数")

    return {"success": False, "error": str(last_error)}


# 模拟一个会失败2次再成功的函数
attempt_count = 0

def mock_api_call():
    global attempt_count
    attempt_count += 1
    if attempt_count < 3:
        raise Exception("模拟网络抖动")
    return {"success": True, "content": "这是AI的回复"}

result = call_with_retry(mock_api_call)
print(f"最终结果: {result}")
print()


# ==================== 3. 完整的AI客户端封装 ====================

print("=" * 50)
print("3. AI客户端封装（模拟调用）")
print("=" * 50)

class MockAIClient:
    """
    模拟AI API客户端
    （真实项目中替换为真实API地址和Key）
    """

    # 模拟的API响应库
    MOCK_RESPONSES = {
        "装饰器": "装饰器是Python中用于修改函数行为的语法糖，使用@符号。",
        "列表推导式": "列表推导式是一种简洁创建列表的方式：[x*2 for x in range(10)]",
        "default": "这是一个模拟的AI回复。"
    }

    def __init__(self, api_key: str = "sk-mock"):
        self.api_key = api_key
        self.total_tokens = 0

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        temperature: float = 0.7,
    ) -> Optional[str]:
        """
        发送对话请求，返回AI回复内容
        
        Returns:
            AI回复文本，失败返回None
        """
        # 构造请求体
        payload = build_request(messages, model, temperature)

        # 模拟API调用（实际项目替换为真实请求）
        response = self._mock_request(payload)

        if not response:
            return None

        # 解析响应
        content = self._parse_response(response)
        self.total_tokens += response.get("usage", {}).get("total_tokens", 0)
        return content

    def _mock_request(self, payload: dict) -> Optional[dict]:
        """模拟HTTP请求（实际替换为requests.post）"""
        last_user_msg = ""
        for msg in reversed(payload["messages"]):
            if msg["role"] == "user":
                last_user_msg = msg["content"]
                break

        # 匹配模拟回复
        reply = self.MOCK_RESPONSES.get("default")
        for keyword, response in self.MOCK_RESPONSES.items():
            if keyword in last_user_msg:
                reply = response
                break

        # 构造模拟响应
        return {
            "id": "mock-001",
            "choices": [{"message": {"role": "assistant", "content": reply}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 20, "completion_tokens": 30, "total_tokens": 50},
            "model": payload["model"],
        }

    def _parse_response(self, response: dict) -> Optional[str]:
        """解析响应，提取回复内容"""
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return None

    def get_stats(self) -> dict:
        """获取使用统计"""
        return {"total_tokens": self.total_tokens}


# 演示使用
client = MockAIClient(api_key="sk-demo")

# 多轮对话
conversation = [{"role": "system", "content": "你是Python编程助手"}]

questions = ["什么是装饰器？", "列表推导式怎么用？"]

for question in questions:
    conversation.append({"role": "user", "content": question})
    reply = client.chat(conversation)
    conversation.append({"role": "assistant", "content": reply})
    print(f"Q: {question}")
    print(f"A: {reply}")
    print()

print(f"累计消耗Token: {client.get_stats()['total_tokens']}")
