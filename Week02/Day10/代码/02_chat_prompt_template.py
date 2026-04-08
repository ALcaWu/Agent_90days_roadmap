"""
Day 10 - ChatPromptTemplate 对话模板
学习目标：掌握对话模板的创建、消息类型和消息占位符
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# ============================================
# 1. ChatPromptTemplate 基础
# ============================================

print("=" * 50)
print("1. ChatPromptTemplate 基础")
print("=" * 50)

# 创建对话模板
chat_template = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}，擅长{skill}"),
    ("human", "{question}")
])

# 查看输入变量
print(f"输入变量: {chat_template.input_variables}")

# 生成消息列表
messages = chat_template.invoke({
    "role": "Python专家",
    "skill": "代码优化和性能调优",
    "question": "如何提升Python代码性能？"
})

print(f"\n生成的消息类型: {type(messages)}")
print(f"消息内容:")
for msg in messages.messages:
    print(f"  [{msg.type}]: {msg.content[:50]}...")

# ============================================
# 2. 消息类型详解
# ============================================

print("\n" + "=" * 50)
print("2. 消息类型详解")
print("=" * 50)

# 支持的消息格式
template = ChatPromptTemplate.from_messages([
    ("system", "你是一个有帮助的AI助手"),      # 系统消息
    ("human", "用户问题：{question}"),          # 用户消息
    ("ai", "这是我的回答模板"),                 # AI消息（用于Few-shot）
])

messages = template.invoke({"question": "什么是LangChain？"})
print("消息列表:")
for msg in messages.messages:
    print(f"  类型: {msg.type:8} | 内容: {msg.content[:40]}...")

# ============================================
# 3. MessagesPlaceholder 消息占位符
# ============================================

print("\n" + "=" * 50)
print("3. MessagesPlaceholder 消息占位符")
print("=" * 50)

# 场景：需要动态插入消息列表（如对话历史）
history_template = ChatPromptTemplate.from_messages([
    ("system", "你是一个有帮助的助手，请根据对话历史回答问题"),
    MessagesPlaceholder("history"),  # 动态消息占位符
    ("human", "{input}")
])

# 模拟对话历史
chat_history = [
    HumanMessage(content="我叫吴文杰"),
    AIMessage(content="你好吴文杰！很高兴认识你。"),
    HumanMessage(content="我在学习LangChain"),
    AIMessage(content="太棒了！LangChain是一个强大的LLM开发框架。"),
]

# 使用模板
messages = history_template.invoke({
    "history": chat_history,
    "input": "你还记得我的名字吗？"
})

print(f"消息总数: {len(messages.messages)}")
print("\n完整消息列表:")
for i, msg in enumerate(messages.messages, 1):
    content_preview = msg.content[:30] + "..." if len(msg.content) > 30 else msg.content
    print(f"  {i}. [{msg.type:8}] {content_preview}")

# ============================================
# 4. Few-shot 示例模板
# ============================================

print("\n" + "=" * 50)
print("4. Few-shot 示例模板")
print("=" * 50)

# 在模板中嵌入示例对话
fewshot_template = ChatPromptTemplate.from_messages([
    ("system", "你是一个情感分析助手，判断文本的情感倾向"),
    # 示例1
    ("human", "今天天气真好，心情很愉快！"),
    ("ai", "情感：积极\n置信度：高"),
    # 示例2
    ("human", "这个产品太差了，非常失望。"),
    ("ai", "情感：消极\n置信度：高"),
    # 实际问题
    ("human", "{text}")
])

messages = fewshot_template.invoke({
    "text": "服务一般般，没什么特别的。"
})

print("Few-shot 消息列表:")
for i, msg in enumerate(messages.messages, 1):
    print(f"  {i}. [{msg.type:8}] {msg.content}")

# ============================================
# 5. 模板格式化输出
# ============================================

print("\n" + "=" * 50)
print("5. 模板格式化输出")
print("=" * 50)

# 使用 format 方法获取字符串
template = ChatPromptTemplate.from_messages([
    ("system", "你是{role}"),
    ("human", "{question}")
])

# 方式1：invoke 返回 ChatPromptValue
prompt_value = template.invoke({
    "role": "助手",
    "question": "你好"
})
print(f"invoke 返回类型: {type(prompt_value).__name__}")

# 方式2：format_messages 返回消息列表
messages = template.format_messages(
    role="助手",
    question="你好"
)
print(f"format_messages 返回类型: {type(messages)}")

# 方式3：format 返回字符串
text = template.format(
    role="助手",
    question="你好"
)
print(f"format 返回类型: {type(text)}")
print(f"\n格式化字符串:\n{text}")

print("\n✅ ChatPromptTemplate 学习完成")