# -*- coding: utf-8 -*-
"""
Day 09 - 多模型集成与切换
知识点：统一接口、多模型切换、模型对比
"""

import os
from typing import Optional


# ==================== 1. 统一模型接口 ====================

print("=" * 50)
print("1. 统一模型接口")
print("=" * 50)

unified_interface = """
LangChain 的优势：统一接口

不管使用哪个模型，调用方式都是一样的：

# OpenAI
from langchain_openai import ChatOpenAI
chat = ChatOpenAI()
response = chat.invoke(messages)

# Anthropic (Claude)
from langchain_anthropic import ChatAnthropic
chat = ChatAnthropic()
response = chat.invoke(messages)

# HuggingFace
from langchain_community.chat_models import ChatHuggingFace
chat = ChatHuggingFace()
response = chat.invoke(messages)

这就是 LangChain 的"模型无关"特性！
"""
print(unified_interface)


# ==================== 2. 模型工厂函数 ====================

print("\n" + "=" * 50)
print("2. 模型工厂函数")
print("=" * 50)


def create_chat_model(
    provider: str = "openai", model: str = "gpt-3.5-turbo", **kwargs
) -> Optional[object]:
    """
    统一的模型创建函数

    Args:
        provider: 提供商 (openai/anthropic/huggingface)
        model: 模型名称
        **kwargs: 其他参数

    Returns:
        ChatModel 实例
    """
    if provider == "openai":
        try:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(model=model, **kwargs)
        except ImportError:
            print("请安装: pip install langchain-openai")
            return None

    elif provider == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic

            # Claude 使用 anthropic- 开头的模型名
            return ChatAnthropic(model=model, **kwargs)
        except ImportError:
            print("请安装: pip install langchain-anthropic")
            return None

    elif provider == "huggingface":
        try:
            from langchain_community.chat_models import ChatHuggingFace

            return ChatHuggingFace(model=model, **kwargs)
        except ImportError:
            print("请安装: pip install langchain-community")
            return None

    else:
        print(f"不支持的 provider: {provider}")
        return None


# 测试工厂函数
print("测试模型工厂函数:")
models = [
    {"provider": "openai", "model": "gpt-3.5-turbo"},
    {"provider": "anthropic", "model": "claude-3-sonnet-20240229"},
    {"provider": "huggingface", "model": "microsoft/phi-2"},
]

for cfg in models:
    # 不实际创建，只展示配置
    print(f"  配置: {cfg['provider']} - {cfg['model']}")


# ==================== 3. 模型切换示例 ====================

print("\n" + "=" * 50)
print("3. 模型切换示例")
print("=" * 50)

switch_example = """
# 定义消息
messages = [
    SystemMessage(content="你是一个助手"),
    HumanMessage(content="1+1等于多少？")
]

# 切换 OpenAI
chat_openai = create_chat_model("openai", "gpt-3.5-turbo")
if chat_openai:
    response = chat_openai.invoke(messages)
    print(f"OpenAI: {response.content}")

# 切换 Claude（需要配置 ANTHROPIC_API_KEY）
chat_claude = create_chat_model("anthropic", "claude-3-sonnet-20240229")
if chat_claude:
    response = chat_claude.invoke(messages)
    print(f"Claude: {response.content}")
"""
print(switch_example)


# ==================== 4. 模型对比工具 ====================

print("\n" + "=" * 50)
print("4. 模型对比工具")
print("=" * 50)


class ModelComparator:
    """简单的模型对比工具"""

    def __init__(self):
        self.results = {}

    def add_result(self, model_name: str, response: str, time_taken: float):
        """添加模型结果"""
        self.results[model_name] = {
            "response": response,
            "time": time_taken,
            "length": len(response),
        }

    def compare(self):
        """对比所有模型结果"""
        print("\n模型对比结果:")
        print("-" * 60)
        for name, result in self.results.items():
            print(f"模型: {name}")
            print(f"  响应长度: {result['length']} 字符")
            print(f"  耗时: {result['time']:.2f}秒")
            print(f"  回复: {result['response'][:80]}...")
            print()


# 演示
comparator = ModelComparator()
print("ModelComparator 用法示例:")
print(
    """
comparator = ModelComparator()

# 添加各个模型的结果
comparator.add_result("gpt-3.5-turbo", "回复内容1", 1.5)
comparator.add_result("gpt-4", "回复内容2", 3.2)

# 对比结果
comparator.compare()
"""
)


# ==================== 5. 模型选择策略 ====================

print("\n" + "=" * 50)
print("5. 模型选择策略")
print("=" * 50)

selection_strategy = """
模型选择考虑因素:

1. 任务复杂度
   - 简单对话: gpt-3.5-turbo (便宜快速)
   - 复杂推理: gpt-4 (能力强)
   - 代码生成: gpt-4 (代码能力更强)

2. 成本
   - gpt-3.5-turbo: ~$0.002/1K tokens
   - gpt-4: ~$0.03/1K tokens (15倍)
   - gpt-4-turbo: ~$0.01/1K tokens

3. 响应速度
   - gpt-3.5-turbo 最快
   - gpt-4 较慢但质量高

4. 特殊需求
   - 长上下文: gpt-4-32k
   - 多模态: gpt-4-vision

建议:
  - 开发测试用 gpt-3.5-turbo
  - 生产根据质量要求选择
  - 可以先用便宜的，必要时升级
"""
print(selection_strategy)


# ==================== 6. 环境变量配置 ====================

print("\n" + "=" * 50)
print("6. 各模型环境变量")
print("=" * 50)

env_config = """
各模型需要的API Key:

OpenAI:
  - 环境变量: OPENAI_API_KEY
  - 模型: gpt-3.5-turbo, gpt-4, gpt-4-turbo

Anthropic:
  - 环境变量: ANTHROPIC_API_KEY
  - 模型: claude-3-opus, claude-3-sonnet, claude-3-haiku

Google (Gemini):
  - 环境变量: GOOGLE_API_KEY
  - 模型: gemini-pro, gemini-pro-vision

HuggingFace:
  - 环境变量: HF_TOKEN (部分模型需要)
  - 模型: 各种开源模型

Azure OpenAI:
  - 环境变量: AZURE_OPENAI_API_KEY
  - 需要额外配置: api_base, api_version
"""
print(env_config)


# ==================== 7. 实际测试 ====================

print("\n" + "=" * 50)
print("7. 实际测试")
print("=" * 50)

# 检查当前环境中的可用模型
available_models = []

# 检查 OpenAI
if os.getenv("OPENAI_API_KEY"):
    try:
        from langchain_openai import ChatOpenAI

        chat = ChatOpenAI()
        available_models.append(f"OpenAI: {chat.model_name}")
    except:
        pass

print(
    f"当前可用模型: {available_models if available_models else '无（需要配置API Key）'}"
)
