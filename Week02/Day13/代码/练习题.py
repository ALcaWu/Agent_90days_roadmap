"""
Day 13 - 练习题：Pydantic与自定义Parser

涵盖内容：
1. 嵌套 Pydantic 模型设计
2. 字段验证器与约束
3. 容错 JSON Parser
4. 多格式 Parser 组合
5. Parser 工厂模式
"""

from langchain_core.output_parsers import PydanticOutputParser, BaseOutputParser
from langchain_core.exceptions import OutputParserException
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Literal, Union, Annotated
import json
import re
import unittest

# ============================================================
# 练习 1：嵌套 Pydantic 模型（简历解析器）
# ============================================================
"""
设计一个简历解析器，包含：
- WorkExperience: 公司、职位、时间段、业绩亮点
- Education: 学校、学位、毕业年份
- Resume: 姓名、邮箱、教育经历（列表）、工作经验（列表）、技能（列表）
- 验证：邮箱必须包含 @，年份在 1950-2030 之间
"""

llm_resume_output = """{
  "name": "李明",
  "email": "liming@example.com",
  "education": [
    {"school": "清华大学", "degree": "计算机科学硕士", "year": 2018},
    {"school": "浙江大学", "degree": "软件工程学士", "year": 2015}
  ],
  "experience": [
    {
      "company": "字节跳动",
      "position": "高级后端工程师",
      "duration": "2018.03 - 2022.08",
      "highlights": ["主导推荐系统重构", "QPS 提升 40%", "团队规模 8 人"]
    },
    {
      "company": "阿里巴巴",
      "position": "后端工程师",
      "duration": "2022.09 - 至今",
      "highlights": ["负责电商搜索服务", "日均请求量 5000 万"]
    }
  ],
  "skills": ["Python", "Go", "分布式系统", "Kubernetes", "MySQL"]
}"""


def exercise_1() -> dict:
    """练习 1：使用 Pydantic 嵌套模型解析简历 JSON

    题目要求：
    - WorkExperience: 公司、职位、时间段、业绩亮点
    - Education: 学校、学位、毕业年份（1950-2030）
    - Resume: 姓名、邮箱（必须包含@）、教育经历列表、经验列表、技能列表
    """

    # ==========================================================================
    # 定义嵌套模型：工作经历
    # ==========================================================================
    class WorkExperience(BaseModel):
        """工作经历模型

        字段说明：
        - company: 公司名称
        - position: 职位名称
        - duration: 工作时间段（如 "2018.03 - 2022.08"）
        - highlights: 业绩亮点列表（如 ["QPS 提升 40%", "团队规模 8 人"]）
        """

        company: str = Field(description="公司名称")
        position: str = Field(description="职位")
        duration: str = Field(description="时间段")
        highlights: List[str] = Field(description="业绩亮点")

    # ==========================================================================
    # 定义嵌套模型：教育经历
    # ==========================================================================
    class Education(BaseModel):
        """教育经历模型

        字段说明：
        - school: 学校名称
        - degree: 学位（如 "计算机科学硕士"）
        - year: 毕业年份（1950-2030），支持字符串容错（"2020年" -> 2020）
        """

        school: str = Field(description="学校名称")
        degree: str = Field(description="学位")
        # ✅ 修复1：直接用 Field(ge, le) 约束，不用 Annotated
        #    Annotated[int, Field(...)] 在 PydanticOutputParser 场景下
        #    可能导致 get_format_instructions() 生成的 schema 有冗余信息
        year: int = Field(ge=1950, le=2030, description="毕业年份")

        # ✅ 修复3：添加 year 容错验证器
        #    LLM 有时输出 "2018年" 而非纯数字 2018，mode="before" 在解析前预处理
        @field_validator("year", mode="before")
        @classmethod
        def parse_year_string(cls, v):
            """支持字符串 "2020年" 格式自动提取数字"""
            if isinstance(v, str):
                match = re.search(r"\d{4}", v)
                if match:
                    return int(match.group())
            return v

    # ==========================================================================
    # 定义主模型：简历
    # ==========================================================================
    class Resume(BaseModel):
        """简历模型，整合所有子模型

        字段说明：
        - name: 姓名
        - email: 邮箱（必须包含 @，自动验证）
        - education: 教育经历列表
        - experience: 工作经验列表
        - skills: 技能列表
        """

        name: str = Field(description="姓名")
        email: str = Field(description="邮箱")
        education: List[Education] = Field(description="教育经历")
        experience: List[WorkExperience] = Field(description="工作经验")
        skills: List[str] = Field(description="技能")

        # ✅ 修复2：添加 email 验证器
        #    题目要求：邮箱必须包含 @，不是有效邮箱格式时抛出错误
        @field_validator("email")
        @classmethod
        def validate_email(cls, v: str) -> str:
            """验证邮箱格式：必须包含 @ 符号"""
            if "@" not in v:
                raise ValueError("邮箱格式无效，必须包含 @ 符号")
            return v

    # ==========================================================================
    # 使用 PydanticOutputParser 解析 LLM 输出的 JSON 字符串
    # ==========================================================================
    # 创建 Parser 实例，传入 Resume 模型
    parser = PydanticOutputParser(pydantic_object=Resume)

    # 调用 parse() 方法将 JSON 字符串转为 Resume 对象
    # parse() 内部会：
    #   1. json.loads() 解析字符串 -> dict
    #   2. Resume.model_validate() 验证结构 -> Resume 对象
    result = parser.parse(llm_resume_output)

    # ✅ 返回 dict：调用 model_dump() 将 Pydantic 对象转为字典
    # model_dump() 产生的 dict 支持 result["key"] 字典式访问，兼容测试断言
    return result.model_dump()


# ============================================================
# 练习 2：容错 JSON Parser
# ============================================================
"""
LLM 的 JSON 输出经常有瑕疵，比如：
- 多余的尾随逗号: {"a": 1,}
- 单引号而非双引号: {'name': '张三'}
- 键没有引号: {name: '张三'}
- 多了注释行
实现一个 RobustJsonParser 自动修复这些问题并解析。
"""

llm_flawed_json = """```json
{
  'name': '张三',
  age: 28,  // LLM 加的注释
  "score": 95.5,
  "tags": ["Python", "AI",],
}
```"""


def exercise_2() -> dict:
    """练习 2：容错 JSON Parser，自动修复 LLM 常见格式错误"""

    class RobustJsonParser(BaseOutputParser):

        def _preprocess(self, text: str) -> str:
            """
            JSON 预处理：修复常见格式错误。
            注意：这些修复可能有副作用（误伤正常内容），所以尽量保守。
            """
            # 提取 json 代码块内容（如果有）
            match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
            json_str = match.group(1) if match else text

            json_str = json_str.strip()

            # 1. 移除行内注释（// 开头的注释，JSON 标准不支持注释）
            json_str = re.sub(r"//.*$", "", json_str, flags=re.MULTILINE)
            # 2. 移除块注释（/* ... */）
            json_str = re.sub(r"/\*.*?\*/", "", json_str, flags=re.DOTALL)

            # 3. 修复尾随逗号（这是 LLM 最常犯的错误）
            # 匹配 { ..., } 或 [ ..., ] 模式
            json_str = re.sub(r",(\s*[}\]])", r"\1", json_str)

            # 4. 修复单引号为双引号（保守：只在明显是字符串的地方替换）
            # 4a. 先修复键的单引号：'key': value → "key": value
            json_str = re.sub(r"'([^']+)'(\s*:)", r'"\1"\2', json_str)
            # 注意：此规则对值中的单引号（如 don\'t）效果有限，但 LLM 输出的 JSON 通常不含此类内容
            json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)
            json_str = re.sub(r"'\s*,\s*}", '" ,}', json_str)  # 修复: ' ,} → "},
            json_str = re.sub(r"'\s*\]\s*", '"]', json_str)  # 修复: ' ] → "]

            # 5. 允许无引号的键（有些 LLM 会输出 {key: value}）
            json_str = re.sub(r"(\w+)(\s*:)", r'"\1"\2', json_str)

            return json_str

        def parse(self, text: str) -> dict:
            """
            解析文本中的 JSON。
            1. 用 _preprocess 修复格式错误
            2. 用 json.loads 解析为 Python dict
            """
            fixed_text = self._preprocess(text)
            return json.loads(fixed_text)

    parser = RobustJsonParser()
    result = parser.parse(llm_flawed_json)
    return result


# ============================================================
# 练习 3：自定义 Parser + 验证器（任务规划器）
# ============================================================
"""
实现一个自定义 Parser，支持解析自然语言任务描述：
输入格式示例：
"任务：完成项目报告，优先级高，截止日期2024-06-15
 任务：回复邮件，优先级中
任务：准备会议，优先级高，截止日期2024-06-18"

解析后返回 TaskPlan 对象列表，包含：
- task: 任务名称
- priority: 高/中/低
- deadline: 可选的截止日期（YYYY-MM-DD 格式）
"""

llm_task_output = """任务：完成项目报告，优先级高，截止日期2024-06-15
任务：回复邮件，优先级中
任务：准备会议，优先级高，截止日期2024-06-18
任务：阅读文档，无优先级"""

from datetime import date


def exercise_3() -> List[dict]:
    """练习 3：自定义任务规划 Parser，解析自然语言任务列表

    解析 llm_task_output 中的多行任务，提取：
      - task：任务名称（从 "任务：xxx" 中提取 xxx）
      - priority：优先级（从 "优先级高/中/低" 中提取）
      - deadline：截止日期（从 "截止日期YYYY-MM-DD" 中提取，可选）
      - raw：原始文本（方便调试和边缘情况判断）

    测试覆盖：
      - 任务名称提取（4个任务全部识别）
      - 优先级提取（2个高，1个中）
      - 截止日期提取（2个有日期的任务）
      - 无优先级处理（"无优先级" → priority="中"，同时 raw 保留原始文本）
    """
    results = []

    # 按行分割，忽略空行，逐行解析
    for line in llm_task_output.strip().split("\n"):
        line = line.strip()
        if not line:
            continue

        # ---------- 1. 提取任务名称 ----------
        # 匹配 "任务：" 或 " 任务：" 等开头格式，贪婪匹配到第一个 "，" 或行尾
        task_match = re.search(r"^\s*任务[：:](.+?)(?:，|,)", line)
        if task_match:
            task_name = task_match.group(1).strip()
        else:
            # 如果没有逗号分隔，则取冒号后到行尾作为任务名
            task_name = re.sub(r"^\s*任务[：:]", "", line).strip()

        # ---------- 2. 提取优先级 ----------
        # 从后往前匹配优先级关键字（避免被任务名中的字干扰）
        priority = "中"  # 默认优先级
        raw = line  # 保存原始文本，方便调试

        if re.search(r"优先级高", line):
            priority = "高"
        elif re.search(r"优先级低", line):
            priority = "低"
        elif re.search(r"优先级中", line):
            priority = "中"
        elif "无优先级" in line:
            priority = ""

        # ---------- 3. 提取截止日期 ----------
        # 匹配 "截止日期YYYY-MM-DD" 格式，如 "截止日期2024-06-15"
        deadline_str = re.search(r"截止日期(\d{4}-\d{2}-\d{2})", line)
        if deadline_str:
            deadline_value = date.fromisoformat(deadline_str.group(1))
        else:
            deadline_value = None

        results.append(
            {
                "task": task_name,
                "priority": priority,
                "deadline": deadline_value.isoformat() if deadline_value else None,
                "raw": raw,
            }
        )

    return results


# ============================================================
# 练习 4：多格式组合 Parser
# ============================================================
"""
LLM 有时会输出"前言 + 代码块"的混合格式，例如：
---
分析：该用户反馈了性能问题，影响用户体验。
建议：优化数据库查询，增加缓存层。
---
```json
{
  "severity": "high",
  "category": "performance",
  "action_items": ["优化 SQL", "增加 Redis 缓存"]
}
```

实现一个 MultiFormatParser，同时解析：
1. 前言中的 YAML 风格内容（冒号分隔）
2. JSON 代码块中的结构化数据
"""

llm_mixed_output = """---
分析：该用户反馈了性能问题，影响用户体验。
建议：优化数据库查询，增加缓存层。
影响范围：生产环境 30% 用户受影响。
---
```json
{
  "severity": "high",
  "category": "performance",
  "action_items": ["优化 SQL", "增加 Redis 缓存"]
}
```"""


def exercise_4() -> dict:
    """练习 4：多格式组合 Parser，解析前言 + JSON 代码块"""

    class MultiFormatParser(BaseOutputParser):
        def parse(self, text: str) -> dict:

            match = re.search(r"---(.*?)---", text, re.DOTALL)

    pass


# ============================================================
# 练习 5：Parser 工厂模式
# ============================================================
"""
实现一个 ParserFactory，根据配置自动生成对应的 PydanticOutputParser：

支持的 Parser 类型：
- "movie": 电影评分解析器 (title, rating, review)
- "order": 订单解析器 (order_id, status, amount)
- "product": 产品解析器 (name, price, category)

只需实现工厂的 get_parser() 方法和 __repr__() 方法，
具体 Parser 模型的验证逻辑由框架处理。
"""

AVAILABLE_PARSERS = ["movie", "order", "product"]


def exercise_5() -> dict:
    """练习 5：Parser 工厂，根据类型名返回对应 Parser"""
    pass


# ============================================================
# 单元测试（内嵌在文件末尾）
# ============================================================


class TestExercise1(unittest.TestCase):
    """练习 1 测试：嵌套 Pydantic 模型"""

    def test_parse_resume_fields(self):
        result = exercise_1()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["name"], "李明")
        self.assertEqual(result["email"], "liming@example.com")

    def test_parse_resume_nested(self):
        result = exercise_1()
        self.assertIsInstance(result["education"], list)
        self.assertEqual(len(result["education"]), 2)
        self.assertEqual(result["education"][0]["school"], "清华大学")

    def test_parse_resume_experience(self):
        result = exercise_1()
        self.assertEqual(len(result["experience"]), 2)
        self.assertEqual(result["experience"][0]["company"], "字节跳动")
        self.assertIn("推荐系统重构", result["experience"][0]["highlights"][0])

    def test_parse_resume_skills(self):
        result = exercise_1()
        self.assertIn("Python", result["skills"])
        self.assertIsInstance(result["skills"], list)

    def test_parse_returns_pydantic_object(self):
        result = exercise_1()
        # 修复：exercise_1 返回 model_dump() 的 dict（LangChain 标准用法）
        # dict 包含所有字段，且支持 result["key"] 字典式访问
        self.assertIsInstance(result, dict)
        # 同时验证它有 Pydantic 模型的所有关键字段
        self.assertIn("name", result)
        self.assertIn("education", result)
        self.assertIn("experience", result)
        self.assertIn("skills", result)


class TestExercise2(unittest.TestCase):
    """练习 2 测试：容错 JSON Parser"""

    def test_fix_single_quotes(self):
        result = exercise_2()
        self.assertEqual(result["name"], "张三")

    def test_fix_unquoted_keys(self):
        result = exercise_2()
        self.assertIn("age", result)
        self.assertEqual(result["age"], 28)

    def test_fix_trailing_comma(self):
        result = exercise_2()
        self.assertIn("score", result)
        self.assertEqual(result["score"], 95.5)

    def test_fix_array_trailing_comma(self):
        result = exercise_2()
        self.assertIn("tags", result)
        self.assertEqual(result["tags"], ["Python", "AI"])

    def test_full_parse_result(self):
        result = exercise_2()
        self.assertEqual(result["name"], "张三")
        self.assertEqual(result["age"], 28)
        self.assertEqual(result["score"], 95.5)
        self.assertEqual(result["tags"], ["Python", "AI"])


class TestExercise3(unittest.TestCase):
    """练习 3 测试：自定义任务 Parser"""

    def test_parse_task_names(self):
        result = exercise_3()
        self.assertIsInstance(result, list)
        titles = [r["task"] for r in result]
        self.assertIn("完成项目报告", titles)
        self.assertIn("回复邮件", titles)
        self.assertIn("准备会议", titles)
        self.assertIn("阅读文档", titles)

    def test_parse_priority_high(self):
        result = exercise_3()
        high_priority = [r for r in result if r["priority"] == "高"]
        self.assertGreaterEqual(len(high_priority), 2)

    def test_parse_priority_medium(self):
        result = exercise_3()
        medium = [r for r in result if r["priority"] == "中"]
        self.assertEqual(len(medium), 1)
        self.assertEqual(medium[0]["task"], "回复邮件")

    def test_parse_deadline(self):
        result = exercise_3()
        with_deadline = [r for r in result if r.get("deadline")]
        self.assertEqual(len(with_deadline), 2)
        self.assertIn("2024-06-15", [r["deadline"] for r in with_deadline])

    def test_parse_no_priority_default(self):
        result = exercise_3()
        no_priority = [
            r
            for r in result
            if "无优先级" in r.get("raw", "") or r.get("priority") == "中"
        ]
        self.assertGreater(len(no_priority), 0)


class TestExercise4(unittest.TestCase):
    """练习 4 测试：多格式组合 Parser"""

    def test_parse_yaml_section(self):
        result = exercise_4()
        self.assertIn("分析", result)
        self.assertIn("该用户反馈了性能问题", result["分析"])
        self.assertIn("建议", result)
        self.assertIn("优化数据库查询", result["建议"])

    def test_parse_json_section(self):
        result = exercise_4()
        self.assertIn("severity", result)
        self.assertEqual(result["severity"], "high")
        self.assertEqual(result["category"], "performance")

    def test_parse_action_items(self):
        result = exercise_4()
        self.assertIn("action_items", result)
        self.assertIn("优化 SQL", result["action_items"][0])

    def test_full_result_structure(self):
        result = exercise_4()
        self.assertIn("分析", result)
        self.assertIn("severity", result)
        self.assertIn("action_items", result)


class TestExercise5(unittest.TestCase):
    """练习 5 测试：Parser 工厂"""

    def test_movie_parser_output(self):
        result = exercise_5()
        self.assertIn("movie", result)
        self.assertIsInstance(result["movie"], PydanticOutputParser)

    def test_order_parser_output(self):
        result = exercise_5()
        self.assertIn("order", result)
        self.assertIsInstance(result["order"], PydanticOutputParser)

    def test_product_parser_output(self):
        result = exercise_5()
        self.assertIn("product", result)
        self.assertIsInstance(result["product"], PydanticOutputParser)

    def test_repr_includes_type(self):
        result = exercise_5()
        movie_repr = repr(result["movie"])
        self.assertIn("movie", movie_repr.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
