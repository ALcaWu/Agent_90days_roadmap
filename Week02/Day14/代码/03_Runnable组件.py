# -*- coding: utf-8 -*-
"""
=================================
第三章：核心 Runnable 组件
=================================

【章节目标】
掌握 LCEL 中最常用的 Runnable 组件：
RunnableLambda、RunnableParallel、RunnablePassthrough。

【三个核心组件速查】

| 组件               | 作用                    | 示例                        |
|-------------------|-----------------------|---------------------------|
| RunnableLambda    | 把普通函数包装成 Runnable  | RunnableLambda(func)      |
| RunnableParallel  | 并行执行多个 Runnable    | RunnableParallel({"a": r1, "b": r2}) |
| RunnablePassthrough | 透传输入，不做处理       | RunnablePassthrough()     |

【内容概览】
1. RunnableLambda：函数 → Runnable
2. RunnableParallel：并行执行多个任务
3. RunnablePassthrough：透传输入
4. LCEL dict 语法：{key: Runnable} 组合
"""

import os

# ============================================================
# 一、RunnableLambda：把普通函数变成 Runnable
# ============================================================
def demo_runnable_lambda():
    """
    RunnableLambda 将普通 Python 函数包装成 Runnable，
    使其可以接入 LCEL 管道。

    RunnableLambda(func)  等价于  lambda x: func(x)

    典型用途：
    1. 数据预处理：函数处理后的结果传给下一步
    2. 数据后处理：对 LLM 输出再加工
    3. 条件逻辑：根据输入决定如何处理
    """
    from langchain_core.runnables import RunnableLambda

    # 示例 1：简单函数包装
    def count_words(text: str) -> dict:
        """统计文本的单词数和字符数"""
        words = text.split()
        return {
            "original": text,
            "word_count": len(words),
            "char_count": len(text),
        }

    counter = RunnableLambda(count_words)
    result = counter.invoke("Python 异步编程 asyncio")
    print(f"[RunnableLambda] 输入: 'Python 异步编程 asyncio'")
    print(f"[RunnableLambda] 输出: {result}")
    print()

    # 示例 2：LCEL 管道 + 后处理
    # 模拟：LLM 输出 → 去除空白 → 转大写
    def trim(text: str) -> str:
        return text.strip()

    def upper(text: str) -> str:
        return text.upper()

    pipeline = (
        RunnableLambda(lambda: "  hello langchain  ")
        | RunnableLambda(trim)
        | RunnableLambda(upper)
    )

    result = pipeline.invoke({})
    print(f"[RunnableLambda 链式] '{'  hello langchain  '}' -> '{result}'")


# ============================================================
# 二、RunnableParallel：并行执行
# ============================================================
def demo_runnable_parallel():
    """
    RunnableParallel 并行执行多个 Runnable，输入相同，结果按 key 合并。

    parallel = RunnableParallel({
        "key1": runnable1,   # 同时执行
        "key2": runnable2,   # 同时执行
    })

    输入 {"text": "..."} 时，两个 Runnable 同时执行，合并结果：
    输出 {"key1": result1, "key2": result2}
    """
    from langchain_core.runnables import RunnableParallel, RunnableLambda

    # 并行任务 1：统计单词数
    def count_words(text: str) -> int:
        return len(text.split())

    # 并行任务 2：提取第一个单词
    def first_word(text: str) -> str:
        return text.split()[0] if text.split() else ""

    # 并行组合
    parallel = RunnableParallel({
        "word_count": RunnableLambda(count_words),
        "first_word": RunnableLambda(first_word),
    })

    result = parallel.invoke("Python 异步编程 asyncio")
    print(f"[RunnableParallel] 输入: 'Python 异步编程 asyncio'")
    print(f"[RunnableParallel] 输出: {result}")
    # {'word_count': 4, 'first_word': 'Python'}
    print()

    # 实际应用：用 LLM 同时生成摘要和关键词
    if os.getenv("OPENAI_API_KEY"):
        from langchain_core.prompts import PromptTemplate
        from langchain_openai import ChatOpenAI
        from langchain_core.output_parsers import StrOutputParser

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        parser = StrOutputParser()

        # 两个并行的 LCEL 链
        summary_chain = (
            PromptTemplate.from_template("用一句话概括：{text}")
            | llm
            | parser
        )
        kw_chain = (
            PromptTemplate.from_template("提取三个关键词（逗号分隔）：{text}")
            | llm
            | parser
        )

        parallel_llm = RunnableParallel({
            "summary": summary_chain,
            "keywords": kw_chain,
        })

        result = parallel_llm.invoke({
            "text": "Python 是一种高级编程语言，广泛用于数据科学和 AI。"
        })
        print(f"[并行 LLM] 摘要: {result['summary']}")
        print(f"[并行 LLM] 关键词: {result['keywords']}")


# ============================================================
# 三、RunnablePassthrough：透传输入
# ============================================================
def demo_runnable_passthrough():
    """
    RunnablePassthrough：透传输入，什么都不做，直接传给下一步。
    常用于：在 RunnableParallel 中保留原始输入。

    示例场景：
        {
            "original": RunnablePassthrough(),  # 保留原始输入
            "processed": another_runnable,     # 处理后的结果
        }
        | RunnableLambda(combine)              # 合并两者
    """
    from langchain_core.runnables import RunnablePassthrough, RunnableLambda

    # Passthrough：直接把输入原样传出
    passthrough = RunnablePassthrough()
    result = passthrough.invoke({"name": "张三", "age": 28})
    print(f"[RunnablePassthrough] 输入: {{'name': '张三', 'age': 28}}")
    print(f"[RunnablePassthrough] 输出: {result}")
    print()

    # 实用场景：保留原始输入的同时添加处理结果
    def add_info(data: dict) -> dict:
        return {
            "original": data,
            "word_count": len(str(data.get("text", "")).split()),
        }

    pipeline = RunnablePassthrough() | RunnableLambda(add_info)

    result = pipeline.invoke({"text": "Python 异步编程 asyncio"})
    print(f"[Passthrough 实用] {result}")


# ============================================================
# 四、LCEL dict 语法与组合
# ============================================================
def demo_lcel_dict():
    """
    LCEL 中，dict 语法创建 RunnableParallel。

    等价关系：
        RunnableParallel({"a": r1, "b": r2})
      = {"a": r1, "b": r2}  # 简写形式

    可以和 | 组合使用：
        {"a": r1, "b": r2} | RunnableLambda(merge)

    这在处理多输入/多输出的复杂 Chain 中非常有用。
    """
    from langchain_core.runnables import RunnableParallel, RunnableLambda

    # dict 语法创建并行
    parallel = {
        "double": RunnableLambda(lambda x: x * 2),
        "triple": RunnableLambda(lambda x: x * 3),
    }

    result = parallel.invoke(5)
    print(f"[dict 语法] 输入: 5")
    print(f"[dict 语法] 输出: {result}")
    # {'double': 10, 'triple': 15}

    # 合并处理
    def summary(data: dict) -> str:
        return f"double={data['double']}, triple={data['triple']}"

    pipeline = parallel | RunnableLambda(summary)
    result = pipeline.invoke(5)
    print(f"[dict+|组合] 最终结果: {result}")


# ============================================================
# 五、综合示例：翻译 + 摘要（纯 LCEL）
# ============================================================
def demo_translate_and_summarize():
    """
    综合示例：用纯 LCEL 实现翻译 + 摘要任务（无 LLMChain）

    流程：
    输入 {"text": "英文", "lang": "中文"}
      → 翻译链  → {"translated": "中文翻译"}
      → 摘要链  → {"summary": "一句话摘要"}

    使用 RunnableLambda 做数据转换，连接两个 LCEL 子链。
    """
    print("[翻译+摘要 LCEL 实现]")
    print("  Step 1: 翻译 LCEL 链")
    print("    translate_chain = prompt_t | llm | parser")
    print()
    print("  Step 2: 摘要 LCEL 链")
    print("    summarize_chain = prompt_s | llm | parser")
    print()
    print("  Step 3: 数据转换（翻译输出 -> 摘要输入）")
    print("    def extract_translated(x): return {'text': x['translated']}")
    print()
    print("  Step 4: 组合")
    print("    full_chain = translate_chain | extract_translated | summarize_chain")

    # 纯 Python 模拟（不依赖 API Key）
    from langchain_core.runnables import RunnableLambda

    translate_step = RunnableLambda(
        lambda x: {"translated": f"[翻译] {x['text']} -> {x['lang']}"}
    )
    summarize_step = RunnableLambda(
        lambda x: {"summary": f"[摘要] {x['translated']} 的核心内容"}
    )

    full_chain = translate_step | summarize_step

    result = full_chain.invoke({
        "text": "Python is a great language",
        "lang": "中文"
    })
    print()
    print(f"[模拟运行] 最终结果: {result}")


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("第三章：核心 Runnable 组件")
    print("=" * 50)

    demo_runnable_lambda()
    print()
    demo_runnable_parallel()
    print()
    demo_runnable_passthrough()
    print()
    demo_lcel_dict()
    print()
    demo_translate_and_summarize()
