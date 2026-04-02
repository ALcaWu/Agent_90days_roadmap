# -*- coding: utf-8 -*-
"""
Day 08 - 练习题：LangChain基础与LLM调用

完成以下练习，巩固今日所学知识点。
运行测试：python 练习题.py
"""

import os
import unittest
from typing import Optional


# ==================== 练习1：环境变量检查 ====================
# 任务：实现一个函数，检查OPENAI_API_KEY是否正确配置


def check_api_key() -> dict:
    """
    检查 OPENAI_API_KEY 环境变量

    Returns:
        dict: {
            "exists": bool,      # 是否存在
            "valid": bool,       # 格式是否正确
            "masked": str        # 遮蔽后的key（如 sk-xxx...xxxx）
        }
    """

    api_key_0 = os.getenv("OPENAI_API_KEY")
    return {
        "exists": bool(api_key_0),
        "valid": bool(api_key_0 and api_key_0.startswith("sk-")),
        "masked": api_key_0[:7] + "..." + api_key_0[-4:] if api_key_0 else None,
    }
    # TODO: 实现此函数
    # 提示：
    #   1. 使用 os.getenv("OPENAI_API_KEY") 获取环境变量
    #   2. 检查是否存在且以 "sk-" 开头
    #   3. 遮蔽显示：保留前7位和后4位
    pass


# ==================== 练习2：LLM配置工厂 ====================
# 任务：实现一个LLM创建函数


def create_llm(
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
    max_tokens: int = 1000,
) -> Optional[object]:
    """
    创建并返回 ChatOpenAI 实例

    Args:
        model: 模型名称
        temperature: 温度参数
        max_tokens: 最大token数

    Returns:
        ChatOpenAI 实例，如果 API Key 未配置则返回 None
    """
    if check_api_key()["exists"]:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            base_url=os.getenv("OPENAI_API_BASE"),
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    # TODO: 实现此函数
    # 提示：
    #   1. 先检查 API Key 是否存在
    #   2. 导入 ChatOpenAI
    #   3. 创建并返回实例
    pass


# ==================== 练习3：消息构建器 ====================
# 任务：实现一个消息列表构建函数


def build_messages(
    user_input: str,
    system_prompt: Optional[str] = None,
    history: Optional[list] = None,
) -> list:
    """
    构建消息列表

    Args:
        user_input: 用户输入
        system_prompt: 系统提示（可选）
        history: 历史消息列表（可选）

    Returns:
        消息列表，格式如下：
        [
            SystemMessage(content="..."),  # 如果有 system_prompt
            ... history 中的消息 ...,
            HumanMessage(content=user_input)
        ]
    """
    from langchain_core.messages import SystemMessage, HumanMessage

    messages = []
    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))
    if history:
        messages.extend(history)

    messages.append(HumanMessage(content=user_input))
    return messages
    # TODO: 实现此函数
    # 提示：
    #   1. 导入 HumanMessage, SystemMessage
    #   2. 按顺序添加消息
    #   3. 返回消息列表
    pass


# ==================== 练习4：LLM响应解析器 ====================
# 任务：实现一个解析LLM响应的函数


def parse_llm_response(response) -> dict:
    """
    解析 LLM 响应对象

    Args:
        response: LLM 响应对象（AIMessage）

    Returns:
        dict: {
            "content": str,           # 回复内容
            "model": str,             # 使用的模型
            "token_usage": dict       # token使用情况
        }
    """
    # 提取 content
    content = response.content

    # response_metadata 是字典，不是对象
    metadata = response.response_metadata or {}

    # 从 metadata 中获取模型名称
    model = metadata.get("model_name", "")

    # token_usage 可能在 metadata 中，也可能通过 usage_metadata 获取
    # 优先从 response_metadata 取，其次从 usage_metadata 取
    token_usage = metadata.get("token_usage", {})
    if not token_usage and hasattr(response, "usage_metadata"):
        usage_meta = response.usage_metadata
        if usage_meta:
            token_usage = {
                "prompt_tokens": usage_meta.get("prompt_tokens", 0),
                "completion_tokens": usage_meta.get("completion_tokens", 0),
                "total_tokens": usage_meta.get("total_tokens", 0)
            }

    return {
        "content": content,
        "model": model,
        "token_usage": token_usage
    }
    print(f"模型信息: {str_1}")
    # TODO: 实现此函数
    # 提示：
    #   1. 从 response.content 获取内容
    #   2. 从 response.response_metadata 获取模型和token信息
    #   3. 返回字典
    pass


# ==================== 单元测试（不要修改） ====================


class TestCheckApiKey(unittest.TestCase):

    def test_missing_key(self):
        # 临时移除环境变量
        original = os.environ.pop("OPENAI_API_KEY", None)
        result = check_api_key()
        self.assertFalse(result["exists"])
        # 恢复
        if original:
            os.environ["OPENAI_API_KEY"] = original

    def test_valid_key(self):
        os.environ["OPENAI_API_KEY"] = "sk-test123456789abcdef"
        result = check_api_key()
        self.assertTrue(result["exists"])
        self.assertTrue(result["valid"])
        self.assertIn("sk-", result["masked"])

    def test_invalid_key_format(self):
        os.environ["OPENAI_API_KEY"] = "invalid-key"
        result = check_api_key()
        self.assertTrue(result["exists"])
        self.assertFalse(result["valid"])


class TestBuildMessages(unittest.TestCase):

    def test_user_only(self):
        from langchain_core.messages import HumanMessage

        msgs = build_messages("你好")
        self.assertEqual(len(msgs), 1)
        self.assertIsInstance(msgs[0], HumanMessage)

    def test_with_system(self):
        from langchain_core.messages import HumanMessage, SystemMessage

        msgs = build_messages("你好", system_prompt="你是助手")
        self.assertEqual(len(msgs), 2)
        self.assertIsInstance(msgs[0], SystemMessage)
        self.assertIsInstance(msgs[1], HumanMessage)

    def test_with_history(self):
        from langchain_core.messages import HumanMessage, AIMessage

        history = [
            HumanMessage(content="问题1"),
            AIMessage(content="回答1"),
        ]
        msgs = build_messages("问题2", history=history)
        self.assertEqual(len(msgs), 3)


class TestParseLlmResponse(unittest.TestCase):

    def test_parse_basic_response(self):
        """测试解析基本响应"""
        from langchain_core.messages import AIMessage

        mock_response = AIMessage(content="这是AI的回复")
        mock_response.response_metadata = {
            "model_name": "gpt-3.5-turbo",
            "token_usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }

        result = parse_llm_response(mock_response)

        self.assertEqual(result["content"], "这是AI的回复")
        self.assertEqual(result["model"], "gpt-3.5-turbo")
        self.assertEqual(result["token_usage"]["total_tokens"], 30)

    def test_parse_response_with_usage(self):
        """测试解析包含token使用信息的响应"""
        from langchain_core.messages import AIMessage

        mock_response = AIMessage(content="你好，有什么可以帮你的？")
        mock_response.response_metadata = {
            "model_name": "gpt-4",
            "token_usage": {
                "prompt_tokens": 5,
                "completion_tokens": 15,
                "total_tokens": 20
            }
        }

        result = parse_llm_response(mock_response)

        self.assertIn("你好", result["content"])
        self.assertEqual(result["model"], "gpt-4")
        self.assertEqual(result["token_usage"]["prompt_tokens"], 5)
        self.assertEqual(result["token_usage"]["completion_tokens"], 15)


# ==================== 运行测试 ====================

if __name__ == "__main__":
    print("=" * 50)
    print("Day 08 练习题测试")
    print("=" * 50)
    print()
    unittest.main(verbosity=2)
