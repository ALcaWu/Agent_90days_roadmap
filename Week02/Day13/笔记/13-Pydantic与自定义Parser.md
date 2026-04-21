# Day 13：Pydantic与自定义Parser

**学习日期：** 2026-04-10
**所属周次：** Week 02 - LangChain核心概念
**学习时长：** 2-2.5小时

---

## 📋 今日学习目标

1. 掌握 Pydantic 高级特性：嵌套模型、验证器、字段约束
2. 设计复杂数据结构的 Pydantic 模型（递归、联合类型）
3. 实现支持多格式的自定义 Parser
4. 处理解析错误、边缘情况与容错机制
5. 理解 Parser 的组合与链式调用

---

## 一、Pydantic 高级特性回顾

### 1.1 Field 高级约束

Pydantic 的 `Field` 不仅仅是定义字段类型，还能添加丰富的验证逻辑：

```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date
from enum import Enum


class Priority(Enum):
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class Task(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    priority: Priority = Field(default=Priority.MEDIUM)
    tags: List[str] = Field(default_factory=list, max_length=10)
    deadline: Optional[date] = None

    @field_validator("tags", mode="before")
    @classmethod
    def split_tags(cls, v):
        # 支持逗号分隔的字符串或列表
        if isinstance(v, str):
            return [t.strip() for t in v.split(",") if t.strip()]
        return v
```

### 1.2 嵌套模型

Pydantic 的核心能力之一：**嵌套模型可以自动递归验证**：

```python
class Address(BaseModel):
    city: str
    street: str
    zip_code: str


class Person(BaseModel):
    name: str
    age: int = Field(ge=0, le=150)
    address: Address  # 嵌套 Address


person = Person(
    name="张三",
    age=30,
    address={"city": "北京", "street": "中关村大街", "zip_code": "100000"}
)
# Pydantic 会自动把 dict 转换成 Address 对象并验证
```

### 1.3 模型序列化与反序列化

Pydantic v2（当前主流版本）提供了强大的序列化控制：

```python
class Product(BaseModel):
    name: str
    price: float = Field(gt=0)
    tags: List[str] = []

    model_config = {
        # 允许额外的字段不报错
        "extra": "ignore",
        # 自定义 JSON 序列化方式
        "json_encoders": {date: lambda v: v.isoformat()},
    }


product = Product.model_validate_json('{"name": "电脑", "price": 5999}')

# 序列化回 JSON
print(product.model_dump_json())  # '{"name":"电脑","price":5999.0,"tags":[]}'
print(product.model_dump())       # {'name': '电脑', 'price': 5999.0, 'tags': []}
```

---

## 二、PydanticOutputParser 深度使用

### 2.1 与 Prompt 的完整配合

`PydanticOutputParser` 的核心价值在于**让 LLM 和 Pydantic 模型保持格式一致**：

```python
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel


class MovieReview(BaseModel):
    title: str
    rating: float = Field(ge=0, le=10, description="评分，0-10分")
    summary: str
    key_points: List[str] = Field(min_length=1, max_length=5)


parser = PydanticOutputParser(pydantic_object=MovieReview)

prompt = PromptTemplate.from_template(
    "请为电影《{movie_name}》写一篇影评。\n{format_instructions}",
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# partial_variables 让模板在运行时自动注入格式指令
chain = prompt | chat_model | parser
result = chain.invoke({"movie_name": "肖申克的救赎"})
# result 是一个 MovieReview 对象，不是 dict！
print(result.title, result.rating)
```

### 2.2 带条件的格式指令

通过 Pydantic 的 `Field` description 可以让 LLM 精确知道每个字段的含义：

```python
class OrderStatus(BaseModel):
    order_id: str = Field(description="订单编号，格式如 ORD-YYYYMMDD-XXXX")
    status: Literal["pending", "paid", "shipped", "delivered", "cancelled"]
    amount: float = Field(gt=0, description="订单金额，单位元")
    items: List[str] = Field(min_length=1, description="商品名称列表")


parser = PydanticOutputParser(pydantic_object=OrderStatus)
print(parser.get_format_instructions())
```

---

## 三、自定义 Parser 进阶

### 3.1 组合多个 Parser

有时候 LLM 的输出可能包含多个部分，需要分别解析：

```python
class ThinkingBlock(BaseModel):
    reasoning: str = Field(description="思考过程")
    conclusion: str = Field(description="最终结论")


class CombinedParser(BaseOutputParser):
    """先解析 YAML 前言，再解析 JSON 正文"""

    def parse(self, text: str) -> dict:
        # 1. 提取 YAML 部分
        yaml_match = re.search(r"---(.*?)---", text, re.DOTALL)
        # 2. 提取 JSON 部分
        json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)

        return {
            "yaml_meta": yaml_match.group(1).strip() if yaml_match else None,
            "json_data": json.loads(json_match.group(1)) if json_match else None,
        }

    def get_format_instructions(self) -> str:
        return """请用以下格式输出：
---
标签: xxx
时间: xxx
---
```json
{"字段": "值"}
```
"""
```

### 3.2 容错 Parser：自动修复常见格式错误

LLM 的输出经常有小瑕疵，比如多了一个尾随逗号、少了引号——健壮的自定义 Parser 应该能处理这些：

```python
class RobustJsonParser(BaseOutputParser):
    """能自动修复 LLM 常见 JSON 错误的 Parser"""

    def parse(self, text: str) -> dict:
        # 1. 提取 JSON 代码块
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        json_str = match.group(1) if match else text

        # 2. 常见修复
        json_str = json_str.strip()
        # 移除尾随逗号
        json_str = re.sub(r",(\s*[}\]])", r"\1", json_str)
        # 修复单引号为双引号（简化处理）
        json_str = re.sub(r"'([^']*)'", r'"\1"', json_str)
        # 允许无引号的键
        json_str = re.sub(r"(\w+):", r'"\1":', json_str)

        return json.loads(json_str)

    def get_format_instructions(self) -> str:
        return """请输出有效的 JSON 格式，放在 ```json 代码块中。"""
```

### 3.3 流式解析器 StreamingParser

对于需要流式输出（一个字一个字返回）的场景：

```python
from langchain_core.output_parsers import StrOutputParser


class StreamingAccumulator(StrOutputParser):
    """累积流式输出，在特定条件满足时触发解析"""

    def __init__(self, trigger_pattern: str = "```json"):
        super().__init__()
        self.trigger_pattern = trigger_pattern
        self.buffer = ""

    def parse(self, text: str) -> str:
        self.buffer += text
        return self.buffer
```

---

## 四、复杂 Parser 实战

### 4.1 多级嵌套结构：解析简历

```python
from pydantic import BaseModel, Field, field_validator
from typing import List
from datetime import datetime


class WorkExperience(BaseModel):
    company: str
    position: str
    duration: str = Field(description="工作时间，格式如 2020.01 - 2023.06")
    highlights: List[str] = Field(min_length=1)


class Education(BaseModel):
    school: str
    degree: str
    year: int = Field(ge=1950, le=2030)

    @field_validator("year", mode="before")
    @classmethod
    def parse_year(cls, v):
        if isinstance(v, str):
            # 支持 "2020年" 这种格式
            return int(re.match(r"(\d{4})", v).group(1))
        return v


class Resume(BaseModel):
    name: str
    email: str
    education: List[Education] = Field(min_length=1)
    experience: List[WorkExperience] = Field(min_length=1)
    skills: List[str]

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if "@" not in v:
            raise ValueError("无效的邮箱格式")
        return v


parser = PydanticOutputParser(pydantic_object=Resume)
```

### 4.2 联合类型与别名字段

```python
from typing import Union, Annotated
from pydantic import AliasChoices


class ImageContent(BaseModel):
    type: Literal["image"] = "image"
    url: str


class TextContent(BaseModel):
    type: Literal["text"] = "text"
    content: str


class MixedContent(BaseModel):
    """支持多种内容类型的联合解析"""
    # 使用 AliasChoices 支持多个可能的字段名
    author: Annotated[
        str,
        AliasChoices("author", "creator", "username"),
    ]
    data: Union[ImageContent, TextContent]

    model_config = {
        # 使用 discriminator 字段区分联合类型
    }
```

---

## 五、错误处理与调试

### 5.1 解析失败的优雅处理

```python
from langchain_core.exceptions import OutputParserException


class SafeParser(BaseOutputParser):
    def parse(self, text: str) -> dict:
        try:
            # 尝试解析
            return json.loads(text)
        except json.JSONDecodeError as e:
            # 提供有意义的错误信息
            raise OutputParserException(
                f"JSON 解析失败: {e}\n原始文本: {text[:200]}",
                observation="LLM 输出格式不符合预期，请检查格式指令",
            )

    def get_format_instructions(self) -> str:
        return """严格输出有效 JSON，不要加任何额外文字。"""
```

### 5.2 使用 with_config 传递解析选项

```python
chain = prompt | chat_model | parser.with_config(
    {"run_name": "main_parser"}
)
```

### 5.3 调试 Parser 的常用技巧

```python
# 1. 先看原始输出
raw_output = chain.invoke({"input": "..."})
print("原始输出:", raw_output)

# 2. 分步调试
prompt_result = prompt.invoke({"input": "..."})
print("Prompt:", prompt_result.to_string())

# 3. 测试 Parser 单独解析
parser = PydanticOutputParser(pydantic_object=MyModel)
test_text = '{"field": "value"}'
result = parser.parse(test_text)
```

---

## 六、综合实战：构建一个可配置的 Parser 工厂

```python
from dataclasses import dataclass
from typing import Type
from langchain_core.output_parsers import BaseOutputParser


@dataclass
class ParserConfig:
    name: str
    model: Type[BaseModel]
    format_template: str


class ParserFactory:
    """Parser 工厂，根据配置自动生成合适的 Parser"""

    _parsers: dict[str, ParserConfig] = {}

    @classmethod
    def register(cls, config: ParserConfig):
        cls._parsers[config.name] = config

    @classmethod
    def get(cls, name: str) -> BaseOutputParser:
        config = cls._parsers.get(name)
        if not config:
            raise ValueError(f"未知的 Parser: {name}")
        return PydanticOutputParser(pydantic_object=config.model)


# 注册 Parser
ParserFactory.register(ParserConfig(
    name="movie_review",
    model=MovieReview,
    format_template="请输出JSON格式的影评...",
))

# 使用
parser = ParserFactory.get("movie_review")
```

---

## 七、避坑指南

### 7.1 常见错误

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| `ValidationError` | Pydantic 字段验证失败 | 检查 LLM 输出是否符合 Field 约束 |
| `json.JSONDecodeError` | LLM 输出不是有效 JSON | 用 RobustJsonParser 预处理 |
| 字段为空或缺失 | LLM 没按格式输出 | 加强 `get_format_instructions()` 说明 |
| 类型不匹配 | LLM 输出字符串，Field 要求数字 | 用 `field_validator(mode="before")` 预处理 |

### 7.2 Field 约束与 LLM 理解的对应关系

| Pydantic 约束 | LLM 格式指令 |
|---------------|-------------|
| `Field(ge=0, le=10)` | "评分在 0 到 10 之间" |
| `Field(min_length=1)` | "至少包含 1 项" |
| `Literal["a", "b"]` | "只能填 a 或 b" |
| `Optional[str]` | "可留空或填写 xxx" |

---

## 八、参考资料

- [Pydantic v2 官方文档](https://docs.pydantic.dev/latest/)
- [LangChain Output Parsers](https://python.langchain.com/docs/modules/model_io/output_parsers/)
- [LangChain PydanticOutputParser](https://python.langchain.com/docs/modules/model_io/output_parsers/types/pydantic_parser)
- [Pydantic Field 高级用法](https://docs.pydantic.dev/latest/concepts/fields/)

---

**上一篇回顾：** Day 12 - Output Parser基础与JSON解析
**下一篇预告：** Day 14 - Chain基础与LLMChain，进入 LangChain 核心组件的学习
