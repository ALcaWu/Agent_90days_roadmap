"""
Day 12 - 代码示例 2：PydanticOutputParser 进阶用法
深入学习如何使用 Pydantic 模型进行复杂结构解析
"""

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum
import json

# =============================================
# 1. 基础 Pydantic 模型解析
# =============================================
print("=" * 50)
print("1. 基础 Pydantic 模型解析")
print("=" * 50)

class Book(BaseModel):
    title: str = Field(description="书名")
    author: str = Field(description="作者")
    publish_year: int = Field(description="出版年份")
    rating: float = Field(description="评分", ge=0, le=10)
    genres: List[str] = Field(description="类型列表")

parser = PydanticOutputParser(pydantic_object=Book)

# 模拟 LLM 输出
llm_output = '''
{
    "title": "Python编程：从入门到实践",
    "author": "Eric Matthes",
    "publish_year": 2016,
    "rating": 9.2,
    "genres": ["编程", "技术", "Python"]
}
'''

result = parser.parse(llm_output)
print(f"解析结果:")
print(f"  书名: {result.title}")
print(f"  作者: {result.author}")
print(f"  年份: {result.publish_year}")
print(f"  评分: {result.rating}")
print(f"  类型: {result.genres}")
print(f"  类型验证: {type(result)}")
print()

# =============================================
# 2. 带验证的 Pydantic 模型
# =============================================
print("=" * 50)
print("2. 带验证的 Pydantic 模型")
print("=" * 50)

class UserProfile(BaseModel):
    username: str = Field(description="用户名", min_length=3, max_length=20)
    email: str = Field(description="邮箱地址")
    age: int = Field(description="年龄", ge=0, le=150)
    phone: Optional[str] = Field(description="电话号码", default=None)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v or '.' not in v:
            raise ValueError('邮箱格式不正确')
        return v

parser = PydanticOutputParser(pydantic_object=UserProfile)

# 测试有效数据
valid_output = '''
{
    "username": "john_doe",
    "email": "john@example.com",
    "age": 28,
    "phone": "138-0013-8000"
}
'''

result = parser.parse(valid_output)
print(f"有效数据解析成功:")
print(f"  用户名: {result.username}")
print(f"  邮箱: {result.email}")
print(f"  年龄: {result.age}")
print()

# 测试无效数据
invalid_output = '''
{
    "username": "ab",
    "email": "invalid-email",
    "age": 200
}
'''

try:
    result = parser.parse(invalid_output)
    print(f"应该抛出验证错误")
except Exception as e:
    print(f"验证错误（预期行为）: {type(e).__name__}")
    print(f"错误信息: {str(e)[:100]}...")
print()

# =============================================
# 3. 嵌套 Pydantic 模型
# =============================================
print("=" * 50)
print("3. 嵌套 Pydantic 模型")
print("=" * 50)

class Address(BaseModel):
    street: str = Field(description="街道")
    city: str = Field(description="城市")
    country: str = Field(description="国家")

class Company(BaseModel):
    name: str = Field(description="公司名称")
    industry: str = Field(description="行业")
    founded_year: int = Field(description="成立年份")

class Employee(BaseModel):
    name: str = Field(description="员工姓名")
    employee_id: str = Field(description="工号")
    department: str = Field(description="部门")
    address: Address = Field(description="办公地址")
    company: Company = Field(description="所属公司")

parser = PydanticOutputParser(pydantic_object=Employee)

llm_output = '''
{
    "name": "张三",
    "employee_id": "EMP001",
    "department": "技术部",
    "address": {
        "street": "科技路123号",
        "city": "北京",
        "country": "中国"
    },
    "company": {
        "name": "某科技公司",
        "industry": "互联网",
        "founded_year": 2015
    }
}
'''

result = parser.parse(llm_output)
print(f"嵌套模型解析成功:")
print(f"  员工: {result.name}")
print(f"  部门: {result.department}")
print(f"  城市: {result.address.city}")
print(f"  公司: {result.company.name}")
print()

# =============================================
# 4. 列表嵌套模型
# =============================================
print("=" * 50)
print("4. 列表嵌套模型")
print("=" * 50)

class Course(BaseModel):
    name: str = Field(description="课程名称")
    instructor: str = Field(description="讲师")
    duration_hours: int = Field(description="课时数")

class Curriculum(BaseModel):
    major: str = Field(description="专业名称")
    total_credits: int = Field(description="总学分")
    courses: List[Course] = Field(description="课程列表")

parser = PydanticOutputParser(pydantic_object=Curriculum)

llm_output = '''
{
    "major": "计算机科学与技术",
    "total_credits": 160,
    "courses": [
        {
            "name": "数据结构与算法",
            "instructor": "李教授",
            "duration_hours": 64
        },
        {
            "name": "操作系统",
            "instructor": "王教授",
            "duration_hours": 48
        },
        {
            "name": "计算机网络",
            "instructor": "张教授",
            "duration_hours": 48
        }
    ]
}
'''

result = parser.parse(llm_output)
print(f"列表嵌套解析成功:")
print(f"  专业: {result.major}")
print(f"  总学分: {result.total_credits}")
print(f"  课程数量: {len(result.courses)}")
for i, course in enumerate(result.courses):
    print(f"    {i+1}. {course.name} - {course.instructor} ({course.duration_hours}课时)")
print()

# =============================================
# 5. 带默认值和可选字段
# =============================================
print("=" * 50)
print("5. 带默认值和可选字段")
print("=" * 50)

class Product(BaseModel):
    name: str = Field(description="产品名称")
    price: Optional[float] = Field(description="价格", default=None)
    description: Optional[str] = Field(description="描述", default=None)
    tags: List[str] = Field(description="标签", default_factory=list)

parser = PydanticOutputParser(pydantic_object=Product)

minimal_output = '''
{
    "name": "智能手表"
}
'''

result = parser.parse(minimal_output)
print(f"最小数据解析成功:")
print(f"  名称: {result.name}")
print(f"  价格: {result.price} (应为 None)")
print(f"  描述: {result.description} (应为 None)")
print(f"  标签: {result.tags} (应为空列表)")
print()

# =============================================
# 6. 枚举字段
# =============================================
print("=" * 50)
print("6. 枚举字段")
print("=" * 50)

class Priority(Enum):
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    URGENT = "紧急"

class Task(BaseModel):
    title: str = Field(description="任务标题")
    priority: Priority = Field(description="优先级")
    status: str = Field(description="状态")

parser = PydanticOutputParser(pydantic_object=Task)

llm_output = '''
{
    "title": "修复登录bug",
    "priority": "高",
    "status": "进行中"
}
'''

result = parser.parse(llm_output)
print(f"枚举字段解析成功:")
print(f"  任务: {result.title}")
print(f"  优先级: {result.priority} (类型: {type(result.priority)})")
print(f"  状态: {result.status}")
print(f"  优先级枚举值: {result.priority.value}")
print()

# =============================================
# 7. 使用 partial_variables 注入格式指令
# =============================================
print("=" * 50)
print("7. 使用 partial_variables 注入格式指令")
print("=" * 50)

class Recipe(BaseModel):
    name: str = Field(description="菜名")
    difficulty: str = Field(description="难度: 简单/中等/困难")
    prep_time: int = Field(description="准备时间（分钟）")
    ingredients: List[str] = Field(description="配料列表")
    steps: List[str] = Field(description="步骤列表")

parser = PydanticOutputParser(pydantic_object=Recipe)

prompt = PromptTemplate.from_template(
    """请提供一个{cuisine}菜谱的基本信息。

{format_instructions}

cuisine 类型: {cuisine}""",
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

print("生成的提示模板内容:")
print(prompt.format(cuisine="川菜"))
print()

print("=" * 50)
print("所有示例执行完成！")
print("=" * 50)