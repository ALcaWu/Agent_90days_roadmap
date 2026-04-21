# -*- coding: utf-8 -*-
"""
================================================================================
Day 13 - 02_PydanticParser深度使用
================================================================================
本文件演示 PydanticOutputParser 的完整使用流程，包括：
  1. PydanticOutputParser 构造与核心方法（get_format_instructions / parse）
  2. 与 PromptTemplate 的完整配合（partial_variables 自动注入格式指令）
  3. LCEL 链式调用（prompt | model | parser）
  4. Field description 在格式指令中的作用
  5. 模拟 LLM 调用（无需真实 API Key）

核心理解：
  - get_format_instructions() 负责"告诉 LLM 该怎么输出"
  - parse() 负责"把 LLM 的输出转成 Python 对象"
  - 两者描述的是同一个格式，互为镜像
================================================================================
"""

import json
import re
from typing import List, Literal
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel


# ==============================================================================
# 一、PydanticOutputParser 核心方法解析
# ==============================================================================

class MovieReview(BaseModel):
    """
    影评模型：每个 Field 的 description 会自动出现在 get_format_instructions() 中，
    因此描述要清晰、准确，像在给 LLM 下规格说明书。
    """
    title: str = Field(description="电影的中文完整标题")
    rating: float = Field(ge=0, le=10, description="评分，0-10分的浮点数，10分最高")
    summary: str = Field(max_length=500, description="影评正文摘要，200字以内")
    # min_length=1 确保至少有一个亮点，否则 Pydantic 验证失败
    key_points: List[str] = Field(
        min_length=1, max_length=5,
        description="3到5个影评要点，每项不超过50字"
    )


# 构造 Parser，观察它返回的格式指令
parser = PydanticOutputParser(pydantic_object=MovieReview)

print("=" * 60)
print("一、PydanticOutputParser 核心方法")
print("=" * 60)

# get_format_instructions() 的返回值 —— 这段文字会插入到 Prompt 中
instructions = parser.get_format_instructions()
print("\n[get_format_instructions() 返回值]")
print(instructions)
print()

# 模拟一个 LLM 输出（符合上述格式要求的 JSON）
fake_llm_output = """
{
  "title": "肖申克的救赎",
  "rating": 9.7,
  "summary": "一部关于希望与自由的经典影片，剧情紧凑，人物塑造出色。",
  "key_points": [
    "主题深刻，关于希望与救赎",
    "演员表演精湛",
    "叙事结构巧妙"
  ]
}
"""

# parse() 将字符串解析为 Python 对象（这里是 MovieReview 实例）
parsed = parser.parse(fake_llm_output)
print("[parse() 解析结果]")
print(f"类型: {type(parsed).__name__}")
print(f"标题: {parsed.title}")
print(f"评分: {parsed.rating}")
print(f"要点数: {len(parsed.key_points)}")


# ==============================================================================
# 二、与 PromptTemplate 完整配合
# ==============================================================================
# partial_variables 是 PromptTemplate 的关键特性：
# 模板变量在 .from_template() 时还未知，通过 partial_variables 延迟注入
# 这避免了每次 invoke() 都手动拼接格式指令的麻烦

print("\n" + "=" * 60)
print("二、PromptTemplate + partial_variables 配合")
print("=" * 60)

# 创建模板，使用 {format_instructions} 占位符
# partial_variables 在模板构建时就注入，无需在 invoke() 时传入
prompt = PromptTemplate.from_template(
    template="请为电影《{movie_name}》写一篇影评。\n{format_instructions}",
    partial_variables={
        # 关键：这里注入的不是字符串值，而是 parser.get_format_instructions() 的返回值
        # 模板每次 render 时会自动用最新的返回值替换 {format_instructions}
        "format_instructions": parser.get_format_instructions()
    },
)

# 查看渲染后的完整 Prompt
rendered = prompt.invoke({"movie_name": "阿甘正传"})
print("\n[渲染后的完整 Prompt（最后500字符）]")
print(rendered.to_string()[-500:])


# ==============================================================================
# 三、LCEL 链式调用
# ==============================================================================
# LangChain Expression Language（LCEL）：用 | 将组件串联成链
# chain = prompt | chat_model | parser
#
# 工作流程：
#   input={"movie_name": "..."}
#       ↓
#   prompt.invoke({"movie_name": "..."})  → 生成完整 Prompt
#       ↓
#   chat_model.invoke(PromptValue)         → 调用 LLM（模拟）
#       ↓
#   parser.invoke(str)                     → 解析为 Python 对象

print("\n" + "=" * 60)
print("三、LCEL 链式调用结构")
print("=" * 60)

# 完整的链式表达式
# prompt: PromptTemplate → PromptValue
# chat_model: PromptValue → str
# parser: str → Pydantic 对象

print("""
chain = prompt | chat_model | parser

invoke("肖申克的救赎")
        ↓
prompt.invoke({"movie_name": "肖申克的救赎"})
  → PromptValue（包含完整 Prompt + format_instructions）
        ↓
chat_model.invoke(PromptValue)
  → str（LLM 生成的 JSON 字符串）
        ↓
parser.invoke(str)
  → MovieReview 实例（结构化对象）

result.title          # 直接访问属性
result.rating         # 类型已经是 float 而非字符串
result.key_points[0]  # 直接迭代，无需 json.loads
""")


# ==============================================================================
# 四、Field description 的效果：直接生成给 LLM 的规格说明书
# ==============================================================================

print("\n" + "=" * 60)
print("四、Field description 生成格式指令")
print("=" * 60)


class OrderStatus(BaseModel):
    """订单状态模型：展示 description 如何指导 LLM 输出"""
    order_id: str = Field(
        description="订单编号，格式为 ORD-YYYYMMDD-XXXX（如 ORD-20260410-0001）"
    )
    # Literal 限制 status 只能取指定值，是最强的格式约束
    status: Literal["pending", "paid", "shipped", "delivered", "cancelled"] = Field(
        description="订单状态，只能是 pending/paid/shipped/delivered/cancelled 之一"
    )
    amount: float = Field(gt=0, description="订单金额，单位元，必须大于0")
    items: List[str] = Field(
        min_length=1,
        description="商品名称列表，至少包含一个商品"
    )
    # Optional 字段：LLM 可以留空或不返回该字段
    note: str | None = Field(default=None, description="可选备注")


order_parser = PydanticOutputParser(pydantic_object=OrderStatus)
print("\n[OrderStatus 格式指令]")
print(order_parser.get_format_instructions())

# 模拟 LLM 输出（包含可选字段）
fake_order = """
{
  "order_id": "ORD-20260410-1234",
  "status": "shipped",
  "amount": 299.5,
  "items": ["蓝牙耳机", "手机壳"],
  "note": "已发出，请注意查收"
}
"""
parsed_order = order_parser.parse(fake_order)
print("\n[解析结果]")
print(f"订单号: {parsed_order.order_id}")
print(f"状态: {parsed_order.status}")
print(f"金额: ¥{parsed_order.amount}")
print(f"备注: {parsed_order.note if parsed_order.note else '无'}")


# ==============================================================================
# 五、模拟 LLM 完整调用（无需 API Key）
# ==============================================================================
# 这里用字符串模拟 LLM 输出，真实使用时只需把 chat_model 替换为 ChatOpenAI

print("\n" + "=" * 60)
print("五、模拟完整 Chain 调用")
print("=" * 60)


class MockLLMOutput:
    """
    模拟 LLM 输出：接受 PromptValue，返回符合 MovieReview 格式的 JSON 字符串。
    真实使用时替换为 ChatOpenAI(model="gpt-4o-mini") 即可。
    """

    def invoke(self, prompt_value):
        """模拟 LLM：给定 Prompt，返回符合 Parser 要求的 JSON"""
        # 这里硬编码一个模拟输出，实际应用中 LLM 会根据 Prompt 生成
        return json.dumps({
            "title": "阿甘正传",
            "rating": 9.5,
            "summary": "一个智商低于平均水平的男人，却创造出不平凡的人生奇迹。",
            "key_points": [
                "感人至深的励志故事",
                "演技精湛，特别是汤姆·汉克斯",
                "配乐经典，《随风而逝》传唱至今"
            ]
        }, ensure_ascii=False)

    def __ror__(self, other):
        """支持 LCEL 的 | 管道操作符"""
        # 在 LCEL 中，A | B 等价于 B.invoke(A.invoke(input))
        # 这里模拟 LCEL 的 RunnableRainbow 行为
        return RunnableChain(self, other)


class RunnableChain:
    """简化版 LCEL 链：仅演示调用流程"""

    def __init__(self, prompt_template, llm):
        self.prompt = prompt_template
        self.llm = llm

    def invoke(self, input_dict):
        # Step 1: 渲染 Prompt
        prompt_result = self.prompt.invoke(input_dict)
        # Step 2: 调用 LLM（模拟）
        llm_output = self.llm.invoke(prompt_result)
        # Step 3: 解析（这里手动调用，实际链中用 | parser 自动串联）
        return parser.parse(llm_output)


# 手动模拟链调用
mock_llm = MockLLMOutput()
chain = RunnableChain(prompt, mock_llm)

# 调用链
result = chain.invoke({"movie_name": "阿甘正传"})
print(f"\n[模拟 Chain 调用结果]")
print(f"电影: {result.title}")
print(f"评分: {result.rating}/10")
print(f"摘要: {result.summary}")
print(f"要点: {result.key_points}")


print("\n✅ 02_PydanticParser深度使用 演示完毕！")
print("💡 真实使用时，只需将 MockLLMOutput 替换为真实的 ChatOpenAI 即可。")
