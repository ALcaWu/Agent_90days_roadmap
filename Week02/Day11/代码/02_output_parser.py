# -*- coding: utf-8 -*-
"""
Day 11 - Output Parser 输出解析
知识点：StrOutputParser、JsonOutputParser、PydanticOutputParser、CommaSeparatedListOutputParser
"""

import os
from typing import List, Optional

from langchain_core.output_parsers import (
    StrOutputParser,
    JsonOutputParser,
    CommaSeparatedListOutputParser,
)
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from pydantic import BaseModel, Field

# ==================== 1. StrOutputParser ====================

print("=" * 50)
print("1. StrOutputParser - 字符串解析器")
print("=" * 50)

parser = StrOutputParser()
print(f"解析器类型：{type(parser).__name__}")
print("作用：直接提取 AIMessage.content 中的字符串")

# 模拟 AIMessage 输入
from langchain_core.messages import AIMessage
mock_response = AIMessage(content="  Hello World  \n")
result = parser.invoke(mock_response)
print(f"解析结果：'{result}'")  # 'Hello World'（自动 strip）


# ==================== 2. CommaSeparatedListOutputParser ====================

print("\n" + "=" * 50)
print("2. CommaSeparatedListOutputParser - 列表解析器")
print("=" * 50)

list_parser = CommaSeparatedListOutputParser()

# 查看格式指令（会注入到 Prompt 中）
format_instructions = list_parser.get_format_instructions()
print(f"格式指令：{format_instructions}")

# 模拟解析逗号分隔文本
mock_list_output = "苹果, 香蕉, 橙子, 西瓜, 草莓"
parsed_list = list_parser.invoke(mock_list_output)
print(f"解析结果：{parsed_list}")
print(f"数据类型：{type(parsed_list)}")

# 构建完整 Prompt
list_prompt = PromptTemplate(
    template="列出5种{category}。\n{format_instructions}",
    input_variables=["category"],
    partial_variables={"format_instructions": format_instructions},
)

print(f"\n完整 Prompt 示例：")
print(list_prompt.invoke({"category": "编程语言"}).text)


# ==================== 3. JsonOutputParser ====================

print("\n" + "=" * 50)
print("3. JsonOutputParser - JSON 解析器")
print("=" * 50)

import json

json_parser = JsonOutputParser()
print(f"格式指令：{json_parser.get_format_instructions()[:80]}...")

# 模拟解析 JSON 字符串
mock_json_output = '{"name": "张三", "age": 25, "skills": ["Python", "LangChain"]}'
parsed_dict = json_parser.invoke(mock_json_output)
print(f"\n解析结果：{parsed_dict}")
print(f"数据类型：{type(parsed_dict)}")
print(f"访问字段：name={parsed_dict['name']}, age={parsed_dict['age']}")


# ==================== 4. PydanticOutputParser ====================

print("\n" + "=" * 50)
print("4. PydanticOutputParser - 类型安全解析器（推荐）")
print("=" * 50)

from langchain_core.output_parsers import PydanticOutputParser


# 4.1 定义业务数据结构
class JobPosting(BaseModel):
    """招聘信息结构"""
    title: str = Field(description="职位名称")
    company: str = Field(description="公司名称")
    salary_range: str = Field(description="薪资范围，如 20k-30k")
    required_skills: List[str] = Field(description="必备技能列表")
    experience_years: int = Field(description="所需工作年限", ge=0)
    is_remote: bool = Field(description="是否支持远程工作")


# 4.2 创建解析器
pydantic_parser = PydanticOutputParser(pydantic_object=JobPosting)
print("格式指令（前200字）：")
print(pydantic_parser.get_format_instructions()[:200] + "...\n")

# 4.3 模拟解析 JSON 字符串（实际场景中由 LLM 生成）
mock_job_json = json.dumps({
    "title": "高级Agent开发工程师",
    "company": "某AI科技公司",
    "salary_range": "30k-50k",
    "required_skills": ["Python", "LangChain", "LangGraph", "RAG", "FastAPI"],
    "experience_years": 3,
    "is_remote": True
}, ensure_ascii=False)

job = pydantic_parser.invoke(mock_job_json)

print(f"解析结果类型：{type(job)}")
print(f"职位：{job.title}")
print(f"公司：{job.company}")
print(f"薪资：{job.salary_range}")
print(f"技能要求：{', '.join(job.required_skills)}")
print(f"经验年限：{job.experience_years}年")
print(f"支持远程：{'✅' if job.is_remote else '❌'}")

# 4.4 类型验证演示
print("\n--- 验证类型约束 ---")
try:
    invalid_data = '{"title": "测试", "company": "测试公司", "salary_range": "20k", "required_skills": [], "experience_years": -1, "is_remote": false}'
    invalid_job = pydantic_parser.invoke(invalid_data)
    print("❌ 应该报错（experience_years 不能为负）")
except Exception as e:
    print(f"✅ 类型验证正常工作：{type(e).__name__}")


# ==================== 5. 构建完整解析链（不调用真实 API）====================

print("\n" + "=" * 50)
print("5. 完整 LCEL 解析链结构展示")
print("=" * 50)

# 展示链的结构（不实际调用 API）
job_prompt = PromptTemplate(
    template="""请根据以下信息生成一个招聘岗位的结构化数据。
{format_instructions}

岗位描述：{description}""",
    input_variables=["description"],
    partial_variables={"format_instructions": pydantic_parser.get_format_instructions()},
)

print("完整的 LCEL 链结构：")
print("  job_prompt | ChatOpenAI(...) | pydantic_parser")
print()
print("调用示例（需要真实 API Key）：")
print("""
  chain = job_prompt | ChatOpenAI(model="gpt-3.5-turbo") | pydantic_parser
  job = chain.invoke({"description": "招一名资深Python工程师..."})
  print(job.title)          # 直接访问类型安全的字段
  print(job.required_skills)  # List[str]
""")

print("✅ Output Parser 代码运行完成！")
