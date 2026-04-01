# -*- coding: utf-8 -*-
"""
Day 04 - 单元测试基础示例
知识点：unittest框架、断言方法、测试夹具

运行方式：
    python 03_单元测试.py
    或
    python -m unittest 03_单元测试.py -v
"""

import unittest
from typing import List, Dict, Optional


# ==================== 被测试的函数 ====================

def calculate_area(radius: float) -> float:
    """计算圆面积"""
    if radius < 0:
        raise ValueError("半径不能为负数")
    import math
    return math.pi * radius ** 2


def format_message(role: str, content: str) -> Dict[str, str]:
    """格式化AI对话消息"""
    if role not in ["system", "user", "assistant"]:
        raise ValueError(f"无效角色: {role}")
    return {"role": role, "content": content}


def count_tokens(text: str, avg_chars_per_token: int = 4) -> int:
    """估算token数量（简化版）"""
    if not text:
        return 0
    return max(1, len(text) // avg_chars_per_token)


def extract_json_from_response(response: str) -> Optional[str]:
    """从AI响应中提取JSON内容"""
    import re
    # 匹配 ```json ... ``` 格式
    match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
    if match:
        return match.group(1).strip()
    return None


# ==================== 测试类 ====================

class TestCalculateArea(unittest.TestCase):
    """测试圆面积计算函数"""
    
    def test_positive_radius(self):
        """测试正数半径"""
        self.assertAlmostEqual(calculate_area(1), 3.14159, places=4)
        self.assertAlmostEqual(calculate_area(2), 12.56637, places=4)
    
    def test_zero_radius(self):
        """测试零半径"""
        self.assertEqual(calculate_area(0), 0)
    
    def test_negative_radius(self):
        """测试负数半径应抛出异常"""
        with self.assertRaises(ValueError):
            calculate_area(-1)


class TestFormatMessage(unittest.TestCase):
    """测试消息格式化函数"""
    
    def test_valid_roles(self):
        """测试有效角色"""
        msg = format_message("user", "你好")
        self.assertEqual(msg["role"], "user")
        self.assertEqual(msg["content"], "你好")
    
    def test_invalid_role(self):
        """测试无效角色应抛出异常"""
        with self.assertRaises(ValueError):
            format_message("guest", "你好")


class TestCountTokens(unittest.TestCase):
    """测试token计数函数"""
    
    def test_empty_string(self):
        """测试空字符串"""
        self.assertEqual(count_tokens(""), 0)
    
    def test_short_string(self):
        """测试短字符串"""
        self.assertEqual(count_tokens("hi"), 1)  # 至少返回1
    
    def test_normal_string(self):
        """测试普通字符串"""
        # 12个英文字符 / 4 = 3 tokens
        self.assertEqual(count_tokens("Test message"), 3)
    
    def test_custom_ratio(self):
        """测试自定义字符/token比率"""
        # 8个字符 / 2 = 4 tokens
        self.assertEqual(count_tokens("测试文本测试文本", avg_chars_per_token=2), 4)


class TestExtractJson(unittest.TestCase):
    """测试JSON提取函数"""
    
    def test_valid_json_block(self):
        """测试有效的JSON代码块"""
        response = '这是回复：\n```json\n{"name": "test"}\n```\n结束'
        result = extract_json_from_response(response)
        self.assertEqual(result, '{"name": "test"}')
    
    def test_no_json_block(self):
        """测试没有JSON代码块"""
        response = "这是一段普通文本，没有JSON"
        result = extract_json_from_response(response)
        self.assertIsNone(result)
    
    def test_multiline_json(self):
        """测试多行JSON"""
        response = '```json\n{"name": "test",\n"value": 123}\n```'
        result = extract_json_from_response(response)
        self.assertIn('"name": "test"', result)
        self.assertIn('"value": 123', result)


# ==================== 测试夹具示例 ====================

class TestWithFixture(unittest.TestCase):
    """演示测试夹具（setUp/tearDown）"""
    
    def setUp(self):
        """每个测试方法前执行"""
        print("\n  [setUp] 准备测试数据...")
        self.test_data = [
            {"role": "user", "content": "问题1"},
            {"role": "assistant", "content": "回答1"},
        ]
    
    def tearDown(self):
        """每个测试方法后执行"""
        print("  [tearDown] 清理测试数据...")
        self.test_data = None
    
    def test_data_integrity(self):
        """测试数据完整性"""
        print("  执行测试: test_data_integrity")
        self.assertEqual(len(self.test_data), 2)
        self.assertEqual(self.test_data[0]["role"], "user")
    
    def test_data_append(self):
        """测试数据追加"""
        print("  执行测试: test_data_append")
        self.test_data.append({"role": "user", "content": "问题2"})
        self.assertEqual(len(self.test_data), 3)


# ==================== 主程序入口 ====================

if __name__ == "__main__":
    # 运行所有测试
    # verbosity=2 显示详细信息
    unittest.main(verbosity=2)
