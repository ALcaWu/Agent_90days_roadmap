# Day 08 - LangChain架构概览与LLM基础

> 学习日期：2026-04-02
> 学习时长：约2-3小时

---

## 一、LangChain 核心组件

### 1.1 四大核心组件

| 组件 | 说明 | 典型用途 |
|------|------|----------|
| **LLM** | 大语言模型封装 | 文本生成、对话 |
| **Chain** | 组件串联工作流 | 多步骤处理 |
| **Agent** | 自主决策智能体 | 复杂任务执行 |
| **Memory** | 对话历史管理 | 多轮对话 |

### 1.2 组件关系图

```
┌─────────────────────────────────────────────────┐
│                   LangChain                      │
├─────────────────────────────────────────────────┤
│  LLM      │  Chain    │  Agent   │  Memory     │
├───────────┴───────────┴──────────┴─────────────┤
│                     Tools (工具)                 │
└─────────────────────────────────────────────────┘
```

---

## 二、LLM 基础调用

### 2.1 初始化

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-3.5-turbo",    # 模型名称
    temperature=0.7,          # 创造性 (0-2)
    max_tokens=1000,          # 最大输出长度
)
```

### 2.2 调用方式

```python
# 方式1：字符串输入
response = llm.invoke("你好")

# 方式2：消息列表（推荐）
from langchain_core.messages import HumanMessage, SystemMessage

messages = [
    SystemMessage(content="你是助手"),
    HumanMessage(content="你好")
]
response = llm.invoke(messages)
```

### 2.3 关键参数

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| temperature | 创造性程度 | 0.7（平衡） |
| max_tokens | 最大输出长度 | 根据需求 |
| top_p | 核采样 | 1.0（默认） |

---

## 三、环境配置

### 3.1 .env 文件

```env
# OpenAI API Key
OPENAI_API_KEY=sk-xxxxxxxx
```

### 3.2 加载环境变量

```python
from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件
```

### 3.3 安全规范

- ❌ 绝不把真实 API Key 提交到 Git
- ✅ .env 文件已加入 .gitignore
- ✅ 生产环境使用密钥管理服务

---

## 四、LangChain 生态

| 包名 | 说明 |
|------|------|
| langchain-core | 核心抽象 |
| langchain-openai | OpenAI 集成 |
| langchain-anthropic | Claude 集成 |
| langchain-community | 社区组件 |

---

## 五、今日要点总结

| 知识点 | 核心要点 |
|--------|----------|
| LangChain架构 | LLM、Chain、Agent、Memory 四大组件 |
| LLM调用 | invoke() 方法，支持字符串和消息列表 |
| 参数配置 | temperature 控制创造性 |
| 环境安全 | .env + python-dotenv，绝不提交Key |

---

## 六、学习心得

_（学习完成后填写）_

1.
2.
3.