# Day 10 - Prompt Template与动态提示

> 学习日期：2026-04-04
> 学习时长：约2-3小时

---

## 一、Prompt Template 概述

### 1.1 什么是 Prompt Template？

Prompt Template（提示模板）是 LangChain 中用于**动态生成提示**的核心组件。它解决了以下问题：

- **复用性**：同一模板可用于不同输入
- **结构化**：规范提示格式，确保一致性
- **可维护**：修改模板无需改动代码逻辑

### 1.2 核心优势

| 特性 | 硬编码字符串 | PromptTemplate |
|------|-------------|----------------|
| 变量替换 | 手动拼接 | 自动格式化 |
| 输入验证 | 无 | 自动检查必填变量 |
| 模板复用 | 困难 | 轻松实现 |
| 部分填充 | 不支持 | 支持 partial() |

---

## 二、PromptTemplate 基础

### 2.1 创建模板

```python
from langchain_core.prompts import PromptTemplate

# 方式1：from_template（推荐）
template = PromptTemplate.from_template("给我讲一个关于{topic}的笑话")
prompt = template.invoke({"topic": "程序员"})
print(prompt)  # 给我讲一个关于程序员的笑话

# 方式2：构造函数
template = PromptTemplate(
    input_variables=["topic"],
    template="给我讲一个关于{topic}的笑话"
)
```

### 2.2 变量替换

```python
# 单变量
template = PromptTemplate.from_template("翻译成{language}：{text}")
prompt = template.invoke({"language": "英语", "text": "你好世界"})

# 多变量
template = PromptTemplate.from_template("""
你是一个{role}，请用{style}风格回答问题：
{question}
""")
prompt = template.invoke({
    "role": "资深工程师",
    "style": "简洁专业",
    "question": "什么是微服务？"
})
```

### 2.3 部分填充（Partial）

```python
# 预填充部分变量，剩余变量后续填充
template = PromptTemplate.from_template(
    "你是{role}，请回答：{question}"
)

# 先填充 role
partial_template = template.partial(role="AI助手")
# 后填充 question
prompt = partial_template.invoke({"question": "什么是LangChain？"})
```

---

## 三、ChatPromptTemplate 对话模板

### 3.1 基础用法

```python
from langchain_core.prompts import ChatPromptTemplate

# 创建对话模板
chat_template = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}，擅长{skill}"),
    ("human", "{question}")
])

# 生成消息列表
messages = chat_template.invoke({
    "role": "Python专家",
    "skill": "代码优化",
    "question": "如何提升代码性能？"
})
```

### 3.2 消息类型

```python
# 支持的消息格式
chat_template = ChatPromptTemplate.from_messages([
    ("system", "系统提示词"),           # SystemMessage
    ("human", "用户问题"),              # HumanMessage
    ("ai", "AI回复"),                   # AIMessage
    ("placeholder", "{history}"),       # 消息占位符
])
```

### 3.3 MessagesPlaceholder 消息占位符

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 用于插入动态消息列表（如对话历史）
template = ChatPromptTemplate.from_messages([
    ("system", "你是一个有帮助的助手"),
    MessagesPlaceholder("history"),  # 占位符
    ("human", "{input}")
])

# 使用时传入消息列表
messages = template.invoke({
    "history": [
        ("human", "你好"),
        ("ai", "你好！有什么可以帮你的？")
    ],
    "input": "今天天气怎么样？"
})
```

---

## 四、模板组合与管道

### 4.1 模板组合

```python
# 组合多个模板
from langchain_core.prompts import PromptTemplate

intro = PromptTemplate.from_template("你是一个{role}。\n")
task = PromptTemplate.from_template("请完成以下任务：{task}\n")
format_rule = PromptTemplate.from_template("输出格式：{format}")

# 拼接
full_template = intro + task + format_rule
```

### 4.2 PipelinePromptTemplate

```python
from langchain_core.prompts import PipelinePromptTemplate

# 分层模板：最终模板 + 子模板
final_template = PromptTemplate.from_template("""
{role_desc}
{task_desc}
""")

role_template = PromptTemplate.from_template("角色：{role}")
task_template = PromptTemplate.from_template("任务：{task}")

pipeline = PipelinePromptTemplate(
    final_prompt=final_template,
    pipeline_prompts=[
        ("role_desc", role_template),
        ("task_desc", task_template)
    ]
)
```

---

## 五、实战：构建智能问答模板

### 5.1 设计原则

1. **角色定义清晰**：明确AI的身份和能力边界
2. **上下文完整**：提供足够的背景信息
3. **输出规范**：指定格式、长度、风格
4. **示例引导**：复杂任务提供Few-shot示例

### 5.2 完整示例

```python
from langchain_core.prompts import ChatPromptTemplate

# 设计一个代码审查助手的模板
code_review_template = ChatPromptTemplate.from_messages([
    ("system", """你是一位资深代码审查专家。
你的职责是：
1. 发现潜在的bug和逻辑错误
2. 检查代码风格和最佳实践
3. 提出改进建议

请用简洁、专业的语言进行审查。"""),
    ("human", """请审查以下{language}代码：

```{language}
{code}
```

请从以下几个方面给出反馈：
{focus_areas}""")
])

# 使用模板
messages = code_review_template.invoke({
    "language": "Python",
    "code": "def add(a, b): return a + b",
    "focus_areas": "1. 类型安全\n2. 边界处理\n3. 可读性"
})
```

---

## 六、与 LLM 链式调用

### 6.1 使用 LCEL 语法

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 定义组件
model = ChatOpenAI(model="gpt-3.5-turbo")
template = ChatPromptTemplate.from_template("翻译成{language}：{text}")
parser = StrOutputParser()

# 链式调用（LCEL）
chain = template | model | parser

# 执行
result = chain.invoke({
    "language": "英语",
    "text": "你好世界"
})
print(result)  # Hello World
```

### 6.2 流式输出

```python
# 流式处理
for chunk in chain.stream({"language": "英语", "text": "今天天气很好"}):
    print(chunk, end="", flush=True)
```

---

## 七、今日要点总结

| 知识点 | 核心要点 |
|--------|----------|
| PromptTemplate | 单轮提示模板，支持变量替换 |
| ChatPromptTemplate | 对话模板，支持多角色消息 |
| MessagesPlaceholder | 动态插入消息列表（对话历史） |
| partial() | 预填充部分变量 |
| LCEL链式调用 | `template \| model \| parser` |

---

## 八、学习心得

1. **PromptTemplate 的核心价值**：将硬编码的字符串拼接升级为"模板+变量"模式，提升了复用性和可维护性。`partial()` 方法可以预填充部分变量，非常适合做"角色固定+任务可变"的场景，比如一个翻译助手的 system 角色固定，只有目标语言动态变化。

2. **ChatPromptTemplate 的多角色设计**：通过 `SystemMessage` 定义 AI 的行为边界，`HumanMessage` 传递用户输入，`MessagesPlaceholder` 动态插入对话历史——这三者组合在一起，是实现多轮对话系统的基石，也是 Week 03 Memory 管理的重要铺垫。

3. **LCEL 管道语法的优雅之处**：`template | model | parser` 一行代码就构成了完整的 AI 调用链，每个组件都是可独立替换的积木，这种声明式写法比命令式的函数调用更清晰、更易测试、更易扩展，深刻体现了"高内聚、低耦合"的工程思想。

4. **`partial_variables` 与解析器契约**：通过 `partial_variables={"format_instructions": parser.get_format_instructions()}` 将格式要求"烧录"进模板，让 Prompt 和 Parser 之间形成隐式契约——模板告诉模型"按这个格式输出"，Parser 负责"按这个格式解析"，是 Day 11 Output Parser 深度学习的关键铺垫。