# -*- coding: utf-8 -*-
"""
Day 09 - ChatModel 基础与消息类型
知识点：ChatModel vs LLM、消息类型、多轮对话
"""

import os
import dotenv

dotenv.load_dotenv()


# ==================== 1. ChatModel vs LLM ====================
"""
ChatModel 和 LLM 的区别：

LLM (Language Model):
  - 输入输出都是纯文本字符串
  - 适用于文本补全、生成任务
  - 示例: LLM.invoke("写一首诗")

ChatModel:
  - 基于 LLM，但专门优化对话场景
  - 输入输出是消息对象列表
  - 支持 System/Human/AI 三种角色
  - 示例: ChatModel.invoke([HumanMessage(content="你好")])

LangChain 中的关系:
  ChatOpenAI 继承自 ChatModel
  ChatModel 内部调用 LLM
"""

print("=" * 50)
print("1. ChatModel vs LLM")
print("=" * 50)

comparison = """
# LLM 调用
llm = OpenAI()
response = llm.invoke("你好，请介绍一下自己")

# ChatModel 调用（推荐用于对话）
chat = ChatOpenAI()
response = chat.invoke([
    SystemMessage(content="你是一个有帮助的助手"),
    HumanMessage(content="你好，请介绍一下自己")
])
"""
print(comparison)


# ==================== 2. 消息类型 ====================

print("\n" + "=" * 50)
print("2. 消息类型详解")
print("=" * 50)

# 检查是否有 langchain
try:
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

    # 创建各种消息
    human_msg = HumanMessage(content="用户消息")
    system_msg = SystemMessage(content="系统提示词")
    ai_msg = AIMessage(content="AI回复")

    print(f"HumanMessage: {human_msg.type} - {human_msg.content}")
    print(f"SystemMessage: {system_msg.type} - {system_msg.content[:20]}...")
    print(f"AIMessage: {ai_msg.type} - {ai_msg.content}")

    MESSAGE_TYPES = """
消息类型说明:
  - HumanMessage: 用户发送的消息
  - SystemMessage: 系统级提示词，设置AI行为
  - AIMessage: AI的回复（可用作历史记录）

消息用途:
  - HumanMessage: 用户输入
  - SystemMessage: 引导AI角色/行为（通常放在最前面）
  - AIMessage: 保存对话历史中的AI回复
"""
    print(MESSAGE_TYPES)

except ImportError as e:
    print(f"提示: 需要安装 langchain-core: {e}")


# ==================== 3. 多轮对话 ====================

print("\n" + "=" * 50)
print("3. 多轮对话实现")
print("=" * 50)


# 检查是否有API Key
api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key: {api_key}")
base_url = os.getenv("OPENAI_API_BASE")
print(f"Base URL: {base_url}")
if api_key:
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

        chat = ChatOpenAI(base_url=base_url, model="gpt-5.1", temperature=0.7)

        # 第一轮对话
        messages = [
            SystemMessage(content="你是一个简洁的助手"),
            HumanMessage(content="推荐一道中国菜"),
        ]
        response1 = chat.invoke(messages)
        print(f"第一轮 - 用户: 推荐一道中国菜")
        print(f"第一轮 - AI: {response1.content[:50]}...")

        # 第二轮对话（带历史）
        messages.append(AIMessage(content=response1.content))
        messages.append(HumanMessage(content="怎么做？"))
        response2 = chat.invoke(messages)
        print(f"\n第二轮 - 用户: 怎么做？")
        print(f"第二轮 - AI: {response2.content[:50]}...")

    except Exception as e:
        print(f"API调用出错: {e}")
else:
    print("多轮对话示例（需要API Key）:")
    print(
        """
# 第一轮
messages = [
    SystemMessage(content="你是一个简洁的助手"),
    HumanMessage(content="推荐一道中国菜")
]
response1 = chat.invoke(messages)

# 第二轮：把AI回复加入历史
messages.append(AIMessage(content=response1.content))
messages.append(HumanMessage(content="怎么做？"))
response2 = chat.invoke(messages)
"""
    )


# ==================== 4. 消息的构建方式 ====================

print("\n" + "=" * 50)
print("4. 消息构建方式")
print("=" * 50)

construction = """
方式1：手动创建消息列表
messages = [
    SystemMessage(content="你是一个助手"),
    HumanMessage(content="你好")
]

方式2：使用 ChatPromptTemplate（Day 10 详细讲）
from langchain.prompts import ChatPromptTemplate
template = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}"),
    ("user", "{question}")
])
messages = template.format_messages(role="助手", question="你好")

方式3：使用 MessagesPlaceholder（更灵活）
from langchain.prompts import MessagesPlaceholder
template = ChatPromptTemplate.from_messages([
    ("system", "你是一个助手"),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{question}")
])
"""
print(construction)


# ==================== 5. 消息属性与方法 ====================

print("\n" + "=" * 50)
print("5. 消息属性与方法")
print("=" * 50)

props = """
消息对象的主要属性:
  - content: str - 消息内容
  - type: str - 消息类型 (human/ai/system)
  - additional_kwargs: dict - 额外参数
  - response_metadata: dict - 响应元数据

消息对象的主要方法:
  - to_dict() - 转换为字典
  - from_dict() - 从字典创建
"""
print(props)

# 演示
try:
    from langchain_core.messages import HumanMessage

    msg = HumanMessage(content="测试消息")
    print(f"\n示例消息:")
    print(f"  content: {msg.content}")
    print(f"  type: {msg.type}")
    print(f"  to_dict(): {msg.to_dict()}")
except:
    pass
