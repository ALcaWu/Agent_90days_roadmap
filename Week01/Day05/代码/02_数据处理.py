# -*- coding: utf-8 -*-
"""
Day 05 - JSON数据处理
知识点：json模块、嵌套数据提取、列表推导式、数据清洗
"""

import json
from typing import List, Dict, Any, Optional


# ==================== 1. json模块基础 ====================

print("=" * 50)
print("1. json模块基础")
print("=" * 50)

# Python对象 → JSON字符串
data = {
    "model": "gpt-4",
    "messages": [
        {"role": "user", "content": "你好"}
    ],
    "temperature": 0.7,
    "stream": False
}

json_str = json.dumps(data, ensure_ascii=False, indent=2)
print("序列化结果:")
print(json_str)

# JSON字符串 → Python对象
parsed = json.loads(json_str)
print(f"\n反序列化后的model: {parsed['model']}")
print(f"消息内容: {parsed['messages'][0]['content']}")

print()


# ==================== 2. 嵌套数据提取（AI API响应解析） ====================

print("=" * 50)
print("2. 解析AI API响应（模拟OpenAI格式）")
print("=" * 50)

# 模拟OpenAI API的真实响应结构
mock_response = {
    "id": "chatcmpl-abc123",
    "object": "chat.completion",
    "created": 1710000000,
    "model": "gpt-4",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "你好！我是AI助手，有什么可以帮你的？"
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 20,
        "completion_tokens": 18,
        "total_tokens": 38
    }
}

def parse_ai_response(response: dict) -> dict:
    """解析AI API响应，提取关键信息"""
    return {
        "content": response["choices"][0]["message"]["content"],
        "finish_reason": response["choices"][0]["finish_reason"],
        "total_tokens": response["usage"]["total_tokens"],
        "model": response["model"],
    }

result = parse_ai_response(mock_response)
print(f"AI回复: {result['content']}")
print(f"结束原因: {result['finish_reason']}")
print(f"消耗Token: {result['total_tokens']}")

print()


# ==================== 3. 列表推导式处理数据 ====================

print("=" * 50)
print("3. 列表推导式（数据批量处理）")
print("=" * 50)

# 场景：批量处理对话历史
messages = [
    {"role": "system", "content": "  你是助手  "},
    {"role": "user", "content": "  你好  "},
    {"role": "assistant", "content": "  你好！  "},
    {"role": "user", "content": ""},          # 空消息
    {"role": "user", "content": "   "},       # 纯空格
]

# 1. 清洗：去除首尾空格 + 过滤空消息
cleaned = [
    {**msg, "content": msg["content"].strip()}
    for msg in messages
    if msg["content"].strip()  # 过滤空内容
]
print(f"清洗前: {len(messages)} 条，清洗后: {len(cleaned)} 条")

# 2. 提取：只取user消息的内容
user_contents = [
    msg["content"]
    for msg in cleaned
    if msg["role"] == "user"
]
print(f"用户消息: {user_contents}")

# 3. 转换：统计每条消息的字符数
with_length = [
    {**msg, "length": len(msg["content"])}
    for msg in cleaned
]
for m in with_length:
    print(f"  [{m['role']}] {m['length']}字: {m['content']}")

print()


# ==================== 4. 数据清洗工具函数 ====================

print("=" * 50)
print("4. 数据清洗工具函数")
print("=" * 50)

def clean_messages(messages: List[Dict]) -> List[Dict]:
    """清洗消息列表：去空格、过滤空消息"""
    return [
        {**msg, "content": msg["content"].strip()}
        for msg in messages
        if isinstance(msg.get("content"), str) and msg["content"].strip()
    ]

def truncate_messages(messages: List[Dict], max_tokens: int = 2000) -> List[Dict]:
    """
    截断消息列表，保留最近的消息（简化版token控制）
    策略：保留system消息 + 尽量多的最近消息
    """
    system_msgs = [m for m in messages if m["role"] == "system"]
    other_msgs = [m for m in messages if m["role"] != "system"]

    # 简单估算：每4个字符约1个token
    total_chars = sum(len(m["content"]) for m in system_msgs)
    result = list(system_msgs)

    # 从最新消息往前保留
    for msg in reversed(other_msgs):
        msg_chars = len(msg["content"])
        if total_chars + msg_chars <= max_tokens * 4:
            result.insert(len(system_msgs), msg)
            total_chars += msg_chars
        else:
            break

    return result

def extract_last_reply(response: dict) -> Optional[str]:
    """从API响应中安全提取最后一条回复"""
    try:
        return response["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return None

# 测试
test_msgs = [
    {"role": "system", "content": "你是助手"},
    {"role": "user", "content": "  问题1  "},
    {"role": "assistant", "content": "回答1"},
    {"role": "user", "content": ""},
    {"role": "user", "content": "问题2"},
]

cleaned = clean_messages(test_msgs)
print(f"清洗后消息数: {len(cleaned)}")

reply = extract_last_reply(mock_response)
print(f"提取回复: {reply}")
