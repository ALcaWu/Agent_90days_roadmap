# -*- coding: utf-8 -*-
"""
=================================
第四章：Chain 实战与自定义函数
=================================

【章节目标】
掌握用纯 LCEL 构建复杂 Chain，学会自定义函数包装和 Chain 组合。

【实战模式】
LangChain 现代开发的标准模式：
1. 定义各个步骤（Prompt / 函数 / Parser）
2. 用 | 或 RunnableParallel 组装
3. 一行调用获取结果

【内容概览】
1. 翻译 Chain 实战（LCEL + RunnableLambda）
2. 问答 Chain 实战（多角色 Prompt）
3. 复杂 Chain 组合（Parallel + Sequential）
4. 自定义 Chain 的等价写法
"""

import os

# ============================================================
# 一、翻译 Chain 实战
# ============================================================
def demo_translate_chain():
    """
    用 LCEL 实现翻译 Chain：

    输入: {"text": "Hello", "lang": "中文"}
    输出: "你好"

    管道：
        prompt 填充（text + lang）
          → llm.invoke()
          → StrOutputParser.invoke()
    """
    if not os.getenv("OPENAI_API_KEY"):
        print("[翻译 Chain] 未设置 API_KEY，展示结构")
        print("  translate_chain = prompt | llm | parser")
        print("  result = translate_chain.invoke({'text': 'Hello', 'lang': '中文'})")
        return

    from langchain_core.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI
    from langchain_core.output_parsers import StrOutputParser

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    parser = StrOutputParser()

    # 翻译模板
    prompt = PromptTemplate.from_template(
        "将以下文本翻译成 {target_lang}：{text}"
    )

    # 翻译 Chain
    translate_chain = prompt | llm | parser

    result = translate_chain.invoke({
        "text": "Python is a high-level programming language",
        "target_lang": "中文"
    })

    print(f"[翻译 Chain] 输入: 'Python is a high-level programming language'")
    print(f"[翻译 Chain] 输出: {result}")


# ============================================================
# 二、问答 Chain 实战
# ============================================================
def demo_qa_chain():
    """
    用 LCEL 实现问答 Chain：

    关键：SystemMessage 定义 AI 角色，HumanMessage 传入问题
    ChatPromptTemplate 支持多消息组合，比 PromptTemplate 更强大
    """
    if not os.getenv("OPENAI_API_KEY"):
        print("[问答 Chain] 未设置 API_KEY，展示结构")
        return

    from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
    from langchain_openai import ChatOpenAI
    from langchain_core.output_parsers import StrOutputParser

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    parser = StrOutputParser()

    # 问答模板：SystemMessage 设定角色，HumanMessage 传入问题
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的 Python 教练，用简洁的语言回答问题。"),
        ("human", "{question}"),
    ])

    # 问答 Chain
    qa_chain = prompt | llm | parser

    result = qa_chain.invoke({
        "question": "什么是 Python 的装饰器？"
    })

    print(f"[问答 Chain] 问题: 什么是 Python 的装饰器？")
    print(f"[问答 Chain] 回答: {result}")


# ============================================================
# 三、复杂 Chain 组合（并行+顺序）
# ============================================================
def demo_complex_chain():
    """
    实现一个"翻译 + 摘要 + 情感分析" Chain：

    输入: {"text": "English text", "lang": "目标语言"}
      → 翻译链      → {"translated": "翻译结果"}
      → 摘要链      → {"summary": "一句话摘要"}
      → 情感分析链  → {"sentiment": "正面/负面/中性"}

    使用 RunnableParallel 并行启动摘要和情感分析，
    然后用 RunnableLambda 合并结果。
    """
    if not os.getenv("OPENAI_API_KEY"):
        print("[复杂 Chain 组合] 未设置 API_KEY，展示结构")
        print("  1. 翻译链: translate_prompt | llm | parser")
        print("  2. 摘要链: summarize_prompt | llm | parser")
        print("  3. 情感链: sentiment_prompt  | llm | parser")
        print()
        print("  完整链: translate_chain | summary_sentiment_parallel")
        return

    from langchain_core.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnableParallel, RunnableLambda

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    parser = StrOutputParser()

    # Step 1: 翻译链
    translate_prompt = PromptTemplate.from_template(
        "翻译成 {target_lang}：{text}"
    )
    translate_chain = translate_prompt | llm | parser

    # Step 2: 摘要链（接收翻译结果）
    summarize_prompt = PromptTemplate.from_template(
        "用一句话概括：{translated}"
    )
    summarize_chain = summarize_prompt | llm | parser

    # Step 3: 情感分析链（也接收翻译结果，并行执行）
    sentiment_prompt = PromptTemplate.from_template(
        "判断以下文本的情感，只返回'正面'、'负面'或'中性'：{translated}"
    )
    sentiment_chain = sentiment_prompt | llm | parser

    # Step 4: 合并摘要和情感分析（并行）
    summary_sentiment_parallel = RunnableParallel({
        "summary": summarize_chain,
        "sentiment": sentiment_chain,
    })

    # Step 5: 完整链：翻译 → (摘要+情感并行)
    def extract_translated(x: str) -> dict:
        """提取翻译结果，传给下游"""
        return {"translated": x}

    full_chain = (
        translate_chain
        | RunnableLambda(extract_translated)
        | summary_sentiment_parallel
    )

    # Step 6: 整理最终输出
    def format_output(x: dict) -> dict:
        return {
            "translated": x["translated"],
            "summary": x["summary"],
            "sentiment": x["sentiment"],
        }

    final_chain = full_chain | RunnableLambda(format_output)

    result = final_chain.invoke({
        "text": "LangChain is an amazing framework for building LLM applications!",
        "target_lang": "中文"
    })

    print(f"[复杂 Chain] 翻译结果: {result['translated']}")
    print(f"[复杂 Chain] 摘要: {result['summary']}")
    print(f"[复杂 Chain] 情感: {result['sentiment']}")


# ============================================================
# 四、自定义函数的等价写法
# ============================================================
def demo_custom_equivalents():
    """
    展示：自定义 Chain 类（LLMChain 的等价写法）

    在旧版 LangChain 中：
        chain = LLMChain(llm=llm, prompt=prompt, output_key="text")
        result = chain.invoke({"topic": "Python"})

    在新版 LangChain（纯 LCEL）中，等价写法：
        chain = prompt | llm | parser
        result = chain.invoke({"topic": "Python"})

    两者效果完全相同，LCEL 写法更简洁、更灵活。
    """
    print("[自定义 Chain 等价写法]")

    # 旧版 LLMChain 模式（伪代码）
    print("  # 旧版 LLMChain 写法（v0.1.x）")
    print("  chain = LLMChain(llm=llm, prompt=prompt, output_key='text')")
    print("  result = chain.invoke({'topic': 'Python'})")
    print("  # {'topic': 'Python', 'text': '...'}")
    print()

    # 新版 LCEL 模式（推荐）
    print("  # 新版 LCEL 写法（v1.x，推荐）")
    print("  chain = prompt | llm | parser")
    print("  result = chain.invoke({'topic': 'Python'})")
    print("  # 直接返回字符串（最后一步是 parser）")
    print()
    print("  # 如果需要 dict 输出，换掉最后的 parser 即可")
    print("  chain = prompt | llm  # 返回 AIMessage")

    # RunnableLambda 的多种写法
    print()
    print("[RunnableLambda 等价写法]")
    print("  # 方式 1：直接传函数")
    print("  r = RunnableLambda(lambda x: x * 2)")
    print()
    print("  # 方式 2：装饰器语法")
    print("  @RunnableLambda")
    print("  def double(x):")
    print("      return x * 2")
    print()
    print("  # 方式 3：类方法引用")
    print("  r = RunnableLambda(str.upper)")

    from langchain_core.runnables import RunnableLambda

    # 三种写法效果相同
    r1 = RunnableLambda(lambda x: x * 2)
    result1 = r1.invoke(5)

    @RunnableLambda
    def double_fn(x):
        return x * 2
    result2 = double_fn.invoke(5)

    r3 = RunnableLambda(str.upper)
    result3 = r3.invoke("hello")

    print()
    print(f"[验证] lambda:  {result1}")
    print(f"[验证] 装饰器:  {result2}")
    print(f"[验证] 方法:    {result3}")


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("第四章：Chain 实战与自定义函数")
    print("=" * 50)

    demo_translate_chain()
    print()
    demo_qa_chain()
    print()
    demo_complex_chain()
    print()
    demo_custom_equivalents()
