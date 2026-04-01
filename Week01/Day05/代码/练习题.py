# -*- coding: utf-8 -*-
"""
Day 05 - 练习题：requests与数据处理综合练习

完成以下练习，巩固今日所学知识点。
运行测试：python 练习题.py
"""

import json
import unittest
from typing import List, Dict, Optional


# ==================== 练习1：解析API响应 ====================
# 任务：从模拟的API响应中安全提取内容
# 要求：
#   - 正常情况返回 choices[0].message.content
#   - 任何键不存在或索引越界时返回 None

def extract_content(response: dict) -> Optional[str]:
    """
    从AI API响应中提取回复内容
    
    Args:
        response: API响应字典
    
    Returns:
        回复内容字符串，失败返回None
    """
    # TODO: 实现此函数
    # 提示：使用 try/except 捕获 KeyError 和 IndexError
    pass


# ==================== 练习2：构造消息列表 ====================
# 任务：实现一个消息构建器
# 要求：
#   - add_system(content)：添加system消息
#   - add_user(content)：添加user消息
#   - add_assistant(content)：添加assistant消息
#   - build()：返回消息列表
#   - clear()：清空消息列表

class MessageBuilder:
    """消息列表构建器"""

    def __init__(self):
        # TODO: 初始化一个空列表存储消息
        pass

    def add_system(self, content: str) -> "MessageBuilder":
        """添加system消息，返回self支持链式调用"""
        # TODO: 实现此方法
        # 提示：追加 {"role": "system", "content": content}
        pass

    def add_user(self, content: str) -> "MessageBuilder":
        """添加user消息，返回self支持链式调用"""
        # TODO: 实现此方法
        pass

    def add_assistant(self, content: str) -> "MessageBuilder":
        """添加assistant消息，返回self支持链式调用"""
        # TODO: 实现此方法
        pass

    def build(self) -> List[Dict[str, str]]:
        """返回消息列表的副本"""
        # TODO: 实现此方法
        pass

    def clear(self) -> "MessageBuilder":
        """清空消息列表，返回self"""
        # TODO: 实现此方法
        pass


# ==================== 练习3：数据清洗 ====================
# 任务：清洗一批原始消息数据
# 要求：
#   - 去除content首尾空格
#   - 过滤掉content为空的消息
#   - 过滤掉role不合法的消息（合法值：system/user/assistant）
#   - 返回清洗后的列表

def clean_message_list(messages: List[Dict]) -> List[Dict]:
    """
    清洗消息列表
    
    Args:
        messages: 原始消息列表
    
    Returns:
        清洗后的消息列表
    """
    # TODO: 实现此函数
    # 提示：用列表推导式，一步完成过滤+清洗
    pass


# ==================== 练习4：Token统计器 ====================
# 任务：实现一个累计Token用量的统计器
# 要求：
#   - record(response)：从API响应中读取usage并累计
#   - total_tokens：属性，返回总token数
#   - reset()：重置统计
#   - summary()：返回统计摘要字典

class TokenTracker:
    """Token用量追踪器"""

    def __init__(self):
        # TODO: 初始化计数器（prompt_tokens, completion_tokens, total_tokens）
        pass

    def record(self, response: dict) -> None:
        """
        从API响应中提取usage并累计
        
        response格式：
        {
            "usage": {
                "prompt_tokens": 20,
                "completion_tokens": 30,
                "total_tokens": 50
            }
        }
        """
        # TODO: 实现此方法
        # 提示：用 .get() 安全取值，usage不存在时跳过
        pass

    @property
    def total_tokens(self) -> int:
        """返回累计总token数"""
        # TODO: 实现此属性
        pass

    def reset(self) -> None:
        """重置所有计数器"""
        # TODO: 实现此方法
        pass

    def summary(self) -> dict:
        """返回统计摘要"""
        # TODO: 返回包含 prompt_tokens, completion_tokens, total_tokens 的字典
        pass


# ==================== 单元测试（不要修改） ====================

class TestExtractContent(unittest.TestCase):

    def test_normal_response(self):
        resp = {
            "choices": [{"message": {"role": "assistant", "content": "你好"}}]
        }
        self.assertEqual(extract_content(resp), "你好")

    def test_empty_choices(self):
        self.assertIsNone(extract_content({"choices": []}))

    def test_missing_choices(self):
        self.assertIsNone(extract_content({}))

    def test_missing_content(self):
        resp = {"choices": [{"message": {"role": "assistant"}}]}
        self.assertIsNone(extract_content(resp))


class TestMessageBuilder(unittest.TestCase):

    def test_chain_build(self):
        msgs = (
            MessageBuilder()
            .add_system("你是助手")
            .add_user("你好")
            .add_assistant("你好！")
            .build()
        )
        self.assertEqual(len(msgs), 3)
        self.assertEqual(msgs[0]["role"], "system")
        self.assertEqual(msgs[1]["role"], "user")
        self.assertEqual(msgs[2]["role"], "assistant")

    def test_build_returns_copy(self):
        builder = MessageBuilder().add_user("测试")
        msgs1 = builder.build()
        msgs1.append({"role": "user", "content": "额外"})
        msgs2 = builder.build()
        self.assertEqual(len(msgs2), 1)  # 原builder不受影响

    def test_clear(self):
        builder = MessageBuilder().add_user("测试")
        builder.clear()
        self.assertEqual(len(builder.build()), 0)


class TestCleanMessageList(unittest.TestCase):

    def test_strip_whitespace(self):
        msgs = [{"role": "user", "content": "  你好  "}]
        result = clean_message_list(msgs)
        self.assertEqual(result[0]["content"], "你好")

    def test_filter_empty(self):
        msgs = [
            {"role": "user", "content": "你好"},
            {"role": "user", "content": ""},
            {"role": "user", "content": "   "},
        ]
        result = clean_message_list(msgs)
        self.assertEqual(len(result), 1)

    def test_filter_invalid_role(self):
        msgs = [
            {"role": "user", "content": "你好"},
            {"role": "guest", "content": "非法角色"},
        ]
        result = clean_message_list(msgs)
        self.assertEqual(len(result), 1)


class TestTokenTracker(unittest.TestCase):

    def test_record_single(self):
        tracker = TokenTracker()
        tracker.record({"usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}})
        self.assertEqual(tracker.total_tokens, 30)

    def test_record_multiple(self):
        tracker = TokenTracker()
        tracker.record({"usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}})
        tracker.record({"usage": {"prompt_tokens": 5, "completion_tokens": 15, "total_tokens": 20}})
        self.assertEqual(tracker.total_tokens, 50)

    def test_record_missing_usage(self):
        tracker = TokenTracker()
        tracker.record({})  # 没有usage字段，不应报错
        self.assertEqual(tracker.total_tokens, 0)

    def test_reset(self):
        tracker = TokenTracker()
        tracker.record({"usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}})
        tracker.reset()
        self.assertEqual(tracker.total_tokens, 0)

    def test_summary(self):
        tracker = TokenTracker()
        tracker.record({"usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}})
        s = tracker.summary()
        self.assertEqual(s["prompt_tokens"], 10)
        self.assertEqual(s["completion_tokens"], 20)
        self.assertEqual(s["total_tokens"], 30)


# ==================== 运行测试 ====================

if __name__ == "__main__":
    print("=" * 50)
    print("Day 05 练习题测试")
    print("=" * 50)
    print()
    unittest.main(verbosity=2)
