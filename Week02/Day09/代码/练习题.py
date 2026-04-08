# -*- coding: utf-8 -*-
"""
Day 09 - 练习题：ChatModel与模型集成

完成以下练习，巩固今日所学知识点。
运行测试：python 练习题.py
"""

import os
import unittest
from typing import Optional


# ==================== 练习1：消息类型识别 ====================
# 任务：根据消息内容判断消息类型


def identify_message_type(message) -> str:
    """
    识别消息类型

    Args:
        message: 消息对象

    Returns:
        str: "human", "ai", 或 "system"
    """
    # TODO: 实现此函数
    # 提示：根据 message.type 返回 "human", "ai", 或 "system"
    if message.type == "human":
        return "human"
    elif message.type == "ai":
        return "ai"
    elif message.type == "system":
        return "system"
    pass


# ==================== 练习2：多轮对话构建 ====================
# 任务：实现一个简单的对话历史管理器

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


class ConversationManager:
    """
    对话历史管理器

    功能：
    - 自动添加 SystemMessage
    - 保存用户和AI的消息历史
    - 获取完整的消息列表
    """

    def __init__(self, system_prompt: str = "你是一个有帮助的助手"):
        # TODO: 初始化消息列表，添加 SystemMessage
        self.message = []
        self.message.append(SystemMessage(content=system_prompt))
        pass

    def add_user_message(self, content: str) -> None:
        """添加用户消息"""
        # TODO: 添加 HumanMessage 到消息列表
        self.message.append(HumanMessage(content=content))
        pass

    def add_ai_message(self, content: str) -> None:
        """添加AI消息"""
        # TODO: 添加 AIMessage 到消息列表

        self.message.append(AIMessage(content=content))
        pass

    def get_messages(self) -> list:
        """获取完整的消息列表"""
        # TODO: 返回消息列表副本
        return self.message.copy()
        pass

    def clear(self) -> None:
        """清空历史（保留system）"""
        # TODO: 只保留第一条 SystemMessage
        self.message = [self.message[0]]
        pass


# ==================== 练习3：模型配置工厂 ====================
# 任务：实现一个根据配置创建模型的函数


def create_model_from_config(config: dict) -> Optional[object]:
    """
    根据配置创建模型

    Args:
        config: 配置字典，如 {"provider": "openai", "model": "gpt-3.5-turbo", "temperature": 0.7}

    Returns:
        模型实例，或 None（如果配置无效）
    """
    # TODO: 实现此函数
    # 提示：
    #   1. 从 config 中获取 provider, model, temperature 等参数
    #   2. 根据 provider 选择对应的 ChatModel 类
    #   3. 返回创建的模型实例
    #   4. 如果 provider 不支持或缺少 API Key，返回 None
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and config["provider"] == "openai":
        try:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                provider=config["provider"],
                model=config["model"],
                temperature=config["temperature"],
            )
        except ImportError:
            print("请安装 langchain")
    else:
        None
    pass


# ==================== 练习4：响应解析 ====================
# 任务：解析 ChatModel 的响应


def parse_chat_response(response) -> dict:
    """
    解析 ChatModel 响应

    Args:
        response: ChatModel 返回的 AIMessage 对象

    Returns:
        dict: {
            "content": str,      # 回复内容
            "type": str,         # 消息类型
            "metadata": dict    # 元数据
        }
    """
    # TODO: 实现此函数
    # 提示：从 response 中提取 content, type, response_metadata
    return dict(
        content=response.content,
        type=response.type,
        metadata=response.response_metadata,
    )
    pass


# ==================== 单元测试（不要修改） ====================


class TestIdentifyMessageType(unittest.TestCase):

    def test_human_message(self):
        from langchain_core.messages import HumanMessage

        msg = HumanMessage(content="你好")
        self.assertEqual(identify_message_type(msg), "human")

    def test_ai_message(self):
        from langchain_core.messages import AIMessage

        msg = AIMessage(content="你好")
        self.assertEqual(identify_message_type(msg), "ai")

    def test_system_message(self):
        from langchain_core.messages import SystemMessage

        msg = SystemMessage(content="你是助手")
        self.assertEqual(identify_message_type(msg), "system")


class TestConversationManager(unittest.TestCase):

    def test_initial_system_message(self):
        manager = ConversationManager("你是一个诗人")
        msgs = manager.get_messages()
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].type, "system")

    def test_add_user_and_ai(self):
        manager = ConversationManager()
        manager.add_user_message("你好")
        manager.add_ai_message("你好，有什么可以帮你的？")
        msgs = manager.get_messages()
        self.assertEqual(len(msgs), 3)  # system + user + ai

    def test_clear_keeps_system(self):
        manager = ConversationManager()
        manager.add_user_message("你好")
        manager.add_ai_message("回复")
        manager.clear()
        msgs = manager.get_messages()
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].type, "system")


class TestCreateModelFromConfig(unittest.TestCase):

    def test_openai_config(self):
        config = {"provider": "openai", "model": "gpt-3.5-turbo", "temperature": 0.7}
        # 需要 API Key 才能创建成功
        if os.getenv("OPENAI_API_KEY"):
            model = create_model_from_config(config)
            self.assertIsNotNone(model)
        else:
            # 没有 API Key 时应返回 None
            model = create_model_from_config(config)
            self.assertIsNone(model)

    def test_unsupported_provider(self):
        config = {"provider": "unknown", "model": "some-model"}
        model = create_model_from_config(config)
        self.assertIsNone(model)


class TestParseChatResponse(unittest.TestCase):

    def test_parse_basic_response(self):
        from langchain_core.messages import AIMessage

        response = AIMessage(content="这是回复")
        result = parse_chat_response(response)

        self.assertEqual(result["content"], "这是回复")
        self.assertEqual(result["type"], "ai")

    def test_parse_with_metadata(self):
        from langchain_core.messages import AIMessage

        response = AIMessage(content="测试")
        response.response_metadata = {"model_name": "gpt-3.5-turbo"}

        result = parse_chat_response(response)

        self.assertEqual(result["content"], "测试")
        self.assertEqual(result["metadata"]["model_name"], "gpt-3.5-turbo")


# ==================== 运行测试 ====================

if __name__ == "__main__":
    print("=" * 50)
    print("Day 09 练习题测试")
    print("=" * 50)
    print()
    unittest.main(verbosity=2)
