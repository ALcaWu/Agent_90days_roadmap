# -*- coding: utf-8 -*-
"""
=================================
Day 14 练习题：LCEL 管道与 Chain 组合
=================================

【重要说明】
当前环境 langchain 1.2.15 已移除 LLMChain/SequentialChain，
本练习使用纯 LCEL（LangChain Expression Language）方式。

【题目说明】
- 共 3 道题，覆盖 LCEL 管道、RunnableLambda、Chain 组合
- 每道题 pass 留空，先自行完成，再验证答案

【依赖】
pip install langchain-core langchain-openai
需要设置 OPENAI_API_KEY 环境变量

【测试运行】
cd D:\\AgentDeveloperCourse
.venv\\Scripts\\python.exe 练习题.py
"""

import os
import unittest

# ============================================================
# 题目数据
# ============================================================
ENGLISH_TEXT = "Python is a high-level programming language widely used in AI and data science."
ARTICLE_TEXT = "LangChain is an open-source framework for building applications powered by large language models."


# ============================================================
# 练习 1：LCEL 管道组合翻译 Chain
# ============================================================
"""
【题目】使用 LCEL | 管道符组合 PromptTemplate + ChatModel + StrOutputParser，
        完成一个翻译 Chain。

【要求】
1. 用 | 组合三个组件：prompt_template | llm | parser
2. Prompt 模板："将以下文本翻译成中文：{text}"
3. 调用 chain.invoke({"text": ENGLISH_TEXT})
4. 返回字符串结果（翻译后的中文文本）
5. 不需要 API Key 时跳过测试（用 if not os.getenv("OPENAI_API_KEY")）

【参考代码结构】
    from langchain_core.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI
    from langchain_core.output_parsers import StrOutputParser

    llm = ChatOpenAI(model="gpt-4o-mini")
    parser = StrOutputParser()
    chain = prompt_template | llm | parser
    return chain.invoke({"text": ENGLISH_TEXT})
"""


def exercise_1() -> str:
    """练习 1：LCEL 管道组合翻译 Chain"""
    if not os.getenv("OPENAI_API_KEY"):
        return "[跳过] 未设置 OPENAI_API_KEY"

    # TODO：完成以下代码
    pass


# ============================================================
# 练习 2：RunnableLambda + LCEL 管道
# ============================================================
"""
【题目】使用 RunnableLambda 将普通函数包装成 Runnable，
        接入 LCEL 管道，实现"统计+大写" Chain。

【要求】
1. 定义函数 word_count(text: str) -> int，返回单词数
2. 定义函数 uppercase(text: str) -> str，转大写
3. 用 RunnableLambda 将两个函数包装
4. 用 | 组合：输入文本 → 大写处理 → 单词统计
5. 返回 dict: {"upper": "大写文本", "count": 单词数}

【提示】
- RunnableLambda(func) 将普通函数变成 Runnable
- 可以用 RunnableParallel 并行执行两个函数：
      RunnableParallel({
          "upper": RunnableLambda(uppercase),
          "count": RunnableLambda(word_count),
      })
"""


def exercise_2() -> dict:
    """练习 2：RunnableLambda 统计+大写 Chain"""
    # TODO：完成以下代码
    pass


# ============================================================
# 练习 3：LCEL Chain 组合（翻译 + 摘要）
# ============================================================
"""
【题目】用纯 LCEL 实现翻译 + 摘要 Chain（不使用 LLMChain/SequentialChain）。

【流程】
输入: {"text": ARTICLE_TEXT}
  → 翻译链 (translate_prompt | llm | parser)
  → {"translated": "翻译结果"}
  → 摘要链 (summarize_prompt | llm | parser)
  → {"summary": "摘要结果"}

【关键点】
翻译链返回字符串，不能直接传给下一个需要 dict 的链。
需要用 RunnableLambda 做数据转换：
    def extract(x: str) -> dict:
        return {"text": x}  # 把字符串转成 dict 传给下一个链

【要求】
1. 创建翻译 Chain（translate_prompt | llm | parser）
2. 创建摘要 Chain（summarize_prompt | llm | parser）
3. 用 RunnableLambda 做数据转换
4. 用 | 组合完整链
5. 返回 dict: {"translated": "...", "summary": "..."}
6. 不需要 API Key 时跳过测试
"""


def exercise_3() -> dict:
    """练习 3：LCEL Chain 组合翻译 + 摘要"""
    if not os.getenv("OPENAI_API_KEY"):
        return {"translated": "[跳过]", "summary": "[跳过]"}

    # TODO：完成以下代码
    pass


# ============================================================
# ============ 以下为单元测试 ===================================
# ============================================================

class TestExercise1(unittest.TestCase):
    """练习1：LCEL 管道组合翻译"""

    def test_returns_string(self):
        result = exercise_1()
        if not os.getenv("OPENAI_API_KEY"):
            self.skipTest("需要 OPENAI_API_KEY")
        self.assertIsInstance(result, str)

    def test_contains_chinese(self):
        import re
        result = exercise_1()
        if not os.getenv("OPENAI_API_KEY"):
            self.skipTest("需要 OPENAI_API_KEY")
        has_chinese = bool(re.search(r"[\u4e00-\u9fff]", result))
        self.assertTrue(has_chinese, f"结果不包含中文：{result}")

    def test_lcel_pipeline_type(self):
        """验证 LCEL | 管道创建的是 Runnable 对象"""
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnableSequence

        template = PromptTemplate.from_template("翻译：{text}")
        parser = StrOutputParser()
        chain = template | parser  # 简化的链（不含 llm）
        self.assertIsInstance(chain, RunnableSequence)


class TestExercise2(unittest.TestCase):
    """练习2：RunnableLambda 统计+大写"""

    def test_returns_dict(self):
        result = exercise_2()
        self.assertIsInstance(result, dict)

    def test_has_upper_key(self):
        result = exercise_2()
        self.assertIn("upper", result, f"结果缺少 'upper' 键：{result}")

    def test_has_count_key(self):
        result = exercise_2()
        self.assertIn("count", result, f"结果缺少 'count' 键：{result}")

    def test_upper_is_uppercase(self):
        result = exercise_2()
        text = "Hello World"
        self.assertEqual(result["upper"], text.upper())

    def test_count_is_correct(self):
        result = exercise_2()
        text = "Python is great"
        self.assertEqual(result["count"], len(text.split()))

    def test_runnable_lambda_type(self):
        """验证 RunnableLambda 返回正确的类型"""
        from langchain_core.runnables import RunnableLambda

        def dummy(x): return x

        r = RunnableLambda(dummy)
        self.assertTrue(hasattr(r, "invoke"))


class TestExercise3(unittest.TestCase):
    """练习3：LCEL Chain 组合翻译+摘要"""

    def test_returns_dict(self):
        result = exercise_3()
        if not os.getenv("OPENAI_API_KEY"):
            self.skipTest("需要 OPENAI_API_KEY")
        self.assertIsInstance(result, dict)

    def test_has_translated_key(self):
        result = exercise_3()
        if not os.getenv("OPENAI_API_KEY"):
            self.skipTest("需要 OPENAI_API_KEY")
        self.assertIn("translated", result, f"结果缺少 'translated' 键：{result}")

    def test_has_summary_key(self):
        result = exercise_3()
        if not os.getenv("OPENAI_API_KEY"):
            self.skipTest("需要 OPENAI_API_KEY")
        self.assertIn("summary", result, f"结果缺少 'summary' 键：{result}")

    def test_runnable_parallel_combines(self):
        """验证 RunnableParallel 能正确组合多个链"""
        from langchain_core.runnables import RunnableParallel, RunnableLambda

        parallel = RunnableParallel({
            "upper": RunnableLambda(lambda x: x.upper()),
            "lower": RunnableLambda(lambda x: x.lower()),
        })
        result = parallel.invoke("Hello")
        self.assertEqual(result["upper"], "HELLO")
        self.assertEqual(result["lower"], "hello")


if __name__ == "__main__":
    print("=" * 50)
    print("Day 14 练习题：LCEL 管道与 Chain 组合")
    print("=" * 50)
    print()

    # 展示各题结构（不依赖 API Key）
    print("[练习 1] LCEL 管道组合翻译")
    r1 = exercise_1()
    print(f"  返回类型: {type(r1).__name__}")
    if not os.getenv("OPENAI_API_KEY"):
        print("  [跳过] 需要 OPENAI_API_KEY")
    print()

    print("[练习 2] RunnableLambda 统计+大写")
    r2 = exercise_2()
    print(f"  返回类型: {type(r2).__name__}")
    print(f"  返回内容: {r2}")
    print()

    print("[练习 3] LCEL Chain 组合翻译+摘要")
    r3 = exercise_3()
    print(f"  返回类型: {type(r3).__name__}")
    if not os.getenv("OPENAI_API_KEY"):
        print("  [跳过] 需要 OPENAI_API_KEY")
    print()

    print("=" * 50)
    print("单元测试详情（verbosity=2）")
    print("=" * 50)
    unittest.main(verbosity=2)
