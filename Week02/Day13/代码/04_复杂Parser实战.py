# -*- coding: utf-8 -*-
"""
================================================================================
Day 13 - 04_复杂Parser实战
================================================================================
本文件演示复杂 Parser 的实战场景，包括：
  1. 多级嵌套模型：简历解析（Education + WorkExperience → Resume）
  2. field_validator 预处理：自动转换非标准输入（如 "2020年" → 2020）
  3. 联合类型（Union）：支持多种内容类型的解析
  4. AliasChoices：同一字段有多个可能的名字时（author/creator/username）
  5. 嵌套 Parser：父 Parser 内嵌子 Parser，各自独立验证

核心理解：
  - Pydantic 的嵌套验证是自动的：只要模型 A 中有字段类型是模型 B，
    B 的所有约束（Field、validator）会自动应用到该字段。
  - 联合类型让 Parser 能接受多种可能的结构。
================================================================================
"""

import re
from typing import List, Union, Literal, Annotated
from pydantic import BaseModel, Field, field_validator, AliasChoices
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate


# ==============================================================================
# 一、多级嵌套模型：简历解析
# ==============================================================================

class Education(BaseModel):
    """
    教育经历模型（子模型）：嵌套在 Resume 中。
    field_validator 处理多种年份格式，提高容错性。
    """
    school: str = Field(description="学校名称（全称）")
    degree: str = Field(description="学位，如 学士 / 硕士 / 博士")
    major: str = Field(description="专业名称")
    year: int = Field(ge=1950, le=2030, description="毕业年份，4位整数")

    @field_validator("year", mode="before")
    @classmethod
    def parse_year_from_string(cls, v):
        """
        预处理验证器：支持多种年份输入格式。
        LLM 可能输出 "2020年"、"(2020)"、"[2020]" 等格式，
        此处统一提取数字部分转为整数。
        """
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            # 提取第一个4位数字
            match = re.search(r"\d{4}", v.strip())
            if match:
                return int(match.group())
        # 如果是浮点数（如 2020.0），转为整数
        if isinstance(v, float):
            return int(v)
        return v


class WorkExperience(BaseModel):
    """
    工作经历模型（子模型）：包含公司、职位、时间段和工作亮点。
    """
    company: str = Field(description="公司全称")
    position: str = Field(description="职位名称")
    duration: str = Field(
        description="在职时间，格式为 YYYY.MM - YYYY.MM 或 YYYY年MM月 - 至今"
    )
    highlights: List[str] = Field(
        min_length=1, max_length=5,
        description="工作亮点或主要成就，3-5条"
    )

    @field_validator("duration", mode="before")
    @classmethod
    def normalize_duration(cls, v):
        """
        标准化时间段格式。
        LLM 可能输出不同的分隔符，此处统一为 "YYYY.MM - YYYY.MM" 格式。
        """
        if not isinstance(v, str):
            return v
        # 统一破折号
        v = v.replace("—", "-").replace("~", "-")
        return v.strip()


class Resume(BaseModel):
    """
    简历模型（根模型）：整合个人信息、教育和工作经历。

    嵌套验证的级联效果：
      当 Resume 收到 dict 时，Pydantic 会自动：
        education: List[dict] → List[Education]
        experience: List[dict] → List[WorkExperience]
      每一步都经过 Education / WorkExperience 的 validator 检查。
    """
    name: str = Field(min_length=1, max_length=50, description="真实姓名")
    email: str = Field(description="电子邮箱")
    phone: str | None = Field(default=None, description="手机号（可选）")
    education: List[Education] = Field(
        min_length=1, max_length=5,
        description="教育经历列表，至少1条"
    )
    experience: List[WorkExperience] = Field(
        min_length=1, max_length=10,
        description="工作经历列表，至少1条"
    )
    skills: List[str] = Field(
        min_length=1, max_length=20,
        description="技能列表，3-20项"
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """
        字段验证器（mode="after"，默认）：在类型转换后检查。
        这里验证邮箱格式，给出清晰的错误信息。
        """
        if "@" not in v or "." not in v:
            raise ValueError(f"无效的邮箱地址: {v}")
        return v.lower()  # 统一转为小写

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, v):
        """
        手机号标准化：去掉空格和短横线。
        LLM 可能输出 "138-1234-5678" 格式。
        """
        if v is None:
            return None
        if isinstance(v, str):
            # 去掉空格、横线，保留数字
            cleaned = re.sub(r"[\s\-]", "", v)
            # 验证是否是11位数字（以1开头）
            if re.match(r"^1\d{10}$", cleaned):
                return cleaned
        return v


print("=" * 60)
print("一、多级嵌套模型：简历解析")
print("=" * 60)

# 模拟 LLM 输出的简历 JSON（故意包含一些非标准格式）
fake_resume_json = """
{
  "name": "李明",
  "email": "Liming@Example.com",
  "phone": "138-1234-5678",
  "education": [
    {
      "school": "清华大学",
      "degree": "硕士",
      "major": "计算机科学",
      "year": "2020年"
    },
    {
      "school": "北京大学",
      "degree": "学士",
      "major": "软件工程",
      "year": 2017
    }
  ],
  "experience": [
    {
      "company": "字节跳动",
      "position": "高级算法工程师",
      "duration": "2021.03 - 至今",
      "highlights": [
        "设计并实现推荐系统核心算法",
        "优化模型推理效率，提升30%",
        "主导团队技术分享"
      ]
    }
  ],
  "skills": ["Python", "TensorFlow", "PyTorch", "算法设计", "分布式系统"]
}
"""

resume_parser = PydanticOutputParser(pydantic_object=Resume)
result = resume_parser.parse(fake_resume_json)

print(f"\n姓名: {result.name}")
print(f"邮箱: {result.email}（已自动转小写）")
print(f"手机: {result.phone}（已去除横线）")
print(f"\n教育经历:")
for edu in result.education:
    print(f"  {edu.school} | {edu.degree} | {edu.major} | {edu.year}年")
print(f"\n工作经历:")
for exp in result.experience:
    print(f"  {exp.company} - {exp.position} ({exp.duration})")
    for h in exp.highlights:
        print(f"    • {h}")
print(f"\n技能: {result.skills}")


# ==============================================================================
# 二、联合类型：支持多种内容格式
# ==============================================================================

print("\n" + "=" * 60)
print("二、联合类型：支持多种内容格式")
print("=" * 60)


class ImageContent(BaseModel):
    """图片内容类型：type 固定为 "image" """
    type: Literal["image"] = "image"
    url: str = Field(description="图片 URL 地址")
    caption: str | None = Field(default=None, description="图片说明（可选）")


class TextContent(BaseModel):
    """纯文本内容类型：type 固定为 "text" """
    type: Literal["text"] = "text"
    content: str = Field(description="文本内容")
    language: str | None = Field(default=None, description="语言代码，如 zh / en")


class MixedContent(BaseModel):
    """
    混合内容模型：联合类型让同一字段能接受多种可能的结构。

    Pydantic v2 的 Union 处理策略：
      - 逐个尝试每个候选类型
      - 第一个验证成功的类型被使用
      - 通常把更具体的类型放前面（更具体的先匹配）
    """
    # AliasChoices：支持多个可能的字段名（兼容性设计）
    # LLM 可能用 author / creator / username 中的任意一个
    author: Annotated[
        str,
        AliasChoices("author", "creator", "username"),
    ]
    # 联合类型：可以是 ImageContent 或 TextContent
    data: Union[ImageContent, TextContent]
    # 额外元数据（允许额外字段）
    model_config = {"extra": "ignore"}


# 模拟两种不同格式的 LLM 输出
image_output = """
{
  "author": "摄影师小明",
  "data": {
    "type": "image",
    "url": "https://example.com/photo.jpg",
    "caption": "日落时分的海边"
  }
}
"""

text_output = """
{
  "creator": "作者张三",
  "data": {
    "type": "text",
    "content": "今天天气真好！",
    "language": "zh"
  }
}
"""

mixed_parser = PydanticOutputParser(pydantic_object=MixedContent)

print("\n[图片内容格式]")
r1 = mixed_parser.parse(image_output)
print(f"作者: {r1.author}, 类型: {r1.data.type}, URL: {r1.data.url}")

print("\n[文本内容格式]")
r2 = mixed_parser.parse(text_output)
print(f"作者: {r2.author}, 类型: {r2.data.type}, 内容: {r2.data.content}")


# ==============================================================================
# 三、嵌套 Parser：在父 Parser 中调用子 Parser
# ==============================================================================

print("\n" + "=" * 60)
print("三、嵌套 Parser：父 Parser 调用子 Parser")
print("=" * 60)


class NewsItem(BaseModel):
    """新闻条目模型"""
    headline: str = Field(description="新闻标题")
    category: Literal["tech", "sports", "finance", "entertainment"] = Field(
        description="新闻分类"
    )
    sentiment: Literal["positive", "neutral", "negative"] = Field(
        description="情感倾向"
    )


class NewsReport(BaseModel):
    """新闻报告模型：包含多个新闻条目"""
    report_date: str = Field(description="报告日期 YYYY-MM-DD")
    total_count: int = Field(ge=0, description="新闻总数")
    items: List[NewsItem] = Field(
        min_length=1, max_length=20,
        description="新闻条目列表"
    )


class WeatherInfo(BaseModel):
    """天气信息模型（独立模型）"""
    city: str
    temperature: float = Field(description="温度，单位摄氏度")
    condition: str = Field(description="天气状况，如 晴 / 多云 / 雨")


class MultiSectionParser:
    """
    多区块 Parser：同时解析新闻报告和天气信息两个独立区块。

    与组合 Parser（03 文件中的 CombinedYamlJsonParser）不同：
      - 组合 Parser：解析同一段文本的不同部分（YAML前言 + JSON正文）
      - 嵌套 Parser：解析多个独立区块，各自对应不同模型
    """

    def __init__(self):
        self.news_parser = PydanticOutputParser(pydantic_object=NewsReport)
        self.weather_parser = PydanticOutputParser(pydantic_object=WeatherInfo)

    def parse(self, text: str) -> dict:
        """
        分区块解析：
          1. 找到所有 JSON 代码块
          2. 第一个块用 news_parser 解析
          3. 第二个块用 weather_parser 解析
        """
        import json

        blocks = re.findall(r"```json\s*(.*?)\s*```", text, re.DOTALL)

        result = {}
        if len(blocks) >= 1:
            result["news"] = self.news_parser.parse(blocks[0])
        if len(blocks) >= 2:
            result["weather"] = self.weather_parser.parse(blocks[1])

        return result

    @property
    def format_instructions(self) -> str:
        """生成两段独立的格式指令，分别对应新闻和天气"""
        return (
            "请分别输出新闻报告和天气信息，用 ```json 代码块包裹：\n"
            "=== 新闻报告 ===\n"
            f"{self.news_parser.get_format_instructions()}\n"
            "=== 天气信息 ===\n"
            f"{self.weather_parser.get_format_instructions()}"
        )


# 模拟 LLM 同时输出新闻和天气的结果
fake_multi_section = """
=== 新闻报告 ===
```json
{
  "report_date": "2026-04-10",
  "total_count": 3,
  "items": [
    {"headline": "AI Agent 新突破", "category": "tech", "sentiment": "positive"},
    {"headline": "股市小幅波动", "category": "finance", "sentiment": "neutral"},
    {"headline": "足球联赛精彩对决", "category": "sports", "sentiment": "positive"}
  ]
}
```
=== 天气信息 ===
```json
{"city": "北京", "temperature": 18.5, "condition": "多云"}
```
"""

multi_parser = MultiSectionParser()
parsed = multi_parser.parse(fake_multi_section)

print("\n[新闻报告]")
news = parsed["news"]
print(f"日期: {news.report_date}, 总数: {news.total_count}")
for item in news.items:
    print(f"  [{item.category}] {item.headline} | 情感: {item.sentiment}")

print(f"\n[天气信息]")
w = parsed["weather"]
print(f"{w.city}: {w.temperature}°C, {w.condition}")


# ==============================================================================
# 四、实战：让 Parser 与 Prompt 配合工作
# ==============================================================================

print("\n" + "=" * 60)
print("四、完整 Chain 示例（模拟）")
print("=" * 60)

# 构造 Prompt（包含嵌套 Parser 的格式指令）
prompt = PromptTemplate.from_template(
    template="请分析以下新闻并提供天气信息。\n{format_instructions}",
    partial_variables={"format_instructions": multi_parser.format_instructions},
)

print("\n[Prompt 中的格式指令（摘要）]")
inst = multi_parser.format_instructions
print(inst[:300] + "...")

print("\n✅ 04_复杂Parser实战 演示完毕！")
