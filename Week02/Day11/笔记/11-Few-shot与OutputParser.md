# Day 11 - Few-shot 示例与 Output Parser

> 学习日期：2026-04-04
> 学习时长：约2-3小时

---

## 一、Few-shot 提示工程

### 1.1 什么是 Few-shot？

Few-shot Learning 是一种通过**在提示词中提供若干示例**，来引导模型按照期望格式和风格进行回答的技术。

| 类型 | 说明 | 适用场景 |
|------|------|----------|
| Zero-shot | 不提供任何示例，直接提问 | 通用问答、简单任务 |
| One-shot | 提供1个示例 | 格式固定的简单任务 |
| Few-shot | 提供2-5个示例 | 需要引导风格/格式的复杂任务 |

### 1.2 核心价值

1. **格式控制**：让模型严格按照示例格式输出
2. **风格迁移**：让模型模仿特定的语言风格
3. **减少幻觉**：通过示例锚定模型的输出范围
4. **复杂任务分解**：通过示例展示推理步骤（Chain-of-Thought）

---

## 二、LangChain 中的 Few-shot 实现

### 2.1 FewShotPromptTemplate

```python
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

# 1. 定义示例
examples = [
    {"input": "快乐", "output": "悲伤"},
    {"input": "高大", "output": "矮小"},
    {"input": "白天", "output": "黑夜"},
]

# 2. 定义单个示例的格式
example_prompt = PromptTemplate.from_template(
    "输入：{input}\n输出：{output}"
)

# 3. 组装 FewShotPromptTemplate
few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="给出以下单词的反义词：",
    suffix="输入：{adjective}\n输出：",
    input_variables=["adjective"],
)

# 4. 生成提示词
print(few_shot_prompt.invoke({"adjective": "聪明"}))
```

**生成的提示词效果：**
```
给出以下单词的反义词：

输入：快乐
输出：悲伤

输入：高大
输出：矮小

输入：白天
输出：黑夜

输入：聪明
输出：
```

---

### 2.2 FewShotChatMessagePromptTemplate（对话版）

```python
from langchain_core.prompts import (
    FewShotChatMessagePromptTemplate,
    ChatPromptTemplate,
)

# 对话格式的示例
examples = [
    {"input": "2+2等于几？", "output": "4"},
    {"input": "法国的首都是哪里？", "output": "巴黎"},
]

# 单个对话示例模板
example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}"),
    ("ai", "{output}"),
])

# 组装 Few-shot 对话模板
few_shot_chat = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples,
)

# 嵌入完整的对话 Prompt
final_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个知识助手，请简洁回答。"),
    few_shot_chat,
    ("human", "{input}"),
])
```

---

### 2.3 动态示例选择（ExampleSelector）

当示例库很大时，可以根据输入**动态选择最相关**的示例，节省 Token：

```python
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# 大型示例库
examples = [
    {"input": "我很开心", "output": "积极情绪"},
    {"input": "天空是蓝色的", "output": "自然现象"},
    {"input": "苹果是水果", "output": "食物分类"},
    {"input": "我感到难过", "output": "消极情绪"},
    # ... 更多示例
]

# 语义相似度选择器（根据输入找最相关的示例）
selector = SemanticSimilarityExampleSelector.from_examples(
    examples,
    OpenAIEmbeddings(),
    Chroma,
    k=2,  # 选择最相关的2个示例
)

# 使用动态选择器创建 Few-shot 模板
dynamic_prompt = FewShotPromptTemplate(
    example_selector=selector,
    example_prompt=example_prompt,
    prefix="对以下句子进行分类：",
    suffix="输入：{sentence}\n输出：",
    input_variables=["sentence"],
)
```

---

## 三、Output Parser 输出解析

### 3.1 为什么需要 Output Parser？

LLM 输出的是**纯文本字符串**，但业务代码需要**结构化数据**（JSON、列表、Python 对象等）。Output Parser 负责将模型的文本输出解析成我们需要的格式。

```
LLM 输出（字符串）  →  Output Parser  →  结构化数据（dict / list / Pydantic对象）
```

---

### 3.2 StrOutputParser（字符串解析器）

最简单的解析器，直接提取 AIMessage 中的文本内容：

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

model = ChatOpenAI(model="gpt-3.5-turbo")
parser = StrOutputParser()

chain = ChatPromptTemplate.from_template("翻译成英文：{text}") | model | parser

result = chain.invoke({"text": "你好世界"})
print(type(result))   # <class 'str'>
print(result)         # Hello World
```

---

### 3.3 JsonOutputParser（JSON 解析器）

强制模型以 JSON 格式输出并自动解析：

```python
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

parser = JsonOutputParser()

# 在 Prompt 中注入格式指令
prompt = PromptTemplate(
    template="回答用户问题。\n{format_instructions}\n问题：{query}",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

chain = prompt | model | parser

result = chain.invoke({"query": "给我一个用户信息，包含name和age"})
print(type(result))   # <class 'dict'>
print(result)         # {'name': '张三', 'age': 25}
```

---

### 3.4 PydanticOutputParser（类型安全解析器）⭐ 推荐

使用 Pydantic 模型定义输出结构，提供完整的**类型验证**和**自动补全**支持：

```python
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List

# 1. 定义输出结构
class MovieReview(BaseModel):
    title: str = Field(description="电影标题")
    rating: float = Field(description="评分，1-10分", ge=1, le=10)
    pros: List[str] = Field(description="优点列表")
    cons: List[str] = Field(description="缺点列表")
    summary: str = Field(description="一句话总结")

# 2. 创建解析器
parser = PydanticOutputParser(pydantic_object=MovieReview)

# 3. 注入格式指令
prompt = PromptTemplate(
    template="对这部电影进行评价。\n{format_instructions}\n电影：{movie}",
    input_variables=["movie"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# 4. 执行链
chain = prompt | model | parser
review = chain.invoke({"movie": "流浪地球2"})

# 5. 类型安全访问
print(type(review))          # <class 'MovieReview'>
print(review.title)          # 流浪地球2
print(review.rating)         # 8.5
print(review.pros)           # ['特效震撼', '剧情扎实', ...]
```

---

### 3.5 CommaSeparatedListOutputParser（列表解析器）

将模型输出的逗号分隔文本解析为 Python 列表：

```python
from langchain_core.output_parsers import CommaSeparatedListOutputParser

parser = CommaSeparatedListOutputParser()

prompt = PromptTemplate(
    template="列出5个关于{topic}的关键词。\n{format_instructions}",
    input_variables=["topic"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

chain = prompt | model | parser
result = chain.invoke({"topic": "人工智能"})
print(result)   # ['机器学习', '深度学习', '神经网络', '自然语言处理', '计算机视觉']
```

---

## 四、解析器对比与选型

| 解析器 | 输出类型 | 适用场景 | 类型安全 |
|--------|---------|---------|---------|
| `StrOutputParser` | `str` | 纯文本输出 | ❌ |
| `JsonOutputParser` | `dict` | 简单结构化数据 | ⚠️ 部分 |
| `PydanticOutputParser` | `Pydantic对象` | 复杂业务对象 | ✅ 完整 |
| `CommaSeparatedListOutputParser` | `List[str]` | 简单列表 | ⚠️ 部分 |

**选型原则：**
- 开发调试阶段 → `StrOutputParser`（快速验证逻辑）
- 简单 JSON 数据 → `JsonOutputParser`
- 业务对象（有类型约束）→ **`PydanticOutputParser`（强烈推荐）**
- 简单枚举列表 → `CommaSeparatedListOutputParser`

---

## 五、LCEL 进阶：链的组合模式

### 5.1 顺序链（Sequential Chain）

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

model = ChatOpenAI(model="gpt-3.5-turbo")

# 第一步：提取关键词
keyword_chain = (
    ChatPromptTemplate.from_template("提取以下文本的3个核心关键词（逗号分隔）：\n{text}")
    | model
    | StrOutputParser()
)

# 第二步：根据关键词生成摘要
summary_chain = (
    ChatPromptTemplate.from_template("根据关键词「{keywords}」写一段100字的介绍：")
    | model
    | StrOutputParser()
)

# 链式组合：将第一步的输出传入第二步
full_chain = keyword_chain | (lambda keywords: {"keywords": keywords}) | summary_chain

result = full_chain.invoke({"text": "LangChain是一个用于构建LLM应用的框架..."})
```

### 5.2 使用 RunnablePassthrough 传递原始输入

```python
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

# 并行执行：同时获取摘要和关键词
parallel_chain = RunnableParallel(
    summary=summary_chain,
    keywords=keyword_chain,
)

result = parallel_chain.invoke({"text": "..."})
print(result["summary"])   # 摘要文本
print(result["keywords"])  # 关键词列表
```

---

## 六、今日要点总结

| 知识点 | 核心要点 |
|--------|----------|
| Few-shot | 在 Prompt 中提供示例，引导模型输出格式和风格 |
| FewShotPromptTemplate | 单轮 Few-shot 模板，支持静态/动态示例选择 |
| FewShotChatMessagePromptTemplate | 对话版 Few-shot 模板 |
| StrOutputParser | 最简单的解析器，提取文本内容 |
| JsonOutputParser | 将输出解析为 dict |
| PydanticOutputParser | 类型安全的结构化解析器（推荐） |
| LCEL 顺序链 | 将多个链串联，前一步输出作为后一步输入 |

---

## 七、学习心得

_（学习完成后填写）_

1.
2.
3.
