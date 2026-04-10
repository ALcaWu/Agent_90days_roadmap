"""
Day 12 - 练习题：Output Parser 进阶实践
"""

from langchain_core.output_parsers import (
    PydanticOutputParser,
    JsonOutputParser,
    BaseOutputParser,
)
from langchain_core.prompts import PromptTemplate
from openai import skills
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
import re
import unittest


# =============================================
# 练习 1：JSON 解析器基础
# =============================================
"""
使用 JsonOutputParser 从 LLM 输出中提取产品信息。
"""


def exercise_1() -> dict:
    """
    练习 1：JSON 解析器基础，返回解析后的 dict

    步骤：
    1. 创建 JsonOutputParser
    2. 用下面的 llm_output 作为模拟 LLM 输出
    3. 解析输出，打印产品信息（product_name、brand、price、colors、storage_options、in_stock）
    4. 打印 parser.get_format_instructions()
    5. 返回解析结果 dict
    """
    llm_output = """
    {
        "product_name": "iPhone 15 Pro",
        "brand": "Apple",
        "price": 9999,
        "colors": ["黑色钛金属", "白色钛金属", "蓝色钛金属", "原色钛金属"],
        "storage_options": [128, 256, 512, 1024],
        "in_stock": true
    }
    """
    parser = JsonOutputParser()
    result = parser.parse(llm_output)
    print(
        f"product_name: {result['product_name']}, brand: {result['brand']},"
        f"price: {result['price']},colro:{result['colors']},storage_options:{result['storage_options']},"
        f"in_stock:{result['in_stock']}"
    )
    print(parser.get_format_instructions())
    return result



# =============================================
# 练习 2：Pydantic 模型设计 - 新闻文章解析
# =============================================


class NewsArticle(BaseModel):
    headline: str = Field(description="新闻标题")
    subheadline: Optional[str] = Field(description="副标题", default=None)
    author: str = Field(description="作者")
    publish_date: str = Field(description="发布日期 YYYY-MM-DD")
    category: str = Field(description="新闻类别")
    tags: List[str] = Field(description="标签列表")
    content: str = Field(description="正文内容")
    source: str = Field(description="新闻来源")


def exercise_2() -> NewsArticle:
    """
    练习 2：Pydantic 模型设计 - 新闻文章解析，返回 NewsArticle 对象

    步骤：
    1. 创建 PydanticOutputParser(pydantic_object=NewsArticle)
    2. 用下面的 llm_output 作为模拟输出进行解析
    3. 打印标题、副标题、作者、日期、类别、标签、来源
    4. 返回 NewsArticle 实例
    """
    llm_output = """
    {
        "headline": "人工智能在医疗领域取得重大突破",
        "subheadline": "AI诊断准确率首次超过人类专家",
        "author": "张三",
        "publish_date": "2024-06-15",
        "category": "科技",
        "tags": ["人工智能", "医疗", "科技突破"],
        "content": "近日，一款基于深度学习的人工智能诊断系统在...（正文内容省略）",
        "source": "科技日报"
    }
    """
    parser = PydanticOutputParser(pydantic_object=NewsArticle)
    result = parser.parse(llm_output)
    print(f"headline: {result.headline}")
    print(f"subheadline: {result.subheadline}")
    print(f"author: {result.author}")
    print(f"publish_date: {result.publish_date}")
    print(f"category: {result.category}")
    print(f"tags: {result.tags}")
    print(f"source: {result.source}")
        
    return result


# =============================================
# 练习 3：自定义 Markdown 任务列表解析器
# =============================================


class TaskItem(BaseModel):
    """任务数据模型"""

    title: str = Field(description="任务标题")
    completed: bool = Field(description="是否已完成", default=False)
    priority: str = Field(description="优先级：高/中/低", default="中")
    deadline: Optional[str] = Field(description="截止日期 YYYY-MM-DD", default=None)


class TaskListParser(BaseOutputParser[List[TaskItem]]):
    """
    练习 3：继承 BaseOutputParser，解析 Markdown 格式的任务列表。

    格式示例：
    - [ ] 完成项目报告 [高]
    - [x] 回复邮件
    - [ ] 预约医生 2024-06-20 [低]

    要求：
    - 解析 [ ] / [x] 表示未完成 / 已完成
    - 提取 [高]/[中]/[低] 作为 priority（默认"中"）
    - 提取 YYYY-MM-DD 格式日期作为 deadline（默认 None）
    - 实现 get_format_instructions() 返回格式说明字符串
    """
    def parse(self, text: str) -> List[TaskItem]:
        lines = text.strip().split('\n')
        result = []

        for line in lines:
            # 匹配 - [ ] 或 - [x] 开头的行
            match = re.match(r'^\s*-\s+\[([ x])\]\s+(.+)$', line)
            if not match:
                continue

            completed = match.group(1) == 'x'
            content = match.group(2).strip()

            # 提取优先级 [高]/[中]/[低]
            priority = "中"
            priority_match = re.search(r'\[(高|中|低)\]', content)
            if priority_match:
                priority = priority_match.group(1)
                content = content[:priority_match.start()].strip()

            # 提取截止日期 YYYY-MM-DD
            deadline = None
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', content)
            if date_match:
                deadline = date_match.group(1)
                content = content[:date_match.start()].strip()

            result.append(TaskItem(
                title=content,
                completed=completed,
                priority=priority,
                deadline=deadline,
            ))

        return result

    def get_format_instructions(self) -> str:
        return """请用 Markdown 任务列表格式输出，每个任务一行。
                已完成的任务用 [x]，未完成的用 [ ]。
                可在任务后加 [高]/[中]/[低] 表示优先级。
                例如：
                - [ ] 完成任务一 [高]
                - [x] 已完成的任务
                - [ ] 普通任务"""


def exercise_3() -> List[TaskItem]:
    """练习 3：使用 TaskListParser 解析下面的任务列表，打印每条任务，返回 TaskItem 列表"""
    print("=" * 50)
    print("练习 3：自定义 Markdown 任务列表解析器")
    print("=" * 50)

    parser = TaskListParser()

    llm_output = """
今日任务清单：
- [ ] 完成项目报告 [高]
- [x] 回复邮件
- [ ] 准备会议资料 [中]
- [ ] 预约医生 2024-06-20 [低]
- [ ] 阅读文档
"""

    tasks = parser.parse(llm_output)

    for task in tasks:
        status = "[完成]" if task.completed else "[待办]"
        deadline_str = f"  截止: {task.deadline}" if task.deadline else ""
        print(f"{status} [{task.priority}] {task.title}{deadline_str}")

    print()
    return tasks


# =============================================
# 练习 4：异常处理与手动重试（替代已移除的 RetryOutputParser）
# =============================================
# 注意：RetryOutputParser 已从 langchain_core 中移除。
# 现代写法：用 try-except 包裹解析逻辑，根据需要手动重试。
# 如需自动修复格式，可结合 LLM 调用使用 OutputFixingParser（需要 langchain 包）。


def parse_with_retry(parser: BaseOutputParser, text: str, max_retries: int = 3):
    """
    练习 4：通用解析重试函数。

    要求：
    - 解析失败时最多重试 max_retries 次
    - 每次失败打印 "第 N 次解析失败: 错误类型"
    - 超过最大次数后打印提示并返回 None
    - 成功时直接返回解析结果
    """
    for attempt in range(1, max_retries + 1):
        try:
            return parser.parse(text)
        except Exception as e:
            print(f"  第 {attempt} 次尝试失败: {type(e).__name__}")
            if attempt == max_retries:
                print(f"  已达最大重试次数 {max_retries}，放弃解析")
                return None
    pass


def exercise_4():
    json_parser = JsonOutputParser()
    """练习 4：演示 parse_with_retry 对有效/无效 JSON 的处理，返回无效 JSON 的解析结果"""
    # 测试：有效 JSON
    good_output = '{"name": "测试", "value": 100}'
    result = parse_with_retry(json_parser, good_output)
    print(f"有效 JSON 解析结果: {result}")

    # 测试：无效 JSON
    bad_output = "这是一个无效的 JSON 输出。"
    result = parse_with_retry(json_parser, bad_output, max_retries=3)
    print(f"无效 JSON 最终结果: {result}")
    pass


# =============================================
# 练习 5：综合实战 - 简历解析系统
# =============================================


class Education(BaseModel):
    """教育经历模型"""

    school: str = Field(description="学校名称")
    degree: str = Field(description="学位：本科/硕士/博士")
    major: str = Field(description="专业")
    graduation_year: int = Field(description="毕业年份")


class WorkExperience(BaseModel):
    """工作经验模型"""

    company: str = Field(description="公司名称")
    position: str = Field(description="职位")
    duration: str = Field(description="工作时间，如 2020-至今")
    description: str = Field(description="工作描述")


class Resume(BaseModel):
    """简历模型"""

    name: str = Field(description="姓名")
    email: str = Field(description="邮箱")
    phone: str = Field(description="电话")
    skills: List[str] = Field(description="技能列表")
    education: List[Education] = Field(description="教育经历列表")
    experience: List[WorkExperience] = Field(description="工作经验列表")


def exercise_5() -> Resume:
    """
    练习 5：综合实战 - 简历解析系统，返回 Resume 对象

    步骤：
    1. 创建 PydanticOutputParser(pydantic_object=Resume)
    2. 用下面的 llm_output 作为模拟输出进行解析
    3. 打印姓名、邮箱、电话、技能列表
    4. 打印教育经历（school / degree / major / graduation_year）
    5. 打印工作经验（company / position / duration / description）
    6. 返回 Resume 实例
    """
    llm_output = """
{
    "name": "李四",
    "email": "lisi@example.com",
    "phone": "139-0013-9000",
    "skills": ["Python", "JavaScript", "React", "Node.js", "PostgreSQL", "Docker"],
    "education": [
        {
            "school": "清华大学",
            "degree": "硕士",
            "major": "计算机科学与技术",
            "graduation_year": 2020
        },
        {
            "school": "北京大学",
            "degree": "本科",
            "major": "软件工程",
            "graduation_year": 2017
        }
    ],
    "experience": [
        {
            "company": "字节跳动",
            "position": "高级后端工程师",
            "duration": "2020-至今",
            "description": "负责推荐系统后端开发，使用 Python + Go"
        },
        {
            "company": "腾讯",
            "position": "后端开发工程师",
            "duration": "2017-2020",
            "description": "参与微信小程序后端开发"
        }
    ]
}
"""
    parser = PydanticOutputParser(pydantic_object=Resume)
    llm_output = parser.parse(llm_output)
    print(f"姓名：{llm_output.name}", f"邮箱：{llm_output.email}", f"电话：{llm_output.phone}", sep="\n")
    for skill in llm_output.skills:
        print(f"技能：{skill}")

    for education in llm_output.education:
        print(f"教育经历：{education.school} {education.degree} {education.major} {education.graduation_year}")

    for experience in llm_output.experience:
        print(f"工作经历：{experience.company} {experience.position} {experience.duration} {experience.description}")

    return llm_output
    pass


# =============================================
# 运行所有练习
# =============================================
def run_exercises():
    print("\n" + "=" * 60)
    print("Day 12 练习题 - Output Parser 进阶实践")
    print("=" * 60 + "\n")

    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()

    print("\n" + "=" * 60)
    print("所有练习完成！")
    print("=" * 60)


# =============================================
# 单元测试
# =============================================
class TestExercise1(unittest.TestCase):
    """练习 1：JSON 解析器基础"""

    def test_returns_dict(self):
        """exercise_1 应返回 dict"""
        result = exercise_1()
        self.assertIsInstance(result, dict)

    def test_product_name(self):
        """应包含正确的产品名称"""
        result = exercise_1()
        self.assertEqual(result["product_name"], "iPhone 15 Pro")

    def test_brand(self):
        """应包含品牌字段"""
        result = exercise_1()
        self.assertEqual(result["brand"], "Apple")

    def test_colors_is_list(self):
        """颜色字段应为列表"""
        result = exercise_1()
        self.assertIsInstance(result["colors"], list)
        self.assertEqual(len(result["colors"]), 4)

    def test_in_stock_is_bool(self):
        """in_stock 字段应为布尔值"""
        result = exercise_1()
        self.assertIsInstance(result["in_stock"], bool)
        self.assertTrue(result["in_stock"])


class TestExercise2(unittest.TestCase):
    """练习 2：Pydantic 模型设计 - 新闻文章解析"""

    def test_returns_news_article(self):
        """应返回 NewsArticle 实例"""
        result = exercise_2()
        self.assertIsInstance(result, NewsArticle)

    def test_headline(self):
        """标题应正确解析"""
        result = exercise_2()
        self.assertIn("人工智能", result.headline)

    def test_subheadline_optional(self):
        """副标题字段存在（本次不为 None）"""
        result = exercise_2()
        self.assertIsNotNone(result.subheadline)

    def test_tags_is_list(self):
        """标签应为列表且不为空"""
        result = exercise_2()
        self.assertIsInstance(result.tags, list)
        self.assertGreater(len(result.tags), 0)

    def test_source(self):
        """来源字段正确"""
        result = exercise_2()
        self.assertEqual(result.source, "科技日报")


class TestExercise3(unittest.TestCase):
    """练习 3：自定义 Markdown 任务列表解析器"""

    def setUp(self):
        self.parser = TaskListParser()
        self.sample = """
- [ ] 完成项目报告 [高]
- [x] 回复邮件
- [ ] 准备会议资料 [中]
- [ ] 预约医生 2024-06-20 [低]
- [ ] 阅读文档
"""
        self.tasks = self.parser.parse(self.sample)

    def test_returns_list(self):
        """应返回列表"""
        self.assertIsInstance(self.tasks, list)

    def test_correct_count(self):
        """应解析出 5 个任务"""
        self.assertEqual(len(self.tasks), 5)

    def test_completed_task(self):
        """已完成任务标记正确"""
        completed = [t for t in self.tasks if t.completed]
        self.assertEqual(len(completed), 1)
        self.assertIn("回复邮件", completed[0].title)

    def test_high_priority(self):
        """高优先级任务解析正确"""
        high = [t for t in self.tasks if t.priority == "高"]
        self.assertEqual(len(high), 1)
        self.assertIn("完成项目报告", high[0].title)

    def test_deadline_parsed(self):
        """截止日期正确提取"""
        tasks_with_deadline = [t for t in self.tasks if t.deadline is not None]
        self.assertEqual(len(tasks_with_deadline), 1)
        self.assertEqual(tasks_with_deadline[0].deadline, "2024-06-20")

    def test_default_priority(self):
        """无优先级标记的任务默认为'中'"""
        no_mark = [t for t in self.tasks if t.title == "阅读文档"]
        self.assertEqual(len(no_mark), 1)
        self.assertEqual(no_mark[0].priority, "中")


class TestExercise4(unittest.TestCase):
    """练习 4：异常处理与手动重试"""

    def test_parse_valid_json(self):
        """有效 JSON 应成功解析"""
        parser = JsonOutputParser()
        result = parse_with_retry(parser, '{"key": "value"}')
        self.assertIsNotNone(result)
        self.assertEqual(result["key"], "value")

    def test_parse_invalid_json_returns_none(self):
        """无效 JSON 达到最大重试次数后应返回 None"""
        parser = JsonOutputParser()
        result = parse_with_retry(parser, "这不是 JSON", max_retries=2)
        self.assertIsNone(result)

    def test_retry_count(self):
        """重试次数参数应被遵守"""
        from unittest.mock import patch
        from langchain_core.exceptions import OutputParserException

        parser = JsonOutputParser()
        attempts = []

        def side_effect(text):
            attempts.append(1)
            raise OutputParserException("mock parse error")

        with patch.object(type(parser), "parse", side_effect=side_effect):
            parse_with_retry(parser, "invalid", max_retries=3)

        self.assertEqual(len(attempts), 3)


class TestExercise5(unittest.TestCase):
    """练习 5：综合实战 - 简历解析系统"""

    def setUp(self):
        self.resume = exercise_5()

    def test_returns_resume(self):
        """应返回 Resume 实例"""
        self.assertIsInstance(self.resume, Resume)

    def test_basic_info(self):
        """基本信息应正确解析"""
        self.assertEqual(self.resume.name, "李四")
        self.assertEqual(self.resume.email, "lisi@example.com")

    def test_skills_list(self):
        """技能列表不为空"""
        self.assertIsInstance(self.resume.skills, list)
        self.assertIn("Python", self.resume.skills)

    def test_education_count(self):
        """教育经历条目数正确"""
        self.assertEqual(len(self.resume.education), 2)

    def test_education_type(self):
        """教育经历应为 Education 实例"""
        for edu in self.resume.education:
            self.assertIsInstance(edu, Education)

    def test_experience_count(self):
        """工作经验条目数正确"""
        self.assertEqual(len(self.resume.experience), 2)

    def test_experience_type(self):
        """工作经验应为 WorkExperience 实例"""
        for exp in self.resume.experience:
            self.assertIsInstance(exp, WorkExperience)

    def test_nested_field(self):
        """嵌套字段可正常访问"""
        self.assertEqual(self.resume.education[0].school, "清华大学")
        self.assertEqual(self.resume.experience[0].company, "字节跳动")


if __name__ == "__main__":
    # 先运行所有练习展示效果
    run_exercises()
    print("\n" + "=" * 60)
    print("开始运行单元测试")
    print("=" * 60 + "\n")
    unittest.main(verbosity=2)
