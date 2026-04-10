# -*- coding: utf-8 -*-
"""
Day 11 - 练习题：Few-shot 与 Output Parser

完成以下练习，巩固今日所学知识点。
运行测试：python 练习题.py
"""

import json
import unittest
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import (
    FewShotPromptTemplate,
    PromptTemplate,
)
from langchain_core.output_parsers import (
    CommaSeparatedListOutputParser,
    PydanticOutputParser,
)
from langchain_core.runnables import RunnableLambda, RunnableParallel


# ==================== 练习1：构建 Few-shot 模板 ====================
# 任务：构建一个情感分析的 Few-shot 提示模板
# 要求：
#   - 提供3个示例（正面/负面/中性各一）
#   - 输出格式为：情感: xxx（正面/负面/中性）
#   - 输入变量名：text


def build_sentiment_few_shot() -> FewShotPromptTemplate:
    """
    构建情感分析 Few-shot 模板

    Returns:
        FewShotPromptTemplate，包含3个示例
    """
    # TODO：实现此函数
    # 提示：
    #   1. 定义 examples（包含 input 和 output 键）
    #   2. 定义 example_prompt（格式：输入：{input}\n{output}）
    #   3. 返回 FewShotPromptTemplate
    example_prompt = PromptTemplate.from_template("输入：{input}\n输出：{output}")
    examples = [
        {"input": "我非常喜欢这个产品", "output": "正面"},
        {"input": "这个产品非常差", "output": "负面"},
        {"input": "这个产品非常一般", "output": "中性"},
    ]
    few_shot = FewShotPromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
        prefix="请根据以下示例给出评价：\n",
        suffix="输入：{text}\n输出：",
        input_variables=["text"],
    )
    return few_shot


# ==================== 练习2：使用 PydanticOutputParser ====================
# 任务：定义一个书籍信息的 Pydantic 模型并创建对应的解析器


class BookInfo(BaseModel):
    """书籍信息"""

    # TODO：定义以下字段
    # title: str（书名）
    # author: str（作者）
    # year: int（出版年份）
    # genres: List[str]（类型标签列表）
    # rating: float（评分，0-10）
    title: str = Field(description="书名")
    author: str = Field(description="作者")
    year: int = Field(description="出版年份")
    genres: List[str] = Field(description="类型标签列表")
    rating: float = Field(description="评分，0-10")


def parse_book_info(json_str: str) -> Optional[BookInfo]:
    """
    解析书籍 JSON 字符串为 BookInfo 对象

    Args:
        json_str: JSON 格式的书籍信息字符串

    Returns:
        BookInfo 对象，解析失败返回 None
    """
    # TODO：使用 PydanticOutputParser 解析 json_str
    # 提示：
    #   1. 创建 PydanticOutputParser(pydantic_object=BookInfo)
    #   2. 调用 parser.invoke(json_str)
    #   3. 捕获异常，返回 None
    # # ❌ 原答案：parser.invoke() 在 try 外面，无效JSON时异常无法被捕获
    # parser = PydanticOutputParser(pydantic_object=BookInfo)
    # parser.invoke(json_str)
    # try:
    #     return parser.parse(json_str)
    # except Exception:
    #     return None
    try:
        parser = PydanticOutputParser(pydantic_object=BookInfo)
        return parser.invoke(json_str)
    except Exception:
        return None


# ==================== 练习3：CommaSeparatedListOutputParser ====================
# 任务：使用列表解析器处理模拟输出


def parse_skills_list(text: str) -> List[str]:
    """
    将逗号分隔的技能文本解析为列表

    Args:
        text: 逗号分隔的技能文本，如 "Python, LangChain, FastAPI"

    Returns:
        技能列表（去除首尾空格）
    """
    # TODO：使用 CommaSeparatedListOutputParser 解析
    # # ❌ 原答案：硬编码了输入，忽略了函数参数 text
    # parser = comma.invoke("Python, LangChain, FastAPI")
    # return parser
    # # ❌ 只调用 comma.invoke()，CommaSeparatedListOutputParser 不会自动去除首尾空格
    # return comma.invoke(text)
    comma = CommaSeparatedListOutputParser()
    return [s.strip() for s in comma.invoke(text)]


# ==================== 练习4：RunnableParallel 并行链 ====================
# 任务：构建一个并行分析链，同时统计文本的字数和语言


def build_text_analyzer():
    """
    构建一个并行文本分析器

    返回一个 RunnableParallel，同时执行：
    - word_count：统计空格分隔的单词数
    - is_chinese：判断是否包含中文（bool）
    - length：字符总长度

    Returns:
        RunnableParallel 对象
    """
    # TODO：实现此函数
    # 提示：
    #   1. 定义3个 lambda 函数
    #   2. 使用 RunnableParallel(key=RunnableLambda(fn)) 组合
    # # ❌ 原答案："中文" in x 只能检测字面量"中文"，检测不到普通中文字符
    # is_chinese=RunnableLambda(lambda x: "中文" in x),
    import re

    runnable = RunnableParallel(
        word_count=RunnableLambda(lambda x: len(x.split())),
        is_chinese=RunnableLambda(lambda x: bool(re.search(r"[\u4e00-\u9fff]", x))),
        length=RunnableLambda(lambda x: len(x)),
    )
    return runnable


# ==================== 单元测试（不要修改）====================


class TestSentimentFewShot(unittest.TestCase):

    def test_returns_few_shot_template(self):
        template = build_sentiment_few_shot()
        self.assertIsNotNone(template, "函数不能返回 None")
        self.assertIsInstance(template, FewShotPromptTemplate)

    def test_has_examples(self):
        template = build_sentiment_few_shot()
        self.assertIsNotNone(template)
        # 应该有至少3个示例
        if hasattr(template, "examples") and template.examples:
            self.assertGreaterEqual(len(template.examples), 3)

    def test_can_invoke(self):
        template = build_sentiment_few_shot()
        self.assertIsNotNone(template)
        try:
            result = template.invoke({"text": "这个产品真的太棒了！"})
            self.assertIsNotNone(result)
        except Exception as e:
            self.fail(f"invoke 调用失败：{e}")


class TestBookInfo(unittest.TestCase):

    def test_book_info_fields(self):
        # 检查 BookInfo 是否有所有必要字段
        fields = BookInfo.model_fields
        required = ["title", "author", "year", "genres", "rating"]
        for field in required:
            self.assertIn(field, fields, f"BookInfo 缺少字段：{field}")

    def test_parse_valid_book(self):
        book_json = json.dumps(
            {
                "title": "Python编程：从入门到实践",
                "author": "Eric Matthes",
                "year": 2016,
                "genres": ["编程", "Python", "入门"],
                "rating": 9.0,
            },
            ensure_ascii=False,
        )
        book = parse_book_info(book_json)
        self.assertIsNotNone(book, "有效 JSON 应该成功解析")
        self.assertEqual(book.title, "Python编程：从入门到实践")
        self.assertEqual(book.year, 2016)
        self.assertIsInstance(book.genres, list)

    def test_parse_invalid_returns_none(self):
        result = parse_book_info("这不是JSON")
        self.assertIsNone(result, "无效输入应该返回 None")


class TestParseSkillsList(unittest.TestCase):

    def test_basic_parsing(self):
        result = parse_skills_list("Python, LangChain, FastAPI")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)

    def test_strips_whitespace(self):
        result = parse_skills_list("  Python  ,  LangChain  ,  Docker  ")
        for skill in result:
            self.assertEqual(skill, skill.strip(), f"'{skill}' 应该去除首尾空格")

    def test_single_item(self):
        result = parse_skills_list("Python")
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)


class TestBuildTextAnalyzer(unittest.TestCase):

    def test_returns_runnable_parallel(self):
        analyzer = build_text_analyzer()
        self.assertIsNotNone(analyzer)
        self.assertIsInstance(analyzer, RunnableParallel)

    def test_has_required_keys(self):
        analyzer = build_text_analyzer()
        self.assertIsNotNone(analyzer)
        result = analyzer.invoke("hello world test")
        self.assertIn("word_count", result)
        self.assertIn("is_chinese", result)
        self.assertIn("length", result)

    def test_word_count_correct(self):
        analyzer = build_text_analyzer()
        self.assertIsNotNone(analyzer)
        result = analyzer.invoke("hello world langchain")
        self.assertEqual(result["word_count"], 3)

    def test_chinese_detection(self):
        analyzer = build_text_analyzer()
        self.assertIsNotNone(analyzer)
        en_result = analyzer.invoke("hello world")
        cn_result = analyzer.invoke("你好世界")
        self.assertFalse(en_result["is_chinese"])
        self.assertTrue(cn_result["is_chinese"])

    def test_length_correct(self):
        analyzer = build_text_analyzer()
        self.assertIsNotNone(analyzer)
        text = "hello"
        result = analyzer.invoke(text)
        self.assertEqual(result["length"], len(text))


# ==================== 运行测试 ====================

if __name__ == "__main__":
    print("=" * 50)
    print("Day 11 练习题测试")
    print("=" * 50)
    print()
    unittest.main(verbosity=2)
