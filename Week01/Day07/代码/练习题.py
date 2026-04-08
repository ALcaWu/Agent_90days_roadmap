# -*- coding: utf-8 -*-
"""
Day 07 - 练习题：Git操作 + Week01综合

完成以下练习，巩固本周所学。
运行测试：python 练习题.py
"""

import re
import json
import unittest
from pathlib import Path
from typing import List, Dict, Optional


# ==================== 练习1：Git命令判断 ====================
# 任务：根据场景描述，返回正确的Git命令字符串
# 不需要真正执行，只需返回正确的命令字符串


def git_command_for(scenario: str) -> str:
    """
    根据场景返回对应的Git命令

    场景列表：
      "init"          → 初始化仓库
      "stage_all"     → 暂存所有修改
      "commit"        → 提交，消息为 "feat: 初始化项目"
      "status"        → 查看仓库状态
      "log"           → 查看简洁历史（oneline格式）
      "undo_commit"   → 撤销最近一次提交（保留改动）
      "new_branch"    → 创建并切换到 feature/week02 分支

    Args:
        scenario: 场景名称

    Returns:
        对应的Git命令字符串
    """
    # TODO: 实现此函数
    "git init"
    "git stage ."
    # 提示：用字典映射 scenario → 命令字符串
    pass


# ==================== 练习2：.gitignore规则判断 ====================
# 任务：判断给定文件路径是否应该被gitignore忽略
# 根据AI项目的标准规则判断


def should_ignore(filepath: str) -> bool:
    """
    判断文件是否应该被.gitignore忽略

    忽略规则（AI项目标准）：
      - venv/ 或 .venv/ 目录下的文件
      - .env 文件（任意位置）
      - __pycache__ 目录下的文件
      - .pyc 结尾的文件
      - .log 结尾的文件
      - .DS_Store 文件

    Args:
        filepath: 文件路径字符串（使用 / 分隔）

    Returns:
        True 表示应该忽略，False 表示应该提交
    """
    # TODO: 实现此函数
    # 提示：用 any() + 条件列表，逐条检查规则
    pass


# ==================== 练习3：对话历史管理器 ====================
# 任务：实现一个带token预算的对话历史管理器


class BudgetedHistory:
    """
    带token预算的对话历史管理器

    规则：
      - 每条消息的token数 = len(content) // 4
      - 添加消息时，若超出预算，从最旧的非system消息开始删除
      - system消息永远保留
    """

    def __init__(self, max_tokens: int = 500):
        # TODO: 初始化消息列表和max_tokens
        pass

    def _estimate_tokens(self, content: str) -> int:
        """估算token数"""
        # TODO: 返回 len(content) // 4，最小为1
        pass

    def _total_tokens(self) -> int:
        """计算当前所有消息的总token数"""
        # TODO: 累加所有消息content的token数
        pass

    def add(self, role: str, content: str) -> None:
        """
        添加消息，超出预算时自动删除最旧的非system消息
        """
        # TODO: 实现此方法
        # 步骤：
        #   1. 追加新消息
        #   2. 循环检查：若总token超出预算，删除第一条非system消息
        pass

    def get_messages(self) -> List[Dict]:
        """返回消息列表副本"""
        # TODO: 实现此方法
        pass

    def token_usage(self) -> dict:
        """返回token使用情况"""
        # TODO: 返回 {"used": 当前token数, "max": 最大token数, "remaining": 剩余}
        pass


# ==================== 练习4：AI回复解析器 ====================
# 任务：从AI回复文本中提取结构化信息


def parse_ai_reply(text: str) -> dict:
    """
    解析AI回复，提取结构化信息

    提取规则：
      - code_blocks: 所有 ```...``` 代码块内容列表
      - has_list: 是否包含markdown列表（以 - 或数字. 开头的行）
      - word_count: 总字符数（不含空格）
      - languages: 代码块中出现的语言列表（如 ```python → "python"）

    Args:
        text: AI回复文本

    Returns:
        包含上述字段的字典
    """
    # TODO: 实现此函数
    # 提示：
    #   code_blocks: re.findall(r'```(?:\w+)?\n([\s\S]*?)```', text)
    #   languages:   re.findall(r'```(\w+)', text)
    #   has_list:    re.search(r'(?m)^(\s*[-*]|\d+\.)\s', text)
    #   word_count:  len(text.replace(' ', '').replace('\n', ''))
    pass


# ==================== 单元测试（不要修改） ====================


class TestGitCommands(unittest.TestCase):

    def test_init(self):
        self.assertEqual(git_command_for("init"), "git init")

    def test_stage_all(self):
        self.assertEqual(git_command_for("stage_all"), "git add .")

    def test_commit(self):
        self.assertEqual(git_command_for("commit"), 'git commit -m "feat: 初始化项目"')

    def test_status(self):
        self.assertEqual(git_command_for("status"), "git status")

    def test_log(self):
        self.assertEqual(git_command_for("log"), "git log --oneline")

    def test_undo_commit(self):
        self.assertEqual(git_command_for("undo_commit"), "git reset --soft HEAD~1")

    def test_new_branch(self):
        self.assertEqual(
            git_command_for("new_branch"), "git checkout -b feature/week02"
        )


class TestShouldIgnore(unittest.TestCase):

    def test_venv(self):
        self.assertTrue(should_ignore("venv/lib/python3.11/site.py"))

    def test_dotenv(self):
        self.assertTrue(should_ignore(".env"))
        self.assertTrue(should_ignore("config/.env"))

    def test_pycache(self):
        self.assertTrue(should_ignore("src/__pycache__/main.cpython-311.pyc"))

    def test_pyc(self):
        self.assertTrue(should_ignore("main.pyc"))

    def test_log(self):
        self.assertTrue(should_ignore("app.log"))

    def test_ds_store(self):
        self.assertTrue(should_ignore(".DS_Store"))

    def test_normal_py(self):
        self.assertFalse(should_ignore("src/agent.py"))

    def test_readme(self):
        self.assertFalse(should_ignore("README.md"))


class TestBudgetedHistory(unittest.TestCase):

    def test_add_within_budget(self):
        h = BudgetedHistory(max_tokens=100)
        h.add("user", "hello")
        self.assertEqual(len(h.get_messages()), 1)

    def test_system_always_kept(self):
        h = BudgetedHistory(max_tokens=10)
        h.add("system", "你是助手")  # ~2 tokens
        h.add("user", "a" * 100)  # 25 tokens，超出预算
        msgs = h.get_messages()
        roles = [m["role"] for m in msgs]
        self.assertIn("system", roles)

    def test_evict_oldest_non_system(self):
        h = BudgetedHistory(max_tokens=20)
        h.add("user", "a" * 40)  # 10 tokens
        h.add("assistant", "b" * 40)  # 10 tokens，共20，刚好
        h.add("user", "c" * 40)  # 再加10，超出，应删除第一条user
        msgs = h.get_messages()
        self.assertEqual(len(msgs), 2)

    def test_token_usage(self):
        h = BudgetedHistory(max_tokens=100)
        h.add("user", "a" * 40)  # 10 tokens
        usage = h.token_usage()
        self.assertEqual(usage["used"], 10)
        self.assertEqual(usage["max"], 100)
        self.assertEqual(usage["remaining"], 90)


class TestParseAiReply(unittest.TestCase):

    def test_code_blocks(self):
        text = "示例：\n```python\nprint('hi')\n```"
        result = parse_ai_reply(text)
        self.assertEqual(len(result["code_blocks"]), 1)

    def test_languages(self):
        text = "```python\npass\n```\n```bash\nls\n```"
        result = parse_ai_reply(text)
        self.assertIn("python", result["languages"])
        self.assertIn("bash", result["languages"])

    def test_has_list_true(self):
        text = "步骤：\n- 第一步\n- 第二步"
        result = parse_ai_reply(text)
        self.assertTrue(result["has_list"])

    def test_has_list_false(self):
        text = "这是普通段落文本。"
        result = parse_ai_reply(text)
        self.assertFalse(result["has_list"])

    def test_word_count(self):
        text = "hello world"  # 去掉空格后10个字符
        result = parse_ai_reply(text)
        self.assertEqual(result["word_count"], 10)


# ==================== 运行测试 ====================

if __name__ == "__main__":
    print("=" * 50)
    print("Day 07 练习题测试（Week01综合）")
    print("=" * 50)
    print()
    unittest.main(verbosity=2)
