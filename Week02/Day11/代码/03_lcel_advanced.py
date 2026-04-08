# -*- coding: utf-8 -*-
"""
Day 11 - LCEL 进阶：链的组合模式
知识点：顺序链、并行链、RunnablePassthrough、RunnableLambda
"""

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableLambda,
    RunnableParallel,
)
from pydantic import BaseModel, Field
from typing import List


# ==================== 1. LCEL 基础回顾 ====================

print("=" * 50)
print("1. LCEL 核心概念回顾")
print("=" * 50)

lcel_concept = """
LCEL（LangChain Expression Language）= LangChain 表达式语言

核心操作符：`|`（管道符）
语义：将左边的输出作为右边的输入

基本结构：
  chain = prompt | model | parser

每个组件都实现了 Runnable 接口：
  - invoke(input)     同步调用
  - stream(input)     流式输出
  - batch([inputs])   批量调用
  - ainvoke(input)    异步调用

所有 Runnable 可以用 | 自由组合！
"""
print(lcel_concept)


# ==================== 2. RunnablePassthrough ====================

print("=" * 50)
print("2. RunnablePassthrough - 透传原始输入")
print("=" * 50)

# RunnablePassthrough：将输入原封不动地传递给下一步
# 常用于在链中同时保留原始输入和处理后的数据

passthrough = RunnablePassthrough()
result = passthrough.invoke({"key": "value"})
print(f"透传结果：{result}")

# 实际应用：在处理过程中保留上下文
def add_metadata(data: dict) -> dict:
    """模拟：给数据添加元数据"""
    return {**data, "processed": True, "version": "1.0"}

chain_with_passthrough = RunnablePassthrough() | RunnableLambda(add_metadata)
result = chain_with_passthrough.invoke({"text": "原始文本", "user_id": "123"})
print(f"添加元数据后：{result}")


# ==================== 3. RunnableLambda - 自定义函数 ====================

print("\n" + "=" * 50)
print("3. RunnableLambda - 将普通函数变成 Runnable")
print("=" * 50)

# RunnableLambda：将任何 Python 函数包装成 Runnable 组件
def extract_keywords(text: str) -> List[str]:
    """模拟关键词提取（实际会调用 LLM）"""
    # 简单演示：按空格分词取前3个
    words = text.split()
    return words[:3]

def format_for_summary(keywords: List[str]) -> str:
    """将关键词列表格式化为摘要提示词"""
    return f"请基于这些关键词写一段介绍：{', '.join(keywords)}"

# 将函数包装为 Runnable
keyword_extractor = RunnableLambda(extract_keywords)
formatter = RunnableLambda(format_for_summary)

# 组合成链
text_chain = keyword_extractor | formatter

test_text = "LangChain是一个强大的AI开发框架，支持多种语言模型"
print(f"输入文本：{test_text}")
print(f"链式处理结果：{text_chain.invoke(test_text)}")


# ==================== 4. RunnableParallel - 并行执行 ====================

print("\n" + "=" * 50)
print("4. RunnableParallel - 并行执行多个任务")
print("=" * 50)

# RunnableParallel：同时执行多个子链，结果合并成字典
def get_word_count(text: str) -> int:
    """统计字数"""
    return len(text.split())

def get_char_count(text: str) -> int:
    """统计字符数"""
    return len(text)

def get_language(text: str) -> str:
    """简单语言检测"""
    # 检查是否包含中文字符
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return "中文"
    return "英文"

# 并行执行三个分析任务
analysis_chain = RunnableParallel(
    word_count=RunnableLambda(get_word_count),
    char_count=RunnableLambda(get_char_count),
    language=RunnableLambda(get_language),
)

sample_text = "LangChain is an amazing framework for building LLM applications"
result = analysis_chain.invoke(sample_text)
print(f"输入文本：{sample_text}")
print(f"并行分析结果：")
print(f"  字数：{result['word_count']}")
print(f"  字符数：{result['char_count']}")
print(f"  语言：{result['language']}")

# 中文示例
cn_text = "LangChain是一个用于构建大语言模型应用的强大框架"
cn_result = analysis_chain.invoke(cn_text)
print(f"\n中文文本分析：{cn_result}")


# ==================== 5. 组合复杂工作流 ====================

print("\n" + "=" * 50)
print("5. 综合示例：文本处理工作流")
print("=" * 50)

# 模拟一个文本分析流水线（不调用真实 LLM，展示结构）
def preprocess(text: str) -> str:
    """预处理：去除首尾空白"""
    return text.strip()

def to_uppercase_keywords(text: str) -> str:
    """将英文关键词大写（模拟NLP处理）"""
    import re
    # 简单演示：把英文单词变大写
    return re.sub(r'\b[a-z]+\b', lambda m: m.group().upper(), text)

def create_report(data: dict) -> dict:
    """生成分析报告"""
    return {
        "report": {
            "original": data.get("original", ""),
            "processed": data.get("processed", ""),
            "stats": data.get("stats", {}),
        },
        "status": "success"
    }

# 构建工作流
step1 = RunnableLambda(preprocess)

step2 = RunnableParallel(
    original=RunnablePassthrough(),
    processed=RunnableLambda(to_uppercase_keywords),
    stats=RunnableParallel(
        words=RunnableLambda(get_word_count),
        chars=RunnableLambda(get_char_count),
        lang=RunnableLambda(get_language),
    )
)

step3 = RunnableLambda(create_report)

full_workflow = step1 | step2 | step3

input_text = "  langchain is great for building agent applications  "
final_result = full_workflow.invoke(input_text)

print(f"工作流输入：'{input_text}'")
print(f"工作流输出：")
import json
print(json.dumps(final_result, ensure_ascii=False, indent=2))


# ==================== 6. LCEL 调用模式对比 ====================

print("\n" + "=" * 50)
print("6. LCEL 四种调用模式")
print("=" * 50)

simple_chain = RunnableLambda(lambda x: x.upper())

# invoke：同步，返回单个结果
invoke_result = simple_chain.invoke("hello world")
print(f"invoke: {invoke_result}")

# batch：批量处理，返回列表
batch_result = simple_chain.batch(["hello", "world", "langchain"])
print(f"batch: {batch_result}")

# stream 和 ainvoke 需要异步环境，这里展示用法说明
print("""
stream 用法（需要 LLM 支持）：
  for chunk in chain.stream({"input": "..."}):
      print(chunk, end="", flush=True)

ainvoke 用法（异步环境）：
  import asyncio
  result = await chain.ainvoke({"input": "..."})
""")

print("✅ LCEL 进阶代码运行完成！")
