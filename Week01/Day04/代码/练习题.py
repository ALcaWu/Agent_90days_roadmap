# -*- coding: utf-8 -*-
"""
Day 04 - 练习题：模块、虚拟环境、单元测试综合练习

完成以下练习，巩固今日所学知识点。
运行测试：python 练习题.py
"""

import unittest
import math
from typing import List, Dict


# ==================== 练习1：模块导入 ====================
# 任务：完成下面的函数，使用math模块计算圆的周长

def calculate_circumference(radius: float) -> float:
    """
    计算圆的周长
    公式：C = 2 * π * r
    
    Args:
        radius: 半径
    
    Returns:
        周长
    
    Raises:
        ValueError: 半径为负数时
    """
    # TODO: 实现此函数
    # 提示：使用 math.pi 和 raise 语句处理负数
    pass


# ==================== 练习2：消息处理 ====================
# 任务：完成消息验证函数

def validate_messages(messages: List[Dict[str, str]]) -> bool:
    """
    验证AI对话消息格式是否正确
    
    有效消息格式：
    - 必须是列表
    - 每个元素必须是字典
    - 每个字典必须有 "role" 和 "content" 键
    - role 必须是 "system", "user", "assistant" 之一
    
    Args:
        messages: 消息列表
    
    Returns:
        True 如果格式正确，否则 False
    """
    # TODO: 实现此函数
    # 提示：
    #   1. 先检查 messages 是否是列表
    #   2. 遍历每个元素，检查是否是字典
    #   3. 检查每个字典是否有 "role" 和 "content" 键
    #   4. 检查 role 是否在合法值 {"system", "user", "assistant"} 中
    pass


# ==================== 练习3：Token估算器 ====================
# 任务：实现更精确的token估算器

class TokenEstimator:
    """
    Token估算器类
    
    属性：
        - chars_per_token: 每个token对应的字符数
    """
    
    def __init__(self, chars_per_token: int = 4):
        """初始化估算器"""
        # TODO: 将 chars_per_token 保存为实例属性
        pass
    
    def estimate(self, text: str) -> int:
        """
        估算文本的token数量
        
        Args:
            text: 输入文本
        
        Returns:
            token数量（至少为0）
        """
        # TODO: 实现此方法
        # 提示：空字符串返回0，否则返回 len(text) // chars_per_token
        pass
    
    def estimate_messages(self, messages: List[Dict[str, str]]) -> int:
        """
        估算消息列表的总token数
        
        Args:
            messages: 消息列表
        
        Returns:
            总token数量
        """
        # TODO: 实现此方法
        # 提示：遍历 messages，累加每个消息 content 的 token 数
        pass


# ==================== 练习4：配置管理模块 ====================
# 任务：创建一个简单的配置管理类

class ConfigManager:
    """
    配置管理器
    
    用于管理Agent的配置参数
    """
    
    def __init__(self):
        """初始化配置管理器"""
        # TODO: 创建一个字典存储配置
        pass
    
    def set(self, key: str, value) -> None:
        """设置配置项"""
        # TODO: 将 key-value 存入字典
        pass
    
    def get(self, key: str, default=None):
        """获取配置项，不存在则返回default"""
        # TODO: 从字典中获取 key，不存在返回 default
        pass
    
    def update(self, config_dict: Dict) -> None:
        """批量更新配置"""
        # TODO: 批量存入字典（提示：dict.update()）
        pass
    
    def to_dict(self) -> Dict:
        """返回所有配置的字典"""
        # TODO: 返回字典的副本（提示：dict() 或 .copy()）
        pass


# ==================== 单元测试 ====================
# 不要修改下面的测试代码

class TestCalculateCircumference(unittest.TestCase):
    
    def test_positive_radius(self):
        self.assertAlmostEqual(calculate_circumference(1), 2 * math.pi, places=4)
        self.assertAlmostEqual(calculate_circumference(2), 4 * math.pi, places=4)
    
    def test_zero_radius(self):
        self.assertEqual(calculate_circumference(0), 0)
    
    def test_negative_radius(self):
        with self.assertRaises(ValueError):
            calculate_circumference(-1)


class TestValidateMessages(unittest.TestCase):
    
    def test_valid_messages(self):
        messages = [
            {"role": "system", "content": "你是助手"},
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！"}
        ]
        self.assertTrue(validate_messages(messages))
    
    def test_empty_list(self):
        self.assertTrue(validate_messages([]))
    
    def test_missing_key(self):
        messages = [{"role": "user"}]  # 缺少content
        self.assertFalse(validate_messages(messages))
    
    def test_invalid_role(self):
        messages = [{"role": "guest", "content": "你好"}]
        self.assertFalse(validate_messages(messages))
    
    def test_not_list(self):
        self.assertFalse(validate_messages("not a list"))


class TestTokenEstimator(unittest.TestCase):
    
    def test_default_ratio(self):
        estimator = TokenEstimator()
        self.assertEqual(estimator.estimate("Test"), 1)  # 4 chars = 1 token
        self.assertEqual(estimator.estimate("TestTest"), 2)  # 8 chars = 2 tokens
    
    def test_custom_ratio(self):
        estimator = TokenEstimator(chars_per_token=2)
        self.assertEqual(estimator.estimate("Test"), 2)  # 4 chars / 2 = 2 tokens
    
    def test_empty_string(self):
        estimator = TokenEstimator()
        self.assertEqual(estimator.estimate(""), 0)
    
    def test_messages_estimation(self):
        estimator = TokenEstimator(chars_per_token=4)
        messages = [
            {"role": "user", "content": "Test"},      # 4 chars = 1 token
            {"role": "assistant", "content": "Demo"}  # 4 chars = 1 token
        ]
        self.assertEqual(estimator.estimate_messages(messages), 2)


class TestConfigManager(unittest.TestCase):
    
    def test_set_and_get(self):
        config = ConfigManager()
        config.set("model", "gpt-4")
        self.assertEqual(config.get("model"), "gpt-4")
    
    def test_get_default(self):
        config = ConfigManager()
        self.assertIsNone(config.get("not_exist"))
        self.assertEqual(config.get("not_exist", "default"), "default")
    
    def test_update(self):
        config = ConfigManager()
        config.update({"model": "gpt-4", "temperature": 0.7})
        self.assertEqual(config.get("model"), "gpt-4")
        self.assertEqual(config.get("temperature"), 0.7)
    
    def test_to_dict(self):
        config = ConfigManager()
        config.set("model", "gpt-4")
        result = config.to_dict()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["model"], "gpt-4")


# ==================== 运行测试 ====================

if __name__ == "__main__":
    print("=" * 50)
    print("Day 04 练习题测试")
    print("=" * 50)
    print()
    
    # 运行测试
    unittest.main(verbosity=2)
