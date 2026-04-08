"""
Day 10 - LCEL 链式调用
学习目标：使用 LCEL 语法将模板、模型、解析器组合成链
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
import dotenv

# ============================================
# 1. LCEL 基础：管道操作符
# ============================================

print("=" * 50)
print("1. LCEL 基础：管道操作符")
print("=" * 50)

# LCEL 使用 | 操作符连接组件
# template | model | parser
dotenv.load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print(f"OpenAI API Key: {api_key}")
# 定义组件
template = ChatPromptTemplate.from_template("翻译成{language}：{text}")
model = ChatOpenAI(api_key=api_key, model="gpt-5.1", temperature=0.3)
parser = StrOutputParser()

# 组合成链
chain = template | model | parser

print("链组件:")
print(f"  1. PromptTemplate: {template.input_variables}")
print(f"  2. ChatOpenAI: {model.model_name}")
print(f"  3. StrOutputParser: 将AIMessage转为字符串")

# ============================================
# 2. 执行链调用
# ============================================

print("\n" + "=" * 50)
print("2. 执行链调用")
print("=" * 50)

# 同步调用
result = chain.invoke({"language": "英语", "text": "你好，世界"})
print(f"翻译结果: {result}")

# 批量调用
batch_results = chain.batch(
    [
        {"language": "英语", "text": "早上好"},
        {"language": "日语", "text": "谢谢"},
        {"language": "法语", "text": "再见"},
    ]
)
print(f"\n批量翻译结果:")
for i, r in enumerate(batch_results, 1):
    print(f"  {i}. {r}")

# ============================================
# 3. 流式输出
# ============================================

print("\n" + "=" * 50)
print("3. 流式输出")
print("=" * 50)

print("流式翻译: ", end="")
for chunk in chain.stream({"language": "英语", "text": "人工智能正在改变世界"}):
    print(chunk, end="", flush=True)
print("\n")

# ============================================
# 4. 实战：智能问答链
# ============================================

print("=" * 50)
print("4. 实战：智能问答链")
print("=" * 50)

# 设计一个专业的问答模板
qa_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """你是一个{domain}领域的专家。
请用{style}的风格回答问题。
回答要求：
1. 准确专业
2. 结构清晰
3. 适当举例""",
        ),
        ("human", "{question}"),
    ]
)

# 创建问答链
qa_chain = qa_template | model | parser

# 执行问答
answer = qa_chain.invoke(
    {
        "domain": "Python编程",
        "style": "简洁易懂",
        "question": "什么是装饰器？请举例说明",
    }
)

print(f"问答结果:\n{answer}")

# ============================================
# 5. 实战：代码解释链
# ============================================

print("\n" + "=" * 50)
print("5. 实战：代码解释链")
print("=" * 50)

code_explain_template = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个代码解释专家，请用简洁的语言解释代码功能"),
        (
            "human",
            """请解释以下{language}代码的功能：

```{language}
{code}
```

请说明：
1. 代码的主要功能
2. 关键语法点
3. 可能的改进建议""",
        ),
    ]
)

code_chain = code_explain_template | model | parser

# 示例代码
sample_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

explanation = code_chain.invoke({"language": "Python", "code": sample_code})

print(f"代码解释:\n{explanation}")

# ============================================
# 6. 链的复用与配置
# ============================================

print("\n" + "=" * 50)
print("6. 链的复用与配置")
print("=" * 50)

# 创建可配置的链
configurable_template = ChatPromptTemplate.from_messages(
    [("system", "你是一个{role}"), ("human", "{input}")]
)

# 不同配置使用同一链
roles = ["Python专家", "前端工程师", "数据分析师"]

for role in roles:
    chain = configurable_template | model | parser
    result = chain.invoke({"role": role, "input": "请介绍一下你的专业领域"})
    print(f"\n【{role}】的回答:")
    print(f"  {result[:100]}...")

print("\n✅ LCEL 链式调用学习完成")
