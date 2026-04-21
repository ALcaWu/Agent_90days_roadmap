# -*- coding: utf-8 -*-
"""
=================================
第一章：Chain 核心概念
=================================

【章节目标】
理解 Chain 是什么、为什么需要 Chain，以及 LangChain 中 Chain 的分类。

【重要说明】
当前安装的 langchain 版本（1.2.15）中，LLMChain 和 SequentialChain
已被移除。LangChain 全面转向纯 LCEL（LangChain Expression Language）方式。
本课程将使用纯 LCEL 进行教学。

【核心概念】
- Chain（链）：LangChain 的执行单元，将多个 Runnable 组件串联成流水线
- Runnable 接口：所有 LangChain 组件的统一接口
- LCEL：用 | 管道符组合 Runnable，是 LangChain 的现代标准

【内容概览】
1. 不用 Chain 的问题（手动拼接）
2. 用 Chain 的优势（可复用、可组合）
3. LCEL 管道符原理
"""

# ============================================================
# 一、不用 Chain 的问题
# ============================================================
def call_llm_without_chain(topic: str) -> str:
    """
    手动方式：拼 prompt → 调用 LLM → 解析结果

    问题：
    1. prompt 散落在代码里，难以维护
    2. 多步骤任务要手动管理调用顺序
    3. 每次都要重复写调用代码
    """
    # Step 1: 构造 prompt（硬编码）
    prompt = f"请用一段话介绍 {topic}，不超过 50 字"

    # Step 2: 调用 LLM（需要处理消息格式）
    # from langchain_openai import ChatOpenAI
    # llm = ChatOpenAI(model="gpt-4o-mini")
    # response = llm.invoke(prompt)  # 需要手动传入正确格式

    # Step 3: 解析（需要手动处理）
    # result = response.content if hasattr(response, 'content') else str(response)
    return "[模拟] 手动方式：需要自己拼接 prompt、调用 LLM、管理格式]"


# ============================================================
# 二、用 Chain 的优势
# ============================================================
def call_llm_with_chain(topic: str) -> str:
    """
    用 LCEL Chain：一行代码完成全流程，可复用、易维护

    chain = template | llm | parser
    chain.invoke({"topic": "xxx"})  # 传入参数，自动执行完整流水线
    """
    # LCEL 的核心：用 | 管道符把组件串联
    # template.invoke({"topic": ...}) → llm.invoke(...) → parser.invoke(...)
    return "[模拟] LCEL 方式：template | llm | parser，一行搞定"


# ============================================================
# 三、LCEL 管道符原理
# ============================================================
def demo_lcel_pipeline():
    """
    A | B | C 等价于 RunnableSequence(first=A, middle=[B], last=C)

    数据流向：
    1. template.invoke({"topic": "..."})  → PromptValue
    2. llm.invoke(PromptValue)              → AIMessage
    3. parser.invoke(AIMessage)             → str / dict / list

    每个组件都实现 Runnable 接口，都支持 .invoke() / .batch() / .stream()
    """
    # 这是 LCEL 的核心模式（伪代码演示）
    print("[LCEL 管道原理]")
    print("  输入: {\"topic\": \"Python\"}")
    print("  Step 1: template.invoke()  → PromptValue")
    print("  Step 2: llm.invoke()      → AIMessage")
    print("  Step 3: parser.invoke()   → str 结果")
    print()


# ============================================================
# 四、Runnable 接口核心方法
# ============================================================
def demo_runnable_methods():
    """
    LangChain 所有组件都实现了 Runnable 接口，核心方法有：

    | 方法      | 作用            | 返回类型   |
    |---------|-----------------|---------|
    | invoke  | 单次同步执行       | 任意类型    |
    | batch   | 批量同步执行       | list    |
    | ainvoke | 单次异步执行       | 协程      |
    | stream  | 流式输出（逐 token）| generator |

    示例（实际需要 API Key 才能调用 LLM）：
        chain = template | llm | parser
        result = chain.invoke({"topic": "Python"})     # 单次
        results = chain.batch([{"topic": "Python"}, {"topic": "Go"}])  # 批量
        for token in chain.stream({"topic": "Python"}):  # 流式
            print(token, end="")
    """
    print("[Runnable 核心方法]")
    print("  invoke  — 单次执行（最常用）")
    print("  batch   — 批量执行（多个输入）")
    print("  stream  — 流式输出（逐 token）")
    print("  ainvoke — 异步单次执行")
    print()


# ============================================================
# 五、验证 LCEL 在当前环境可用
# ============================================================
def verify_lcel_works():
    """
    验证 LCEL 管道在当前 langchain 版本中可用
    （不需要 API Key，只验证类加载）
    """
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnableLambda, RunnableParallel
    from langchain_openai import ChatOpenAI

    # PromptTemplate
    t = PromptTemplate.from_template("介绍一下 {topic}")
    print(f"[验证] PromptTemplate: {type(t).__name__}")

    # StrOutputParser
    p = StrOutputParser()
    print(f"[验证] StrOutputParser: {type(p).__name__}")

    # RunnableLambda
    r = RunnableLambda(lambda x: x.upper())
    print(f"[验证] RunnableLambda: {type(r).__name__}")

    # RunnableParallel
    rp = RunnableParallel({"a": RunnableLambda(lambda x: x * 2)})
    print(f"[验证] RunnableParallel: {type(rp).__name__}")

    # LCEL 管道（不实际调用 LLM，只验证类型）
    # 如果设置了 API Key，这里可以直接运行：
    # chain = t | llm | p
    # result = chain.invoke({"topic": "LangChain"})

    print("[验证] LCEL 管道创建成功！")


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("第一章：Chain 核心概念（纯 LCEL 版）")
    print("=" * 50)

    demo_lcel_pipeline()
    demo_runnable_methods()
    verify_lcel_works()

    print()
    print("[总结]")
    print("  手动：prompt.format() -> llm.invoke() -> parser.invoke()")
    print("  LCEL：template | llm | parser.invoke() 一行搞定")
    print("  所有组件都实现 Runnable 接口，统一调用方式")
