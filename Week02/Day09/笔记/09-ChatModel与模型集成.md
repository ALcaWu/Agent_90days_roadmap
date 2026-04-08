# Day 09 - ChatModel与模型集成

> 学习日期：2026-04-02
> 学习时长：约2-3小时

---

## 一、ChatModel 详解

### 1.1 ChatModel vs LLM

| 特性 | LLM | ChatModel |
|------|-----|-----------|
| 输入 | 纯文本字符串 | 消息对象列表 |
| 输出 | 纯文本 | 消息对象 |
| 适用场景 | 文本补全 | 对话场景 |
| 消息角色 | 无 | System/Human/AI |

### 1.2 消息类型

```python
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# 三种消息类型
human_msg = HumanMessage(content="用户消息")
system_msg = SystemMessage(content="系统提示")
ai_msg = AIMessage(content="AI回复")
```

---

## 二、OpenAI ChatModel

### 2.1 初始化

```python
from langchain_openai import ChatOpenAI

chat = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    max_tokens=1000,
    streaming=False,
)
```

### 2.2 调用方式

```python
# 方式1：字符串（自动转为HumanMessage）
response = chat.invoke("你好")

# 方式2：消息列表（推荐）
messages = [
    SystemMessage(content="你是一个助手"),
    HumanMessage(content="你好")
]
response = chat.invoke(messages)

# 方式3：流式
for chunk in chat.stream("写一首诗"):
    print(chunk.content, end="", flush=True)
```

---

## 三、多模型集成

### 3.1 统一接口

LangChain 的核心优势：无论使用哪个模型，调用方式一致：

```python
# OpenAI
from langchain_openai import ChatOpenAI
chat = ChatOpenAI()

# Anthropic
from langchain_anthropic import ChatAnthropic
chat = ChatAnthropic()

# HuggingFace
from langchain_community.chat_models import ChatHuggingFace
chat = ChatHuggingFace()
```

### 3.2 模型选择策略

| 场景 | 推荐模型 |
|------|---------|
| 日常对话 | gpt-3.5-turbo |
| 复杂推理 | gpt-4 |
| 代码生成 | gpt-4 |
| 成本优先 | gpt-3.5-turbo |

---

## 四、今日要点总结

| 知识点 | 核心要点 |
|--------|----------|
| ChatModel | 专门优化对话的模型封装 |
| 消息类型 | HumanMessage、SystemMessage、AIMessage |
| 多轮对话 | 将AI回复加入历史，继续提问 |
| 模型切换 | 统一接口，不同provider无缝切换 |

---

## 五、学习心得

1. **ChatModel vs LLM 的本质区别**：LLM 接收纯文本字符串，而 ChatModel 接收有角色语义的消息列表（HumanMessage / SystemMessage / AIMessage）。ChatModel 更贴近现代对话 AI 的使用方式，也是实际开发中的首选，`SystemMessage` 让我们可以精准控制模型的行为边界。

2. **LangChain 统一接口的工程价值**：无论是 OpenAI、Anthropic（Claude）还是 HuggingFace，`invoke(messages)` 的调用方式完全一致。这让业务代码与具体模型提供商完全解耦——今天用 gpt-3.5-turbo，明天换 Claude 只需改一行配置，这是 LangChain 最核心的设计思想之一。

3. **模型工厂模式（`create_chat_model`）的意义**：通过工厂函数统一创建入口，实现"配置驱动"的模型选择，可以根据不同环境（开发/生产）或成本要求动态切换模型，避免硬编码。这也让练习题中的 `ConversationManager` 与具体模型完全解耦，是可扩展设计的雏形。

4. **模型选择的成本意识很重要**：gpt-3.5-turbo 与 gpt-4 之间约有 15 倍的成本差距。开发调试阶段使用便宜模型、在生产关键路径上才升级强模型，这不只是省钱，更是产品上线后维持可持续运营的关键工程决策。