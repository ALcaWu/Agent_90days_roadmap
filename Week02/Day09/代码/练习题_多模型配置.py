# -*- coding: utf-8 -*-
"""
Day 09 - 练习题：多模型配置与切换

完成以下练习，巩固多模型集成知识点。
运行测试：python 练习题.py
"""

import os
import unittest
from typing import Optional


# ==================== 练习1：模型配置类 ====================
# 任务：实现一个模型配置类


class ModelConfig:
    """
    模型配置类

    属性：
        - provider: str, 模型提供商 (openai/anthropic/huggingface)
        - model: str, 模型名称
        - temperature: float, 温度参数
        - max_tokens: int, 最大token数
    """

    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-5.1",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ):
        # TODO: 实现此方法
        # 提示：将参数保存为实例属性
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        pass

    def to_dict(self) -> dict:
        """返回配置字典"""
        # TODO: 实现此方法
        # 提示：返回包含所有属性的字典
        return {
            "provider": self.provider,  # 添加模型提供商参数
            "model": self.model,  # 添加模型名称参数
            "temperature": self.temperature,  # 添加温度参数
            "max_tokens": self.max_tokens,  # 添加最大token数参数
        }
        pass

    @classmethod
    def from_dict(cls, config: dict) -> "ModelConfig":
        """从字典创建配置"""
        # TODO: 实现此类方法
        # 提示：使用 config.get() 获取值，提供默认值
        return ModelConfig(
            provider=config.get(
                "provider", "openai"
            ),  # 使用 get() 方法获取模型提供商参数
            model=config.get("model", "gpt-5.1"),  # 使用 get() 方法获取模型名称参数
            temperature=config.get("temperature", 0.7),  # 使用 get() 方法获取温度参数
            max_tokens=config.get(
                "max_tokens", 1000
            ),  # 使用 get() 方法获取最大token数参数
        )
        pass


# ==================== 练习2：模型工厂 ====================
# 任务：根据配置创建对应的模型实例


def create_chat_model(config: ModelConfig) -> Optional[object]:
    """
    根据 ModelConfig 创建对应的模型

    Args:
        config: ModelConfig 实例

    Returns:
        模型实例，如果失败返回 None
    """
    # TODO: 实现此函数
    # 提示：
    #   1. 检查 provider 类型
    #   2. 根据 provider 导入对应的 ChatModel
    #   3. 检查 API Key 是否存在
    #   4. 创建并返回模型实例
    if os.getenv("OPENAI_API_KEY"):

        if config.provider == "openai":
            from langchain.chat_models import ChatOpenAI

            return ChatOpenAI(
                model_name=config.model,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )
        elif config.provider == "anthropic":
            from langchain.chat_models import ChatAnthropic

            return ChatAnthropic(
                model=config.model,
            )
    else:
        print("请设置 OPENAI_API_KEY 环境变量")
    pass


# ==================== 练习3：模型对比 ====================
# 任务：实现一个简单的模型性能对比器


class ModelBenchmark:
    """
    模型性能对比器

    功能：
        - 记录不同模型的响应时间
        - 统计响应长度
        - 生成对比报告
    """

    def __init__(self):
        # TODO: 初始化结果存储字典
        pass

    def record(
        self, model_name: str, response_time: float, response_length: int
    ) -> None:
        """
        记录单个模型的性能数据

        Args:
            model_name: 模型名称
            response_time: 响应时间（秒）
            response_length: 响应长度（字符数）
        """
        # TODO: 实现此方法
        # 提示：在结果字典中记录数据
        pass

    def get_report(self) -> str:
        """
        生成对比报告

        Returns:
            格式化的对比报告字符串
        """
        # TODO: 实现此方法
        # 提示：遍历结果字典，生成格式化的报告
        pass


# ==================== 练习4：模型切换器 ====================
# 任务：实现一个支持自动切换的模型管理器


class ModelManager:
    """
    模型管理器

    功能：
        - 管理多个模型实例
        - 支持按名称获取模型
        - 支持模型切换
    """

    def __init__(self):
        # TODO: 初始化模型存储字典
        self.models = {}
        pass

    def register(self, name: str, model: object) -> None:
        """
        注册模型

        Args:
            name: 模型名称/别名
            model: 模型实例
        """
        # TODO: 实现此方法
        self.models.add(name, model)
        pass

    def get(self, name: str) -> Optional[object]:
        """
        获取模型

        Args:
            name: 模型名称

        Returns:
            模型实例，不存在返回 None
        """
        # TODO: 实现此方法
        if name in self.models:
            return self.models[name]
        else:
            return None
        pass

    def list_models(self) -> list:
        """
        列出所有已注册的模型名称

        Returns:
            模型名称列表
        """
        # TODO: 实现此方法
        return list(self.models.names)
        pass


# ==================== 单元测试（不要修改） ====================


class TestModelConfig(unittest.TestCase):

    def test_init_with_defaults(self):
        config = ModelConfig()
        self.assertEqual(config.provider, "openai")
        self.assertEqual(config.model, "gpt-5.1")
        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.max_tokens, 1000)

    def test_init_with_custom_values(self):
        config = ModelConfig(
            provider="anthropic", model="claude-3", temperature=0.5, max_tokens=2000
        )
        self.assertEqual(config.provider, "anthropic")
        self.assertEqual(config.model, "claude-3")

    def test_to_dict(self):
        config = ModelConfig(provider="openai", model="gpt-4")
        d = config.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["provider"], "openai")
        self.assertEqual(d["model"], "gpt-4")

    def test_from_dict(self):
        config_dict = {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "temperature": 0.8,
        }
        config = ModelConfig.from_dict(config_dict)
        self.assertEqual(config.provider, "openai")
        self.assertEqual(config.temperature, 0.8)


class TestModelBenchmark(unittest.TestCase):

    def test_record_single(self):
        benchmark = ModelBenchmark()
        benchmark.record("gpt-3.5-turbo", 1.5, 100)
        report = benchmark.get_report()
        self.assertIn("gpt-3.5-turbo", report)
        self.assertIn("1.5", report)

    def test_record_multiple(self):
        benchmark = ModelBenchmark()
        benchmark.record("model-a", 1.0, 50)
        benchmark.record("model-b", 2.0, 100)
        report = benchmark.get_report()
        self.assertIn("model-a", report)
        self.assertIn("model-b", report)


class TestModelManager(unittest.TestCase):

    def test_register_and_get(self):
        manager = ModelManager()
        mock_model = "mock-chat-model"
        manager.register("test", mock_model)
        result = manager.get("test")
        self.assertEqual(result, mock_model)

    def test_get_nonexistent(self):
        manager = ModelManager()
        result = manager.get("not-exist")
        self.assertIsNone(result)

    def test_list_models(self):
        manager = ModelManager()
        manager.register("model1", "obj1")
        manager.register("model2", "obj2")
        models = manager.list_models()
        self.assertEqual(len(models), 2)
        self.assertIn("model1", models)


# ==================== 运行测试 ====================

if __name__ == "__main__":
    print("=" * 50)
    print("Day 09 多模型配置练习题")
    print("=" * 50)
    print()
    unittest.main(verbosity=2)
