# -*- coding: utf-8 -*-
"""
Day 07 - Week01 综合复盘
串联 Day01~Day06 所有核心知识点：
  Day01: 基础语法、数据结构、函数
  Day02: 面向对象、装饰器、异常处理
  Day03: 文件操作、正则表达式
  Day04: 模块、虚拟环境、单元测试
  Day05: requests、JSON处理、API调用
  Day06: asyncio、async/await、并发
"""

import re
import json
import time
import asyncio
import unittest
from pathlib import Path
from typing import List, Dict, Optional
from functools import wraps


# ==================== Day01: 数据结构 + 函数 ====================

def build_chat_payload(
    user_input: str,
    system_prompt: str = "你是一个AI助手",
    model: str = "gpt-4",
    temperature: float = 0.7,
    history: Optional[List[Dict]] = None,
) -> dict:
    """
    构造对话请求体（综合：函数参数 + 数据结构 + JSON）
    """
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_input})

    return {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }


# ==================== Day02: 面向对象 + 装饰器 ====================

def timer(func):
    """计时装饰器（Day02：装饰器）"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"  [{func.__name__}] 耗时: {elapsed:.3f}s")
        return result
    return wrapper


class ConversationHistory:
    """
    对话历史管理器（Day02：面向对象）
    负责维护多轮对话的消息列表
    """

    def __init__(self, max_turns: int = 10):
        self._messages: List[Dict] = []
        self.max_turns = max_turns

    def add(self, role: str, content: str) -> None:
        if role not in ("user", "assistant", "system"):
            raise ValueError(f"无效角色: {role}")
        self._messages.append({"role": role, "content": content})
        # 超出最大轮数时，保留system消息 + 最近的消息
        non_system = [m for m in self._messages if m["role"] != "system"]
        if len(non_system) > self.max_turns * 2:
            system = [m for m in self._messages if m["role"] == "system"]
            self._messages = system + non_system[-(self.max_turns * 2):]

    def get_messages(self) -> List[Dict]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()

    def __len__(self) -> int:
        return len(self._messages)


# ==================== Day03: 文件操作 + 正则 ====================

def save_conversation(history: ConversationHistory, filepath: str) -> None:
    """保存对话历史到JSON文件（Day03：文件操作）"""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history.get_messages(), f, ensure_ascii=False, indent=2)


def load_conversation(filepath: str) -> List[Dict]:
    """从文件加载对话历史（Day03：文件操作）"""
    path = Path(filepath)
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_code_blocks(text: str) -> List[str]:
    """从AI回复中提取代码块（Day03：正则表达式）"""
    pattern = r"```(?:\w+)?\n([\s\S]*?)```"
    return re.findall(pattern, text)


def validate_api_key(key: str) -> bool:
    """验证API Key格式（Day03：正则）"""
    # OpenAI格式: sk- 开头，后跟48位字母数字
    return bool(re.match(r"^sk-[A-Za-z0-9]{48}$", key))


# ==================== Day04: 单元测试 ====================

class TestChatComponents(unittest.TestCase):
    """Week01综合测试（Day04：单元测试）"""

    def test_build_payload_structure(self):
        payload = build_chat_payload("你好")
        self.assertIn("model", payload)
        self.assertIn("messages", payload)
        self.assertEqual(payload["messages"][-1]["role"], "user")

    def test_conversation_history_add(self):
        history = ConversationHistory()
        history.add("user", "你好")
        history.add("assistant", "你好！")
        self.assertEqual(len(history), 2)

    def test_conversation_invalid_role(self):
        history = ConversationHistory()
        with self.assertRaises(ValueError):
            history.add("guest", "非法角色")

    def test_extract_code_blocks(self):
        text = "这是代码：\n```python\nprint('hello')\n```"
        blocks = extract_code_blocks(text)
        self.assertEqual(len(blocks), 1)
        self.assertIn("print", blocks[0])

    def test_validate_api_key(self):
        valid_key = "sk-" + "a" * 48
        self.assertTrue(validate_api_key(valid_key))
        self.assertFalse(validate_api_key("invalid-key"))


# ==================== Day05+06: 异步模拟调用 ====================

async def mock_llm_call(prompt: str, delay: float = 0.1) -> str:
    """模拟异步LLM调用（Day06：asyncio）"""
    await asyncio.sleep(delay)
    return f"[模拟回复] 收到：{prompt[:20]}..."


@timer
def run_sequential(prompts: List[str]) -> List[str]:
    """顺序执行（对比用）"""
    results = []
    for p in prompts:
        time.sleep(0.1)
        results.append(f"[模拟回复] 收到：{p[:20]}...")
    return results


@timer
def run_concurrent(prompts: List[str]) -> List[str]:
    """并发执行（Day06：asyncio.gather）"""
    async def _run():
        tasks = [mock_llm_call(p) for p in prompts]
        return await asyncio.gather(*tasks)
    return asyncio.run(_run())


# ==================== 主程序：串联演示 ====================

if __name__ == "__main__":
    print("=" * 55)
    print("Week01 综合复盘演示")
    print("=" * 55)

    # 1. 构造请求体
    print("\n【Day01+05】构造对话请求体")
    payload = build_chat_payload("什么是LangChain？", model="gpt-4")
    print(f"  模型: {payload['model']}")
    print(f"  消息数: {len(payload['messages'])}")

    # 2. 对话历史管理
    print("\n【Day02】对话历史管理")
    history = ConversationHistory(max_turns=5)
    history.add("user", "你好")
    history.add("assistant", "你好！有什么可以帮你？")
    history.add("user", "什么是RAG？")
    print(f"  当前消息数: {len(history)}")

    # 3. 文件操作
    print("\n【Day03】保存/加载对话历史")
    save_path = r"D:\AgentDeveloperCourse\Week01\Day07\代码\test_history.json"
    save_conversation(history, save_path)
    loaded = load_conversation(save_path)
    print(f"  保存并加载成功，共 {len(loaded)} 条消息")

    # 4. 正则提取
    print("\n【Day03】正则提取代码块")
    ai_reply = "用法如下：\n```python\nchain = LLMChain(llm=llm)\n```"
    blocks = extract_code_blocks(ai_reply)
    print(f"  提取到 {len(blocks)} 个代码块: {blocks[0].strip()}")

    # 5. 并发对比
    print("\n【Day06】顺序 vs 并发调用对比（5个请求）")
    prompts = [f"问题{i}" for i in range(5)]
    print("  顺序执行:", end=" ")
    run_sequential(prompts)
    print("  并发执行:", end=" ")
    run_concurrent(prompts)

    # 6. 单元测试
    print("\n【Day04】运行单元测试")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestChatComponents)
    runner = unittest.TextTestRunner(verbosity=0, stream=open("nul", "w"))
    result = runner.run(suite)
    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    status = "全部通过" if passed == total else "存在失败"
    print(f"  测试结果: {passed}/{total} 通过 [{status}]")

    print("\n" + "=" * 55)
    print("Week01 全部知识点串联完成！")
    print("=" * 55)
