# -*- coding: utf-8 -*-
"""
Day 09 - OpenAI ChatModel 调用
知识点：ChatOpenAI 初始化、invoke、参数配置、流式输出
"""

import os


# ==================== 1. ChatOpenAI 初始化 ====================

print("=" * 50)
print("1. ChatOpenAI 初始化")
print("=" * 50)

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    try:
        from langchain_openai import ChatOpenAI

        # 基础初始化
        chat = ChatOpenAI(
            model="gpt-5.1",
            temperature=0.7,
            max_tokens=1000,
        )
        print(f"模型: {chat.model_name}")
        print(f"温度: {chat.temperature}")
        print(f"最大Token: {chat.max_tokens}")

        # 常用参数初始化
        chat_with_options = ChatOpenAI(
            model="gpt-4",  # 也可以用 gpt-4
            temperature=0.5,  # 降低创造性，更准确
            max_tokens=2000,  # 增加到2000
            top_p=0.9,  # 核采样
            frequency_penalty=0.0,  # 频率惩罚
            presence_penalty=0.0,  # 存在惩罚
            stop=None,  # 停止词
            streaming=True,  # 流式输出
        )
        print(f"\n带更多参数的配置也成功")

    except Exception as e:
        print(f"初始化失败: {e}")
else:
    print("未设置 OPENAI_API_KEY，展示配置参数:")
    config_example = """
ChatOpenAI 参数配置:

必选参数:
  - model: 模型名称 (gpt-3.5-turbo / gpt-4)

常用参数:
  - temperature: 0.0-2.0，控制创造性
  - max_tokens: 最大输出token数
  - top_p: 核采样概率
  - streaming: 是否流式输出
  - API相关:
    - api_key: API密钥
    - base_url: API地址（用代理时）
    - organization: 组织ID
"""
    print(config_example)


# ==================== 2. 调用方式 ====================

print("\n" + "=" * 50)
print("2. 调用方式")
print("=" * 50)

call_methods = """
# 方式1：字符串输入（自动转为 HumanMessage）
response = chat.invoke("你好")

# 方式2：消息列表（推荐，用于多轮对话）
from langchain_core.messages import HumanMessage, SystemMessage

messages = [
    SystemMessage(content="你是一个Python专家"),
    HumanMessage(content="什么是装饰器？")
]
response = chat.invoke(messages)

# 方式3：单个消息对象
response = chat.invoke(HumanMessage(content="你好"))

# 方式4：流式调用
for chunk in chat.stream("写一首诗"):
    print(chunk.content, end="", flush=True)
"""
print(call_methods)


# ==================== 3. 完整调用示例 ====================

print("\n" + "=" * 50)
print("3. 完整调用示例")
print("=" * 50)

if api_key:
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage

        chat = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

        # 构建对话
        messages = [
            SystemMessage(content="你是一个专业的编程助手"),
            HumanMessage(content="用Python实现快速排序"),
        ]

        # 调用
        response = chat.invoke(messages)

        print(f"回复内容:\n{response.content[:200]}...")
        print(f"\n元数据:")
        print(f"  模型: {response.response_metadata.get('model_name', 'N/A')}")
        print(f"  类型: {response.type}")

    except Exception as e:
        print(f"调用失败: {e}")
else:
    print("需要API Key才能运行完整示例")


# ==================== 4. 流式输出 ====================

print("\n" + "=" * 50)
print("4. 流式输出")
print("=" * 50)

streaming_info = """
# 流式输出：边生成边显示，适合长文本

chat_streaming = ChatOpenAI(
    model="gpt-3.5-turbo",
    streaming=True,
    temperature=0.7
)

print("流式输出示例:")
for chunk in chat_streaming.stream("写一篇关于AI的文章"):
    print(chunk.content, end="", flush=True)

# 注意：流式调用时响应是 Generator，不是普通消息
"""
print(streaming_info)

print("提示：流式输出在 Day 18 会详细讲解")


# ==================== 5. 错误处理 ====================

print("\n" + "=" * 50)
print("5. 错误处理")
print("=" * 50)

error_handling = """
常见错误与处理:

1. API Key错误
   错误: openai.AuthenticationError
   处理: 检查 .env 中的 OPENAI_API_KEY

2. 限流错误
   错误: openai.RateLimitError
   处理: 添加重试机制，降低请求频率

3. 模型不存在
   错误: openai.NotFoundError
   处理: 检查模型名称是否正确

4. 超时
   错误: openai.TimeoutError
   处理: 增加 timeout 参数

5. 内容安全
   错误: openai.ContentFilterError
   处理: 修改提示词，避免敏感内容
"""
print(error_handling)


# ==================== 6. 常用模型对比 ====================

print("\n" + "=" * 50)
print("6. OpenAI 模型对比")
print("=" * 50)

model_comparison = """
| 模型 | 速度 | 能力 | 成本 | 适用场景 |
|------|------|------|------|----------|
| gpt-3.5-turbo | 快 | 中 | 低 | 日常对话、简单任务 |
| gpt-4 | 慢 | 高 | 高 | 复杂推理、代码生成 |
| gpt-4-turbo | 中 | 高 | 中 | 平衡选择 |
| gpt-3.5-turbo-16k | 快 | 中 | 中 | 长文本处理 |

注意：具体价格以 OpenAI 官方定价为准
"""
print(model_comparison)
