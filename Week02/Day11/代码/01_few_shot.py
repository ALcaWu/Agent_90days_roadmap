# -*- coding: utf-8 -*-
"""
Day 11 - Few-shot 提示工程
知识点：FewShotPromptTemplate、FewShotChatMessagePromptTemplate、示例选择器
"""

from langchain_core.prompts import (
    FewShotPromptTemplate,
    FewShotChatMessagePromptTemplate,
    ChatPromptTemplate,
    PromptTemplate,
)

# ==================== 1. 基础 Few-shot 示例 ====================

print("=" * 50)
print("1. FewShotPromptTemplate 基础")
print("=" * 50)

# 定义示例
examples = [
    {"input": "快乐", "output": "悲伤"},
    {"input": "高大", "output": "矮小"},
    {"input": "白天", "output": "黑夜"},
]

# 单个示例的格式模板
example_prompt = PromptTemplate.from_template("输入：{input}\n输出：{output}")

# 组装 FewShotPromptTemplate
few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="给出以下单词的反义词：\n",
    suffix="输入：{adjective}\n输出：",
    input_variables=["adjective"],
)

# 生成提示词（注意：invoke 返回 StringPromptValue，用 .text 获取字符串）
prompt_value = few_shot_prompt.invoke({"adjective": "聪明"})
print("生成的提示词：")
print(prompt_value.text)

# ==================== 2. 对话版 Few-shot ====================

print("\n" + "=" * 50)
print("2. FewShotChatMessagePromptTemplate（对话版）")
print("=" * 50)

# 对话格式的示例
chat_examples = [
    {"input": "太阳从哪个方向升起？", "output": "东方"},
    {"input": "水的化学式是什么？", "output": "H₂O"},
    {"input": "地球是圆的还是方的？", "output": "球形（准确说是椭球体）"},
]

# 对话示例模板
chat_example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}"),
    ("ai", "{output}"),
])

# 组装对话版 Few-shot
few_shot_chat = FewShotChatMessagePromptTemplate(
    example_prompt=chat_example_prompt,
    examples=chat_examples,
)

# 嵌入完整的对话 Prompt
final_chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个知识助手，请简洁回答，不要废话。"),
    few_shot_chat,
    ("human", "{input}"),
])

# 生成消息列表
messages = final_chat_prompt.invoke({"input": "光速大约是多少？"})
print("生成的消息列表：")
for msg in messages.messages:
    print(f"  [{msg.type}]: {msg.content[:50]}")

# ==================== 3. Chain-of-Thought Few-shot ====================

print("\n" + "=" * 50)
print("3. Chain-of-Thought（思维链）Few-shot 示例")
print("=" * 50)

cot_examples = [
    {
        "question": "小明有5个苹果，给了小红2个，又买了3个，现在小明有几个苹果？",
        "answer": "思考过程：\n1. 初始：5个\n2. 给出2个：5-2=3个\n3. 买入3个：3+3=6个\n最终答案：6个"
    },
    {
        "question": "一个班有30个学生，其中女生占60%，男生有多少人？",
        "answer": "思考过程：\n1. 女生比例：60%，男生比例：40%\n2. 男生人数：30×40%=12人\n最终答案：12人"
    },
]

cot_example_prompt = PromptTemplate.from_template(
    "问题：{question}\n{answer}"
)

cot_prompt = FewShotPromptTemplate(
    examples=cot_examples,
    example_prompt=cot_example_prompt,
    prefix="请仔细思考并一步步解答以下问题：\n",
    suffix="问题：{question}\n",
    input_variables=["question"],
)

print("思维链提示词（前100字）：")
cot_text = cot_prompt.invoke({"question": "工厂A每天生产100个零件，工厂B每天生产80个，两工厂共需几天生产1080个零件？"}).text
print(cot_text[:200] + "...")


# ==================== 4. 示例选择器（动态选择） ====================

print("\n" + "=" * 50)
print("4. LengthBasedExampleSelector（按长度选择示例）")
print("=" * 50)

from langchain_core.example_selectors import LengthBasedExampleSelector

# 这个选择器根据 Token 总长度动态决定选几个示例
large_examples = [
    {"input": "开心", "output": "难过"},
    {"input": "聪明才智", "output": "愚蠢无知"},
    {"input": "蓬勃发展", "output": "日益衰落"},
    {"input": "积极乐观", "output": "消极悲观"},
    {"input": "英勇无畏", "output": "胆小懦弱"},
]

selector = LengthBasedExampleSelector(
    examples=large_examples,
    example_prompt=example_prompt,
    max_length=25,      # 限制示例总 Token 数
)

dynamic_prompt = FewShotPromptTemplate(
    example_selector=selector,
    example_prompt=example_prompt,
    prefix="给出以下词语的反义词：\n",
    suffix="输入：{adjective}\n输出：",
    input_variables=["adjective"],
)

# 短输入时会选更多示例，长输入时选更少
short_result = dynamic_prompt.invoke({"adjective": "美"})
long_result = dynamic_prompt.invoke({"adjective": "这是一个非常非常长的输入词语用来测试动态选择器"})

print(f"短输入时选择了 {short_result.text.count('输入：') - 1} 个示例")
print(f"长输入时选择了 {long_result.text.count('输入：') - 1} 个示例")

print("\n✅ Few-shot 示例代码运行完成！")
