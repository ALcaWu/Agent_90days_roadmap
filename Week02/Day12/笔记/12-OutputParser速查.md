# Day 12 速查卡片：Output Parser 核心要点

## 🎯 一句话总结
> **Output Parser 将 LLM 的原始文本输出转换为结构化数据，是构建可靠 AI 应用的关键组件。**

---

## 📦 内置 Parser 速查

| Parser | 用途 | 返回类型 | 场景 |
|--------|------|----------|------|
| `StrOutputParser` | 字符串透传 | `str` | 简单对话 |
| `JsonOutputParser` | JSON解析 | `dict` | 通用结构化 |
| `JsonLinesOutputParser` | 多行JSON | `List[dict]` | 分行JSON |
| `CommaSeparatedListOutputParser` | 逗号分隔 | `List[str]` | 关键词/标签 |
| `DatetimeOutputParser` | 日期解析 | `datetime` | 时间提取 |
| `EnumOutputParser` | 枚举限制 | `Enum` | 分类任务 |
| `PydanticOutputParser` | Pydantic模型 | `BaseModel` | **生产首选** |

---

## 🔧 PydanticOutputParser 核心语法

```python
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional

class MyModel(BaseModel):
    # 必填字段
    name: str = Field(description="字段描述")

    # 带验证的字段
    age: int = Field(description="年龄", ge=0, le=150)

    # 可选字段
    email: Optional[str] = Field(default=None)

    # 列表字段
    tags: List[str] = Field(default_factory=list)

# 使用
parser = PydanticOutputParser(pydantic_object=MyModel)
result = parser.parse(llm_output)  # 返回 MyModel 对象
```

---

## 🛠️ 自定义 Parser 模板

```python
from langchain_core.output_parsers import BaseOutputParser
from typing import Any

class MyParser(BaseOutputParser):
    """自定义 Parser"""

    def parse(self, text: str) -> Any:
        # 1. 解析逻辑
        result = ...

        # 2. 验证结果
        if not result:
            raise ValueError("解析失败")

        return result

    def get_format_instructions(self) -> str:
        return """给 LLM 的格式指令"""
```

---

## 🔄 RetryOutputParser 用法

```python
from langchain_core.output_parsers import RetryOutputParser, JsonOutputParser

# 包装基础 Parser
retry_parser = RetryOutputParser(
    parser=JsonOutputParser(),
    max_retries=3,  # 最多重试3次
    retry_on_parse_error=True
)

# 自动处理格式错误
result = retry_parser.parse(llm_output)
```

---

## 💡 最佳实践

1. **生产环境用 PydanticOutputParser** - 类型安全、验证完善
2. **始终用 `get_format_instructions()`** - 确保 LLM 知道期望格式
3. **配合 RetryOutputParser** - 处理 LLM 格式错误
4. **在 Prompt 中包含格式指令** - 使用 `partial_variables`

```python
prompt = PromptTemplate.from_template(
    """生成关于 {topic} 的信息。
    {format_instructions}
    主题：{topic}""",
    partial_variables={"format_instructions": parser.get_format_instructions()}
)
```

---

## 🚀 LCEL 链式调用

```python
chain = (
    prompt
    | chat_model
    | parser  # Output Parser 作为链的最后一环
)

result = chain.invoke({"topic": "Python"})
```

---

## ⚠️ 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `OutputParserException` | LLM 输出格式不对 | 用 RetryOutputParser |
| `ValidationError` | 数据不满足 Pydantic 约束 | 检查 Field 约束 |
| `JSONDecodeError` | 不是有效 JSON | 检查 LLM 输出 |

---

**下节预告：** Day 13 - Pydantic与自定义Parser，深入学习复杂 Pydantic 模型设计和自定义 Parser 开发。