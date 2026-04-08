"""
Day 12 - 练习题：Output Parser 进阶实践
"""

from langchain_core.output_parsers import (
    PydanticOutputParser,
    JsonOutputParser,
    RetryOutputParser,
    BaseOutputParser,
)
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
import re


# =============================================
# 练习 1：JSON 解析器基础
# =============================================
"""
使用 JsonOutputParser 从 LLM 输出中提取产品信息。
"""

def exercise_1():
    """练习 1：JSON 解析器基础"""
    print("=" * 50)
    print("练习 1：JSON 解析器基础")
    print("=" * 50)

    # 步骤 1：创建 JsonOutputParser

    # 步骤 2：模拟 LLM 输出
    llm_output = '''
    {
        "product_name": "iPhone 15 Pro",
        "brand": "Apple",
        "price": 9999,
        "colors": ["黑色钛金属", "白色钛金属", "蓝色钛金属", "原色钛金属"],
        "storage_options": [128, 256, 512, 1024],
        "in_stock": true
    }
    '''

    # 步骤 3：解析输出

    # 步骤 4：提取并打印产品信息
    # product_name, brand, price, colors, storage_options, in_stock

    # 步骤 5：使用 get_format_instructions 打印格式指令

    print()


# =============================================
# 练习 2：Pydantic 模型设计 - 新闻文章解析
# =============================================
"""
设计一个 Pydantic 模型来解析新闻文章，包含：
- 标题、作者、发布日期、类别、标签
- 正文内容（取前100字）
- 新闻来源
- 可选：副标题
"""

def exercise_2():
    """练习 2：Pydantic 模型设计 - 新闻文章解析"""
    print("=" * 50)
    print("练习 2：Pydantic 模型设计 - 新闻文章解析")
    print("=" * 50)

    # 步骤 1：定义 NewsArticle Pydantic 模型
    # 使用 Field 添加 description，使用 Optional 处理可选字段

    # 步骤 2：创建 PydanticOutputParser

    # 步骤 3：模拟 LLM 输出
    llm_output = '''
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
    '''

    # 步骤 4：解析并验证

    # 步骤 5：打印解析结果

    print()


# =============================================
# 练习 3：自定义 Markdown 任务列表解析器
# =============================================
"""
创建一个自定义 Parser，解析 LLM 输出的 Markdown 格式任务列表。
任务格式示例：
- [ ] 完成任务一 [高]
- [x] 已完成的任务
- [ ] 普通任务 2024-06-20

解析结果应为 TaskItem 列表，每个任务包含：
- title: 任务标题
- priority: 优先级（高/中/低），默认为"中"
- deadline: 截止日期（可选）
"""

class TaskItem(BaseModel):
    """任务数据模型"""
    # TODO: 定义字段


class TaskListParser(BaseOutputParser[List[TaskItem]]):
    """解析 Markdown 格式的任务列表"""

    def parse(self, text: str) -> List[TaskItem]:
        # TODO: 实现解析逻辑
        # 1. 逐行解析 Markdown 任务列表 (- [ ] 或 - [x])
        # 2. 提取任务标题
        # 3. 识别优先级 [高]/[中]/[低]
        # 4. 提取截止日期 (YYYY-MM-DD)
        # 5. 返回 TaskItem 列表
        pass

    def get_format_instructions(self) -> str:
        return """请用 Markdown 任务列表格式输出，每个任务一行。
已完成的任务用 [x]，未完成的用 [ ]。
可在任务后加 [高]/[中]/[低] 表示优先级。
例如：
- [ ] 完成任务一 [高]
- [x] 已完成的任务
- [ ] 普通任务"""


def exercise_3():
    """练习 3：自定义 Markdown 任务列表解析器"""
    print("=" * 50)
    print("练习 3：自定义 Markdown 任务列表解析器")
    print("=" * 50)

    parser = TaskListParser()

    llm_output = '''
今日任务清单：
- [ ] 完成项目报告 [高]
- [x] 回复邮件
- [ ] 准备会议资料 [中]
- [ ] 预约医生 2024-06-20 [低]
- [ ] 阅读文档
'''

    # TODO: 使用 parser 解析 llm_output

    # TODO: 遍历结果，打印每个任务的信息

    print()


# =============================================
# 练习 4：带重试的错误处理
# =============================================
"""
使用 RetryOutputParser 实现一个健壮的 JSON 解析链。
当 LLM 输出格式不正确时，自动重试。
"""

def exercise_4():
    """练习 4：带重试的错误处理"""
    print("=" * 50)
    print("练习 4：带重试的错误处理")
    print("=" * 50)

    # 步骤 1：创建基础 JsonOutputParser

    # 步骤 2：包装为带重试的 RetryOutputParser
    # 设置 max_retries=3, retry_on_parse_error=True

    # 步骤 3：测试正常 JSON
    good_output = '{"name": "测试", "value": 100}'
    # TODO: 使用 retry_parser 解析

    # 步骤 4：测试无效 JSON（会被重试）
    bad_output = "这是一个无效的 JSON"
    # TODO: 使用 retry_parser 解析，观察重试行为

    print()
    print("RetryOutputParser 会在解析失败时自动重试。")
    print("实际使用时，LLM 会根据错误信息重新生成正确格式的输出。")
    print()


# =============================================
# 练习 5：综合实战 - 简历解析系统
# =============================================
"""
完整实现一个简历解析系统，支持提取：
- 基本信息（姓名、邮箱、电话）
- 技能列表
- 教育经历（学校、学位、专业、毕业年份）
- 工作经验（公司、职位、工作时间、描述）
"""

class Education(BaseModel):
    """教育经历模型"""
    # TODO: 定义字段
    pass


class WorkExperience(BaseModel):
    """工作经验模型"""
    # TODO: 定义字段
    pass


class Resume(BaseModel):
    """简历模型"""
    # TODO: 定义字段
    pass


def exercise_5():
    """练习 5：综合实战 - 简历解析系统"""
    print("=" * 50)
    print("练习 5：综合实战 - 简历解析系统")
    print("=" * 50)

    # 步骤 1：创建 PydanticOutputParser

    # 步骤 2：模拟 LLM 解析后的简历数据
    llm_output = '''
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
'''

    # 步骤 3：解析简历数据

    # 步骤 4：打印解析结果
    # 姓名、邮箱、电话、技能列表、教育经历、工作经验

    print()


# =============================================
# 运行所有练习
# =============================================
if __name__ == "__main__":
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