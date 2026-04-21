# Day 14：LCEL 管道与 Chain 组合

> **日期：** 2026-04-21
> **主题：** LangChain 纯 LCEL（LangChain Expression Language）开发
> **前置知识：** Day 08~13（LLM 调用、PromptTemplate、OutputParser）
> **重要说明：** 当前环境 langchain 1.2.15 中，`LLMChain` 和 `SequentialChain` 已被移除，
> LangChain 全面转向纯 LCEL 方式。本课程以此为准。

---

## 一、Chain 是什么？

**Chain（链）** 是 LangChain 的执行单元——将多个组件串联成可重复执行的流水线。

```
用户输入 → PromptTemplate → LLM → OutputParser → 结构化结果
              ↑__________________|  ↑
              多步骤协作，统一执行 ← Chain 编排
```

### 为什么要用 Chain？

| 不用 Chain | 用 Chain |
|-----------|---------|
| 每次手动拼接 prompt、调用 LLM、解析结果 | 一行代码完成全流程 |
| prompt 散落在代码各处，难以维护 | prompt 集中在模板中，可复用 |
| 多步骤任务需要手动编排 | Chain 自动管理调用顺序 |

---

## 二、LangChain 版本说明

### 当前环境：langchain 1.2.15

在较新版本的 LangChain 中，`LLMChain` 和 `SequentialChain` 已被移除，全面改用 **LCEL** 方式：

| 旧版（已移除） | 新版（推荐） |
|-------------|-----------|
| `langchain.chains.LLMChain` | 直接用 `prompt \| llm \| parser` |
| `langchain.chains.SequentialChain` | 用 `\|` 顺序管道 + `RunnableLambda` |
| `langchain.chains.BaseChain` | 继承 `Runnable` 接口 |

**结论**：只学 LCEL 即可，这是 LangChain 的现代标准。

---

## 三、Runnable 接口：一切的基础

LangChain 所有组件都实现了 **`Runnable`** 接口，统一了调用方式：

### Runnable 的核心方法

```python
# 同步调用
chain.invoke(input)           # 单次执行
chain.batch([input1, input2])  # 批量执行

# 异步调用
chain.ainvoke(input)          # 单次异步
chain.abatch([...])           # 批量异步

# 流式输出
chain.stream(input)           # 逐 token 打印

# 配置
chain.with_config(config)      # 传参（如 temperature）
```

### 常用 Runnable 组件（全部来自 `langchain_core`）

| 组件 | 导入路径 | 作用 |
|------|---------|------|
| `PromptTemplate` | `langchain_core.prompts` | 构造 prompt |
| `StrOutputParser` | `langchain_core.output_parsers` | 解析为字符串 |
| `RunnableLambda` | `langchain_core.runnables` | 将函数包装成 Runnable |
| `RunnableParallel` | `langchain_core.runnables` | 并行执行多个 Runnable |
| `RunnablePassthrough` | `langchain_core.runnables` | 透传输入 |

---

## 四、LCEL：LangChain Expression Language

**LCEL** 是 LangChain 的声明式管道语法，用 `|` 将 Runnable 连接起来。

### 基础管道

```python
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# 三步组合：Prompt → LLM → Parser
chain = prompt_template | chat_model | output_parser

# 执行
result = chain.invoke({"topic": "Python 异步编程"})
```

### 管道原理（A | B | C）

等价于 `RunnableSequence(first=A, middle=[B], last=C)`，数据从左流向右：

```
输入 {"topic": "..."}
  → PromptTemplate.invoke()  → PromptValue（填充后的提示）
  → ChatModel.invoke()        → AIMessage（AI 回复）
  → StrOutputParser.invoke()  → str（纯文本）
```

### 带变量的管道

```python
chain = (
    PromptTemplate.from_template("介绍一下 {topic}")
    | ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    | StrOutputParser()
)

result = chain.invoke({"topic": "Python 装饰器"})
```

---

## 五、RunnableLambda：把函数变成 Runnable

`RunnableLambda` 将普通 Python 函数包装成 Runnable，使其可以接入 LCEL 管道。

```python
from langchain_core.runnables import RunnableLambda

def count_words(text: str) -> dict:
    return {"word_count": len(text.split()), "text": text}

counter = RunnableLambda(count_words)
result = counter.invoke("Python 异步编程 asyncio")
# {'word_count': 4, 'text': 'Python 异步编程 asyncio'}
```

### 典型用途

| 用途 | 示例 |
|------|------|
| 数据预处理 | `RunnableLambda(preprocess)` |
| 数据后处理 | `chain \| RunnableLambda(postprocess)` |
| 条件逻辑 | `RunnableLambda(branch_func)` |

---

## 六、RunnableParallel：并行执行

```python
from langchain_core.runnables import RunnableParallel, RunnableLambda

parallel = RunnableParallel({
    "word_count": RunnableLambda(lambda t: len(t.split())),
    "first": RunnableLambda(lambda t: t.split()[0]),
})

result = parallel.invoke("Python 异步编程")
# {'word_count': 4, 'first': 'Python'}
```

### 实用场景：同时生成摘要和关键词

```python
summary_chain = summary_prompt | llm | parser
kw_chain = kw_prompt | llm | parser

parallel = RunnableParallel({
    "summary": summary_chain,
    "keywords": kw_chain,
})

result = parallel.invoke({"text": "Python 是一种高级编程语言..."})
# {'summary': '...', 'keywords': '...'}
```

---

## 七、LCEL dict 语法

`dict` 语法是 `RunnableParallel` 的简写，两者等价：

```python
# 完整写法
parallel = RunnableParallel({"a": r1, "b": r2})

# 简写
parallel = {"a": r1, "b": r2}
```

---

## 八、Chain 组合实战：翻译 + 摘要

### 需求

```
输入: {"text": "English article", "lang": "中文"}
  → 翻译链  → {"translated": "中文翻译"}
  → 摘要链  → {"summary": "一句话摘要"}
```

### 关键：数据转换

翻译链返回的是字符串 `str`，但摘要链需要 `{"text": "..."}` 格式的 dict。
需要 `RunnableLambda` 做转换：

```python
def extract_translated(x: str) -> dict:
    """把字符串转成 dict，传给下游"""
    return {"text": x}
```

### 完整实现

```python
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnableLambda

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
parser = StrOutputParser()

# 翻译链
translate_chain = (
    PromptTemplate.from_template("翻译成 {lang}：{text}")
    | llm
    | parser
)

# 摘要链
summarize_chain = (
    PromptTemplate.from_template("用一句话概括：{text}")
    | llm
    | parser
)

# 数据转换
def to_summary_input(translated: str) -> dict:
    return {"text": translated}

# 组合：翻译 → 转换 → 摘要
full_chain = (
    translate_chain
    | RunnableLambda(to_summary_input)
    | summarize_chain
)

result = full_chain.invoke({
    "text": "LangChain is a framework for LLM applications.",
    "lang": "中文"
})
# {'summary': '...'}
```

---

## 九、batch 与 stream 性能优化

### batch 批量执行

```python
# 串行（3次调用 × 2秒 = 6秒）
for q in questions:
    chain.invoke({"question": q})

# 批量（LangChain 内部可能并行优化）
results = chain.batch([{"question": q} for q in questions])
```

### stream 流式输出

```python
# 非流式：等完整结果
result = chain.invoke({"topic": "LangChain"})

# 流式：逐 token 打印
for token in chain.stream({"topic": "LangChain"}):
    print(token, end="", flush=True)
```

---

## 十、学习要点总结

| 概念 | 核心理解 |
|------|---------|
| **Runnable** | 统一接口，`invoke/batch/stream` 三种调用方式 |
| **LCEL `\|`** | `A \| B \| C` = `RunnableSequence(A, B, C)` |
| **RunnableLambda** | 普通函数 → Runnable，`func \| RunnableLambda(post)` 做后处理 |
| **RunnableParallel** | `{key: r1, ...}` 并行执行，key-value 合并结果 |
| **RunnablePassthrough** | 透传输入，保留原始值 |
| **batch & stream** | `batch()` 批量优化，`stream()` 流式输出 |
| **LLMChain/BaseChain** | 已被移除，统一使用 LCEL 方式 |

---

## 练习题预告

Day 14 练习题包含 3 道：

1. **LCEL 管道翻译 Chain**：用 `\|` 组合 Prompt + LLM + Parser
2. **RunnableLambda 统计 Chain**：统计单词数 + 转大写，返回 dict
3. **LCEL Chain 组合**：翻译 + 摘要完整流水线

> 练习题 pass 留空，先自己思考完成，再验证答案。
