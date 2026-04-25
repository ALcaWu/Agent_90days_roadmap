# -*- coding: utf-8 -*-
"""
=================================
第二章：LCEL 管道基础
=================================

【章节目标】
掌握 LCEL | 管道符的用法，理解数据在管道中的流动方式。

【LCEL 核心语法】
- A | B：将 A 的输出作为 B 的输入
- A | B | C：依次传递，first=A, middle=[B], last=C
- {"key": runnable}：用 dict 创建 RunnableParallel（并行）

【数据流向示例】
输入: {"topic": "Python"}
  Step 1: template.invoke({"topic": "Python"}) → PromptValue
  Step 2: llm.invoke(PromptValue)              → AIMessage
  Step 3: parser.invoke(AIMessage)             → str

【内容概览】
1. 最简单的 LCEL 管道
2. 管道中的数据转换
3. batch 批量执行
4. stream 流式输出
"""

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

api_key = os.getenv("OPENAI_API_KEY")
print(api_key)  # 测试用，确认能读到


# ============================================================
# 一、最简单的 LCEL 管道
# ============================================================
def demo_simple_pipeline():
    """
    最简单的 LCEL 管道：
        prompt_template | chat_model | output_parser

    功能：用户输入 topic → LLM 生成介绍

    注意：需要设置 OPENAI_API_KEY 环境变量才能实际运行
    """

    print(os.getenv("OPENAI_API_KEY"))
    if not os.getenv("OPENAI_API_KEY"):
        print("[跳过] 未设置 OPENAI_API_KEY，展示代码结构")
        print("  chain = prompt | llm | parser")
        print("  result = chain.invoke({'topic': 'LangChain'})")
        return

    from langchain_core.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI
    from langchain_core.output_parsers import StrOutputParser

    # 组件 1: Prompt 模板
    prompt = PromptTemplate.from_template("请用一段话介绍 {topic}，不超过 50 字")

    # 组件 2: Chat Model（使用 gpt-4o-mini 便宜模型）
    llm = ChatOpenAI(model="MiniMax-M2.7", temperature=0.7)

    # 组件 3: Output Parser（把 LLM 输出转成字符串）
    parser = StrOutputParser()

    # 用 | 组合成 Chain
    chain = prompt | llm | parser

    # 调用
    result = chain.invoke({"topic": "LangChain"})
    print(f"[LCEL 管道] 结果类型: {type(result).__name__}")
    print(f"[LCEL 管道] 结果内容: {result}")


# ============================================================
# 二、管道中的数据转换
# ============================================================
def demo_pipeline_data_flow():
    """
    LCEL 管道中，每个环节的输出是下一个环节的输入。

    以 {"topic": "Python"} 为例：

    Step 1: PromptTemplate.invoke({"topic": "Python"})
            输入: dict  {"topic": "Python"}
            输出: PromptValue（一种特殊的消息容器）

    Step 2: ChatModel.invoke(PromptValue)
            输入: PromptValue
            输出: AIMessage（AI 的回复消息对象）

    Step 3: StrOutputParser.invoke(AIMessage)
            输入: AIMessage
            输出: str（纯文本字符串）

    最后一步决定返回类型：StrOutputParser → str
    """
    print("[管道数据转换流程]")
    print('  输入: {"topic": "Python"}')
    print("  Step 1: PromptTemplate.invoke() → PromptValue")
    print("  Step 2: ChatModel.invoke(PromptValue) → AIMessage")
    print("  Step 3: StrOutputParser.invoke(AIMessage) → str")
    print()

    # 不依赖 API Key 的演示：用 RunnableLambda 做数据转换
    from langchain_core.runnables import RunnableLambda

    def step1(data):
        return {"prompt_value": f"请介绍 {data['topic']}"}

    def step2(data):
        return {"llm_response": f"[模拟 LLM 回复：关于 {data['prompt_value']}的知识]"}

    def step3(data):
        return data["llm_response"]

    # 等价的 LCEL 链（用普通函数演示）
    chain = RunnableLambda(step1) | RunnableLambda(step2) | RunnableLambda(step3)

    result = chain.invoke({"topic": "Python"})
    print(f"[模拟 LCEL 链] 最终结果: {result}")


# ============================================================
# 三、batch 批量执行
# ============================================================
def demo_batch():
    """
    batch() 方法可以一次传入多个输入，批量执行。

    适用场景：
    - 一次性处理多个用户请求
    - 批量生成多个内容（批量翻译、批量摘要等）
    - LangChain 内部会对 batch 做并行优化
    """
    print("[batch 批量执行]")
    print("  # 串行（3次调用）")
    print("  for q in questions:")
    print("      chain.invoke({'question': q})")
    print()
    print("  # 批量（LangChain 内部可能并行优化）")
    print("  results = chain.batch([")
    print("      {'question': '什么是 Python？'},")
    print("      {'question': '什么是 LangChain？'},")
    print("      {'question': '什么是 LCEL？'},")
    print("  ])")
    print()

    # 不依赖 API Key：用 RunnableLambda 演示 batch
    from langchain_core.runnables import RunnableLambda

    chain = RunnableLambda(lambda x: f"回答: {x['question']}")

    results = chain.batch(
        [
            {"question": "什么是 Python？"},
            {"question": "什么是 LangChain？"},
            {"question": "什么是 LCEL？"},
        ]
    )

    for i, r in enumerate(results, 1):
        print(f"  结果 {i}: {r}")


# ============================================================
# 四、stream 流式输出
# ============================================================
def demo_stream():
    """
    stream() 方法以生成器方式逐 token 返回，实现"打字机"效果。

    注意：需要实际调用 LLM 才能看到流式效果，
    这里用模拟数据演示。
    """
    print("[stream 流式输出]")
    print("  for token in chain.stream({'topic': 'LangChain'}):")
    print("      print(token, end='', flush=True)")
    print()
    print("  # 实际输出会是逐字打印的效果：")
    print("  L a n g C h a i n 是 一 个 . . .")

    # 不依赖 API Key：用生成器模拟流式效果
    def stream模拟():
        for char in "[模拟流式输出：LangChain 是一个强大的 LLM 应用框架]":
            yield char

    print("  实际效果: ", end="", flush=True)
    for char in stream模拟():
        print(char, end="", flush=True)
    print()


# ============================================================
# 五、带变量的管道
# ============================================================
def demo_pipeline_with_variables():
    """
    LCEL 管道的优雅之处：模板变量自动流向下一层。

    管道 template | llm | parser 中：
    - template.invoke({"topic": "Python"}) → 生成填充后的 prompt
    - llm.invoke(...) → 调用 LLM
    - parser.invoke(...) → 解析输出

    不需要手动把变量从 template 传到 llm，管道自动处理。
    """
    print("[带变量的管道]")
    print("  template = PromptTemplate.from_template('介绍一下 {topic}')")
    print("  chain = template | llm | parser")
    print()
    print("  # template.invoke() 自动生成 prompt，llm 自动接收结果")
    print("  result = chain.invoke({'topic': 'Python'})")
    print()
    print("  # 变量 topic 在整个管道中保持传递，无需手动管理")


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("第二章：LCEL 管道基础")
    print("=" * 50)

    demo_simple_pipeline()
    print()
    demo_pipeline_data_flow()
    print()
    demo_batch()
    print()
    demo_stream()
    print()
    demo_pipeline_with_variables()
