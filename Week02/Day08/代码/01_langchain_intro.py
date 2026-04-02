# -*- coding: utf-8 -*-
"""
Day 08 - LangChain核心概念与架构
知识点：LangChain是什么、核心组件、组件关系
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os


# ==================== 1. LangChain 核心组件 ====================
"""
LangChain 四大核心组件：

1. LLM (Language Model)
   - 大语言模型封装（OpenAI、Claude等）
   - 支持文本生成与对话

2. Chain (链)
   - 将多个组件串联成工作流
   - LLMChain 是最基础的链

3. Agent (代理)
   - 自主决策的智能体
   - 可以调用工具完成复杂任务

4. Memory (记忆)
   - 对话历史管理
   - 短期记忆/长期记忆
"""

print("=" * 50)
print("LangChain 核心组件")
print("=" * 50)

components = """
┌─────────────────────────────────────────────────┐
│                   LangChain                      │
├─────────────────────────────────────────────────┤
│  LLM      │  Chain    │  Agent   │  Memory     │
│  (模型)    │  (链)     │  (代理)  │  (记忆)     │
├───────────┴───────────┴──────────┴─────────────┤
│                     Tools (工具)                 │
└─────────────────────────────────────────────────┘
"""
print(components)


# ==================== 2. 组件之间的关系 ====================
"""
组件调用流程示例：

1. 用户输入 → Memory(读取历史)
2. Memory + 输入 → Chain(组装Prompt)
3. Chain → LLM(调用模型)
4. LLM返回 → Chain(解析输出)
5. 输出 → Memory(保存历史)
6. 输出 → 用户

简单调用：User → LLM → Output
完整调用：User → Memory → Chain → LLM → Chain → Memory → Output
"""

print("\n" + "=" * 50)
print("组件调用流程")
print("=" * 50)

flow = """
# 简单调用（无需Memory）
llm = ChatOpenAI()
response = llm.invoke("你好")

# 完整调用（带Memory）
# 1. Memory 读取历史对话
# 2. Chain 组装 Prompt（历史 + 当前输入）
# 3. LLM 生成响应
# 4. Memory 保存当前对话
"""
print(flow)


# ==================== 3. 快速体验 LangChain ====================

print("\n" + "=" * 50)
print("快速体验 LangChain")
print("=" * 50)

# 检查是否有API Key
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    # 初始化LLM
    llm = ChatOpenAI(
        base_url="https://gpt.qt.cool/v1",
        model="gpt-5.1",
        temperature=0.7,
    )

    # 简单调用
    response = llm.invoke("LangChain是什么？")
    print(f"回复: {response.content}")

    # 带系统提示的调用
    llm_with_system = ChatOpenAI(
        base_url="https://gpt.qt.cool/v1",
        model="gpt-5.1",
        temperature=0.7,
    )
    messages = [
        SystemMessage(content="你是一个Python编程助手"),
        HumanMessage(content="什么是装饰器？"),
    ]
    response = llm_with_system.invoke(messages)
    print(f"\n带系统提示的回复: {response.content}")
else:
    print("提示: 未设置 OPENAI_API_KEY 环境变量")
    print("请在 .env 文件中设置: OPENAI_API_KEY=sk-xxx")
    print("\n跳过实际API调用，仅展示代码结构")


# ==================== 4. LangChain 生态 ====================

print("\n" + "=" * 50)
print("LangChain 生态概览")
print("=" * 50)

ecosystem = """
LangChain 生态模块：

- langchain-core:       核心抽象与基类
- langchain-openai:     OpenAI 模型集成
- langchain-anthropic: Anthropic (Claude) 集成
- langchain-community:  社区贡献的组件
- langchain-text-splitters: 文本切分

常用扩展：
- langchainhub:      预制Prompts和Chains
- langsmith:         应用监控与调试
- langserve:         部署为API服务
"""
print(ecosystem)
