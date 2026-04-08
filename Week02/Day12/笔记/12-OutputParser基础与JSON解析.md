# Day 12：Output Parser基础与JSON解析

**学习日期：** 2026-04-05
**所属周次：** Week 02 - LangChain核心概念
**学习时长：** 2-2.5小时

---

## 📋 今日学习目标

1. 深入理解 LangChain Output Parser 的底层原理与架构
2. 掌握 LangChain 内置的各种 Output Parser 的使用场景
3. 学会创建自定义 Output Parser
4. 掌握 Parser 的错误处理、重试机制与复杂结构解析
5. 理解 Markdown 输出格式解析

---

## 一、Output Parser 核心原理

### 1.1 什么是 Output Parser

Output Parser 是 LangChain 中的关键组件，负责将 LLM 的原始文本输出转换为结构化数据。它的核心价值在于：

```
LLM原始输出（字符串）
        ↓
[Output Parser 解析]
        ↓
结构化数据（dict/Pydantic对象/列表等）
```

### 1.2 Output Parser 在 LCEL 中的位置

```
PromptTemplate → ChatModel → OutputParser → 结构化输出
    ↑              ↑              ↑
   模板           模型           解析器
```

在 LCEL 中，Output Parser 通常作为链的最后一个环节：

```python
chain = prompt | chat_model | output_parser
```

### 1.3 Output Parser 的核心接口

LangChain 的 Output Parser 都继承自 `BaseOutputParser`，核心方法：

| 方法 | 作用 |
|------|------|
| `parse(text)` | 将 LLM 输出解析为结构化数据 |
| `get_format_instructions()` | 返回给 LLM 的格式指令 |
| `invoke(text)` | parse 的封装，支持流式处理 |

---

## 二、内置 Output Parser 详解

### 2.1 StrOutputParser - 字符串输出解析器

最简单的 Parser，直接返回 LLM 输出的字符串：

```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()
result = parser.parse("Hello, World!")
# result = "Hello, World!"
```

**使用场景：**
- 不需要结构化输出的简单对话
- 作为链式处理的中间步骤
- 调试时快速查看 LLM 原始输出

### 2.2 JsonOutputParser - JSON 输出解析器

最常用的 Parser，将 LLM 输出解析为 Python 字典：

```python
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate

# 定义期望的 JSON 结构
prompt = PromptTemplate.from_template(
    """请生成一个关于{subject}的简短介绍，
    并以JSON格式返回，包含以下字段：
    - title: 标题
    - description: 描述（不超过50字）
    
    {format_instructions}
    
    主题：{subject}"""
)

# 设置输出格式
parser = JsonOutputParser()
prompt_with_format = prompt.partial(
    format_instructions=parser.get_format_instructions()
)

chain = prompt_with_format | chat_model | parser
result = chain.invoke({"subject": "人工智能"})
# result = {"title": "...", "description": "..."}
```

**注意事项：**
- JsonOutputParser 只能解析 JSON 对象（dict），不能解析 JSON 数组
- 如果 LLM 输出包含额外的文本（如"以下是JSON："），Parser 会尝试提取 JSON 部分

### 2.3 JsonLinesOutputParser - JSON Lines 解析器

解析多行 JSON，每行是一个独立的 JSON 对象：

```python
from langchain_core.output_parsers import JsonLinesOutputParser

parser = JsonLinesOutputParser()
text = '{"name": "Alice"}\n{"name": "Bob"}\n{"name": "Charlie"}'
result = parser.parse(text)
# result = [{"name": "Alice"}, {"name": "Bob"}, {"name": "Charlie"}]
```

**使用场景：**
- LLM 生成分行 JSON（如每行一个实体）
- 日志解析、多行记录处理

### 2.4 CommaSeparatedListOutputParser - 列表分隔解析器

将 LLM 输出按逗号分隔为列表：

```python
from langchain_core.output_parsers import CommaSeparatedListOutputParser

parser = CommaSeparatedListOutputParser()
result = parser.parse("Apple, Banana, Cherry, Date")
# result = ["Apple", "Banana", "Cherry", "Date"]
```

**使用场景：**
- 提取关键词列表
- 标签生成
- 简单列表提取

### 2.5 DatetimeOutputParser - 日期时间解析器

将 LLM 输出的日期时间字符串解析为 Python datetime 对象：

```python
from langchain_core.output_parsers import DatetimeOutputParser

parser = DatetimeOutputParser()
result = parser.parse("2024-01-15T10:30:00")
# result = datetime.datetime(2024, 1, 15, 10, 30)
```

### 2.6 EnumOutputParser - 枚举解析器

限制输出必须在预定义的枚举值范围内：

```python
from langchain_core.output_parsers import EnumOutputParser
from enum import Enum

class Color(Enum):
    RED = "红色"
    GREEN = "绿色"
    BLUE = "蓝色"

parser = EnumOutputParser(enum=Color)

# LLM 输出 "红色" → Color.RED
# LLM 输出 "绿色" → Color.GREEN
result = parser.parse("红色")
# result = <Color.RED>
```

**使用场景：**
- 分类任务（情感分析：正面/负面/中性）
- 状态机转换
- 强制 LLM 在限定范围内选择

---

## 三、PydanticOutputParser - 生产级解析器

### 3.1 为什么选择 PydanticOutputParser

相比 JsonOutputParser，PydanticOutputParser 提供：
- **类型约束**：运行时类型验证
- **字段验证**：如 `Field(ge=0)` 限制最小值
- **自动补全**：IDE 中有完整的类型提示
- **嵌套结构**：支持复杂的多层嵌套

### 3.2 基本使用

```python
from langchain_core.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List

# 定义 Pydantic 模型
class MovieReview(BaseModel):
    title: str = Field(description="电影标题")
    rating: float = Field(description="评分，范围0-10", ge=0, le=10)
    summary: str = Field(description="简短摘要，不超过100字")
    pros: List[str] = Field(description="优点列表")
    cons: List[str] = Field(description="缺点列表")

# 创建 Parser
parser = PydanticOutputParser(pydantic_object=MovieReview)

# 创建带格式指令的模板
prompt = PromptTemplate.from_template(
    """请为电影《{movie_name}》写一篇简短的影评。
    
    {format_instructions}
    
    电影名称：{movie_name}""",
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

chain = prompt | chat_model | parser

result = chain.invoke({"movie_name": "肖申克的救赎"})
# result 是 MovieReview 对象
print(result.title)      # 有类型提示
print(result.rating)     # 类型是 float
print(result.pros)       # 类型是 List[str]
```

### 3.3 嵌套 Pydantic 模型

```python
from pydantic import BaseModel, Field
from typing import List

class Author(BaseModel):
    name: str = Field(description="作者姓名")
    bio: str = Field(description="作者简介")

class Book(BaseModel):
    title: str = Field(description="书名")
    author: Author = Field(description="作者信息")
    publish_year: int = Field(description="出版年份", ge=1900, le=2030)
    genres: List[str] = Field(description="类型标签")
    rating: float = Field(description="评分", ge=0, le=10)

class BookCollection(BaseModel):
    total_books: int = Field(description="书籍总数", ge=0)
    books: List[Book] = Field(description="书籍列表")
```

### 3.4 带可选字段的解析

```python
from pydantic import BaseModel, Field
from typing import Optional

class Product(BaseModel):
    name: str = Field(description="产品名称")
    price: Optional[float] = Field(description="价格，如果未知则不填", default=None)
    description: Optional[str] = Field(description="产品描述", default=None)
```

---

## 四、自定义 Output Parser

### 4.1 为什么需要自定义 Parser

内置 Parser 无法满足的场景：
- 需要特殊格式解析（如 XML、TOML）
- 需要复杂的验证逻辑
- 需要后处理转换

### 4.2 实现自定义 Parser

```python
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.outputs import Generation
from typing import Any

class CustomParser(BaseOutputParser):
    """自定义 Parser 示例：提取并验证数字列表"""
    
    @property
    def lc_namespace(self) -> list[str]:
        """定义命名空间，用于序列化"""
        return ["my_parsers"]
    
    def parse(self, text: str) -> Any:
        """解析逻辑"""
        # 提取所有数字
        import re
        numbers = re.findall(r'-?\d+\.?\d*', text)
        
        # 转换为 float
        result = []
        for num in numbers:
            try:
                result.append(float(num))
            except ValueError:
                continue
        
        if not result:
            raise ValueError(f"未找到有效数字，输入: {text}")
        
        return result
    
    def get_format_instructions(self) -> str:
        """返回给 LLM 的格式指令"""
        return (
            "请输出一组数字，用空格分隔。\n"
            "例如：3.14 2.718 1.414"
        )

# 使用自定义 Parser
parser = CustomParser()
result = parser.parse("答案是 42 和 3.14 以及 100")
# result = [42.0, 3.14, 100.0]
```

### 4.3 自定义 XML Parser

```python
from langchain_core.output_parsers import BaseOutputParser
from typing import Any
import xml.etree.ElementTree as ET

class XMLParser(BaseOutputParser):
    """解析 XML 格式输出"""
    
    def parse(self, text: str) -> dict:
        # 尝试提取 XML 内容
        import re
        match = re.search(r'<root>(.*?)</root>', text, re.DOTALL)
        if match:
            xml_content = match.group(1)
        else:
            xml_content = text
        
        try:
            root = ET.fromstring(f"<root>{xml_content}</root>")
            return self._element_to_dict(root)
        except ET.ParseError as e:
            raise ValueError(f"XML 解析失败: {e}")
    
    def _element_to_dict(self, element) -> dict:
        result = {}
        for child in element:
            if len(child) == 0:  # 叶子节点
                result[child.tag] = child.text
            else:  # 有子节点
                result[child.tag] = self._element_to_dict(child)
        return result
    
    def get_format_instructions(self) -> str:
        return (
            "请用 XML 格式输出，包含 <root> 标签。\n"
            "例如：\n"
            "<root>\n"
            "  <name>张三</name>\n"
            "  <age>25</age>\n"
            "</root>"
        )

parser = XMLParser()
result = parser.parse("""
以下是信息：
<root>
  <name>张三</name>
  <age>25</age>
</root>
""")
# result = {"name": "张三", "age": "25"}
```

---

## 五、Parser 错误处理与重试

### 5.1 RetryOutputParser - 带重试的解析器

当 LLM 输出格式不正确时，自动重试：

```python
from langchain_core.output_parsers import RetryOutputParser, OutputParserException
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# 基础 Parser
base_parser = JsonOutputParser()

# 包装为带重试的 Parser
parser = RetryOutputParser(
    parser=base_parser,
    max_retries=3,  # 最多重试3次
    retry_on_parse_error=True  # 只在解析错误时重试
)

# 创建修正 Prompt
retry_prompt = PromptTemplate.from_template(
    """您上次生成的输出格式不正确。
    
    原始输出：
    {completion}
    
    解析错误：
    {error}
    
    请重新生成，确保输出格式正确：
    {format_instructions}"""
)

# 完整链
chain = prompt | chat_model | parser

try:
    result = chain.invoke({"topic": "Python"})
except OutputParserException as e:
    print(f"重试后仍然失败: {e}")
```

### 5.2 在 LCEL 中使用重试机制

```python
from langchain_core.output_parsers import JsonOutputParser, RetryOutputParser
from langchain_core.runnables import RunnableLambda

# 带重试的 JSON Parser
json_parser = JsonOutputParser()
retry_parser = RetryOutputParser(
    parser=json_parser,
    max_retries=3,
    retry_on_parse_error=True
)

# 自定义重试提示
def get_retry_prompt(error):
    return f"""您的输出无法被解析为有效 JSON。
    
错误：{error}

请重新输出一个有效的 JSON，不要包含任何其他文字。"""

chain = (
    prompt
    | chat_model
    | RunnableLambda(lambda x: retry_parser.parse_with_retry(x, retry_prompt=get_retry_prompt))
)
```

---

## 六、Markdown 输出解析

### 6.1 Markdown 列表解析器

```python
from langchain_core.output_parsers import BaseOutputParser
from typing import List
import re

class MarkdownListParser(BaseOutputParser[List[str]]):
    """解析 Markdown 格式的列表"""
    
    def parse(self, text: str) -> List[str]:
        # 匹配 Markdown 列表项 (- 或 * 或数字.)
        pattern = r'^\s*[-*+]|\d+\.\s+'
        lines = text.strip().split('\n')
        
        result = []
        for line in lines:
            # 去除列表标记
            cleaned = re.sub(pattern, '', line).strip()
            if cleaned:
                result.append(cleaned)
        
        return result
    
    def get_format_instructions(self) -> str:
        return (
            "请用 Markdown 列表格式输出，每行以 '-' 开头。\n"
            "例如：\n"
            "- 项目一\n"
            "- 项目二\n"
            "- 项目三"
        )

parser = MarkdownListParser()
result = parser.parse("""
以下是主要特点：
- 第一个特点
- 第二个特点
- 第三个特点
""")
# result = ["第一个特点", "第二个特点", "第三个特点"]
```

### 6.2 Markdown 表格解析器

```python
from langchain_core.output_parsers import BaseOutputParser
from typing import List, Dict
import re

class MarkdownTableParser(BaseOutputParser[List[Dict[str, str]]]):
    """解析 Markdown 表格"""
    
    def parse(self, text: str) -> List[Dict[str, str]]:
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        
        # 找到表头和分隔符行
        header_line = None
        separator_line = None
        data_start = 0
        
        for i, line in enumerate(lines):
            if '|' in line and not re.match(r'^\s*\|[\s:|]+\|$', line):
                if header_line is None:
                    header_line = line
                    data_start = i + 2  # 跳过表头和分隔符
                    break
        
        if not header_line:
            raise ValueError("未找到有效的 Markdown 表格")
        
        # 解析表头
        headers = [h.strip() for h in header_line.split('|') if h.strip()]
        
        # 解析数据行
        result = []
        for line in lines[data_start:]:
            if '|' in line and not re.match(r'^\s*\|[\s:|]+\|$', line):
                cells = [c.strip() for c in line.split('|') if c.strip()]
                if len(cells) == len(headers):
                    result.append(dict(zip(headers, cells)))
        
        return result
    
    def get_format_instructions(self) -> str:
        return (
            "请用 Markdown 表格格式输出。\n"
            "例如：\n"
            "| 姓名 | 年龄 | 城市 |\n"
            "|------|------|------|\n"
            "| 张三 | 25   | 北京 |\n"
            "| 李四 | 30   | 上海 |"
        )

parser = MarkdownTableParser()
result = parser.parse("""
| 姓名 | 年龄 | 城市 |
|------|------|------|
| 张三 | 25   | 北京 |
| 李四 | 30   | 上海 |
""")
# result = [
#     {"姓名": "张三", "年龄": "25", "城市": "北京"},
#     {"姓名": "李四", "年龄": "30", "城市": "上海"}
# ]
```

---

## 七、综合实战：结构化信息提取

### 7.1 简历信息提取

```python
from langchain_core.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List, Optional

class WorkExperience(BaseModel):
    company: str = Field(description="公司名称")
    position: str = Field(description="职位")
    duration: str = Field(description="工作时间")
    description: Optional[str] = Field(description="工作描述", default=None)

class Education(BaseModel):
    school: str = Field(description="学校名称")
    degree: str = Field(description="学位")
    major: str = Field(description="专业")
    graduation_year: int = Field(description="毕业年份")

class Resume(BaseModel):
    name: str = Field(description="姓名")
    email: str = Field(description="邮箱")
    phone: str = Field(description="电话")
    skills: List[str] = Field(description="技能列表")
    education: List[Education] = Field(description="教育经历")
    experience: List[WorkExperience] = Field(description="工作经验")

# 创建 Parser
parser = PydanticOutputParser(pydantic_object=Resume)

# 创建 Prompt
prompt = PromptTemplate.from_template(
    """请从以下简历文本中提取信息，并以 JSON 格式返回。
    
    {format_instructions}
    
    简历内容：
    {resume_text}""",
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# 测试
resume_text = """
张三
邮箱：zhangsan@example.com
电话：138-0013-8000

技能：Python, JavaScript, Docker, PostgreSQL

教育经历：
- 清华大学，计算机科学，2018-2022

工作经验：
- 字节跳动，后端工程师，2022-至今
  负责推荐系统后端开发
"""

chain = prompt | chat_model | parser
result = chain.invoke({"resume_text": resume_text})
print(result.name)           # 张三
print(result.skills)        # ['Python', 'JavaScript', 'Docker', 'PostgreSQL']
print(result.education[0].school)  # 清华大学
```

### 7.2 客服对话意图识别

```python
from langchain_core.output_parsers import PydanticOutputParser, EnumOutputParser
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from enum import Enum

class Intent(Enum):
    GREETING = "问候"
    PRODUCT_INQUIRY = "产品咨询"
    ORDER_STATUS = "订单查询"
    COMPLAINT = "投诉"
    REFUND = "退款申请"
    GOODBYE = "道别"
    OTHER = "其他"

class Sentiment(Enum):
    POSITIVE = "正面"
    NEGATIVE = "负面"
    NEUTRAL = "中性"

class ConversationIntent(BaseModel):
    intent: Intent = Field(description="用户意图分类")
    sentiment: Sentiment = Field(description="情感分析")
    confidence: float = Field(description="置信度", ge=0, le=1)
    key_entities: list[str] = Field(description="关键实体", default_factory=list)
    response_suggestion: str = Field(description="建议的回复策略")

parser = PydanticOutputParser(pydantic_object=ConversationIntent)

prompt = PromptTemplate.from_template(
    """分析以下客服对话，提取用户意图和情感。
    
    {format_instructions}
    
    用户消息：{message}""",
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

chain = prompt | chat_model | parser

result = chain.invoke({
    "message": "我上周买的手机还没收到，你们是怎么搞的？！"
})
print(result.intent)        # Intent.COMPLAINT
print(result.sentiment)     # Sentiment.NEGATIVE
print(result.confidence)    # 0.95
print(result.key_entities)  # ["手机", "上周"]
```

---

## 八、知识总结

### 8.1 Output Parser 家族图谱

```
BaseOutputParser
├── StrOutputParser          # 字符串输出
├── JsonOutputParser         # JSON 对象解析
├── JsonLinesOutputParser    # JSON Lines 解析
├── JsonArrayOutputParser    # JSON 数组解析
├── CommaSeparatedListOutputParser  # 逗号分隔列表
├── DatetimeOutputParser     # 日期时间解析
├── EnumOutputParser         # 枚举值解析
├── RetryOutputParser        # 带重试的解析器
└── PydanticOutputParser     # Pydantic 模型解析（生产级）
```

### 8.2 选型决策树

```
需要解析 LLM 输出？
    │
    ├── 只需要原文本 → StrOutputParser
    │
    ├── 需要结构化数据？
    │   ├── 简单 dict → JsonOutputParser
    │   ├── 复杂验证 → PydanticOutputParser
    │   ├── 固定枚举 → EnumOutputParser
    │   └── 逗号列表 → CommaSeparatedListOutputParser
    │
    ├── 解析可能失败？ → RetryOutputParser 包装
    │
    └── 特殊格式 → 自定义 OutputParser
```

### 8.3 最佳实践

1. **生产环境优先使用 PydanticOutputParser**：类型安全、验证完善
2. **始终使用 get_format_instructions()**：确保 LLM 知道期望格式
3. **配合 RetryOutputParser 使用**：处理 LLM 格式错误
4. **复杂场景自定义 Parser**：继承 BaseOutputParser
5. **测试 Parser 的边界情况**：空输入、多余文本、非法字符

---

## 九、课后练习

### 练习 1：JSON 解析器基础
实现一个函数，使用 JsonOutputParser 从 LLM 输出中提取产品信息。

### 练习 2：Pydantic 模型设计
设计一个 Pydantic 模型来解析新闻文章，包含：标题、作者、发布时间、正文、标签列表。

### 练习 3：自定义 Markdown 解析器
创建一个自定义 Parser，解析 LLM 输出的 Markdown 格式的任务列表。

### 练习 4：带重试的错误处理
使用 RetryOutputParser 实现一个健壮的 JSON 解析链。

### 练习 5：综合实战 - 简历解析
完整实现一个简历解析系统，支持提取教育经历、工作经验、技能等。

---

## 十、参考资料

- [LangChain Output Parsers 官方文档](https://python.langchain.com/docs/modules/model_io/output_parsers/)
- [Pydantic 官方文档](https://docs.pydantic.dev/)
- [LCEL Output Parser 集成](https://python.langchain.com/docs/expression_language/how_to/output_parser/)

---

**下一篇预告：** Day 13 - Pydantic与自定义Parser，将深入学习如何设计复杂的 Pydantic 模型，以及如何创建功能强大的自定义 Output Parser。