# -*- coding: utf-8 -*-
"""
Day 08 - OpenAI LLM 基础调用
知识点：LLM初始化、invoke调用、参数配置、响应解析
使用前请确保安装所需依赖：
pip install python-dotenv
"""

import os


# 尝试导入，如果失败则给出提示
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

    CHAT_OPENAI_AVAILABLE = True
except ImportError as e:
    print(f"警告: 无法导入必要的模块: {e}")
    print("请运行: pip install langchain-openai langchain-core")
    CHAT_OPENAI_AVAILABLE = False


# ==================== 1. LLM 初始化 ====================

print("=" * 50)
print("1. LLM 初始化")
print("=" * 50)

# 检查是否有API Key
api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key: {api_key}")
if not api_key:
    # 没有API Key时，使用演示模式
    print("提示: 未设置 OPENAI_API_KEY，展示配置参数")
    print("  - model: gpt-3.5-turbo")
    print("  - temperature: 0.7")
    print("  - max_tokens: 1000")
    llm = None
else:
    # 有API Key时正常初始化
    llm = ChatOpenAI(
        model="gpt-5.1",
        temperature=0.7,
        max_tokens=1000,
    )
    print(f"模型: {llm.model_name}")
    print(f"温度: {llm.temperature}")
    print(f"最大Token: {llm.max_tokens}")


# ==================== 2. 基础调用 ====================

print("\n" + "=" * 50)
print("2. 基础调用方式")
print("=" * 50)

if llm:
    # 方式1：直接传入字符串
    response1 = llm.invoke("什么是LangChain？")
    print(f"方式1 - 字符串输入:")
    print(f"  回复: {response1.content[:50]}...")

    # 方式2：传入消息列表
    messages = [
        SystemMessage(content="你是一个简洁的助手"),
        HumanMessage(content="Python和JavaScript哪个好？"),
    ]
    response2 = llm.invoke(messages)
    print(f"\n方式2 - 消息列表输入:")
    print(f"  回复: {response2.content[:50]}...")
else:
    # 演示模式
    print("方式1 - 字符串输入:")
    print("  llm.invoke('什么是LangChain？')")
    print("方式2 - 消息列表输入:")
    print("  messages = [SystemMessage(content='...'), HumanMessage(content='...')]")
    print("  llm.invoke(messages)")


# ==================== 3. 模型参数详解 ====================

print("\n" + "=" * 50)
print("3. 关键参数详解")
print("=" * 50)

params_info = """
temperature (温度):
  - 0.0: 最确定性，每次输出相同
  - 0.7: 平衡，创造性与确定性
  - 2.0: 最具创造性，输出多样

max_tokens (最大token):
  - 控制输出长度
  - 根据需求设置，过长浪费成本

top_p (核采样):
  - 0.9: 保留90%概率的token
  - 通常与temperature二选一使用
"""
print(params_info)


# ==================== 4. 不同temperature对比 ====================

print("\n" + "=" * 50)
print("4. temperature 对比演示")
print("=" * 50)

if llm:
    # 温度0（确定性）
    llm_0 = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
    # 温度2（创造性）
    llm_2 = ChatOpenAI(model="gpt-3.5-turbo", temperature=2.0)

    prompt = "给我一个冰淇淋的口味建议"
    resp_0 = llm_0.invoke(prompt)
    resp_2 = llm_2.invoke(prompt)
    print(f"temperature=0.0: {resp_0.content[:60]}...")
    print(f"temperature=2.0: {resp_2.content[:60]}...")
else:
    print("temperature=0.0: [需要API Key] 确定性输出，更保守一致")
    print("temperature=2.0: [需要API Key] 创造性输出，更随机多样")


# ==================== 5. 响应对象结构 ====================

print("\n" + "=" * 50)
print("5. 响应对象结构")
print("=" * 50)

print("响应对象包含:")
print("  - content: str, 回复的文本内容")
print("  - type: str, 角色类型 (ai/human/system)")
print("  - additional_kwargs: dict, 额外参数")
print("  - response_metadata: dict, 响应元数据（包含token使用量）")


# ==================== 6. 流式输出 (可选) ====================

print("\n" + "=" * 50)
print("6. 流式输出")
print("=" * 50)

stream_info = """
# 流式输出用于长文本，边输出边显示
llm = ChatOpenAI(model="gpt-3.5-turbo", streaming=True)

for chunk in llm.stream("写一首关于春天的诗"):
    print(chunk.content, end="", flush=True)
"""
print(stream_info)
print("（流式输出在 Day 18 详细介绍）")
