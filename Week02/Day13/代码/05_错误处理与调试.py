# -*- coding: utf-8 -*-
"""
================================================================================
Day 13 - 05_错误处理与调试
================================================================================
本文件演示 Parser 错误处理与调试的完整方法，包括：
  1. OutputParserException：LangChain 标准解析异常
  2. ValidationError：Pydantic 验证失败异常
  3. try-except 捕获与分类处理
  4. Parser 异常情况下的降级策略（返回默认值 / 空对象 / 回退数据）
  5. 调试三步法：看原始输出 → 分步调试 → 单独测试 Parser
  6. with_config 传递运行时配置

核心理解：
  - 解析失败的原因通常有两类：格式错误（Pydantic 验证失败）vs 数据不合法（验证器拒绝）
  - 好的错误处理要给用户/调用方清晰的信息，而不是直接崩溃
================================================================================
"""

import json
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ValidationError
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException


# ==============================================================================
# 一、LangChain 解析异常体系
# ==============================================================================
"""
LangChain 定义了两类主要异常：

OutputParserException（Parser 层异常）
  - 原因：Parser 内部逻辑出错（如 JSONDecodeError、正则不匹配）
  - 抛出方式：raise OutputParserException(msg, observation=tip)
  - 特点：通常由 Parser 自己抛出（主动检测到问题）
  - observation 参数：给调用方的修复建议

ValidationError（Pydantic 层异常）
  - 原因：LLM 输出不符合 Pydantic 模型的字段约束
  - 抛出方式：Pydantic 自动抛出（被动验证失败）
  - 特点：通常包装在 OutputParserException 中抛给上层
"""

print("=" * 60)
print("一、异常类型对比")
print("=" * 60)

sample_pydantic_model = """
| 异常类型 | 来源 | 原因 | 触发场景 |
|---------|------|------|---------|
| OutputParserException | Parser 主动抛出 | Parser 发现无法解析 | JSON 格式损坏、正则匹配失败 |
| ValidationError | Pydantic 自动抛出 | 字段验证器拒绝输入 | rating > 10、required 字段缺失 |
| JSONDecodeError | json.loads() | Python 标准异常 | 不是合法 JSON |
"""
print(sample_pydantic_model)


# ==============================================================================
# 二、Parser 内置异常处理：抛出有意义的错误
# ==============================================================================

class SafeJsonParser:
    """
    安全的 JSON Parser：演示如何在 Parser 内部做异常处理，
    并抛出有意义的错误信息给调用方。
    """

    def parse(self, text: str) -> Dict[str, Any]:
        """
        解析时捕获异常，转换为 LangChain 标准 OutputParserException。
        好处：调用方可以用统一的 except OutputParserException 捕获所有解析问题。
        """
        try:
            # 尝试提取 JSON 代码块内容
            import re
            match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
            json_str = match.group(1).strip() if match else text.strip()

            # 尝试解析
            return json.loads(json_str)

        except json.JSONDecodeError as e:
            # JSONDecodeError → OutputParserException
            # observation 参数是 LangChain 特有的：用于 chain.stream() 时
            # 把错误信息作为 LLM 的观察反馈
            raise OutputParserException(
                f"JSON 格式错误: {e}\n"
                f"请确保输出的是标准 JSON，不要加额外文字。\n"
                f"原始文本（前200字符）: {text[:200]}",
                observation="LLM 输出的 JSON 格式不正确，请检查格式指令或尝试简化结构。"
            )

        except re.error as e:
            # 正则异常（理论上不应该发生，但防御性编程）
            raise OutputParserException(
                f"正则匹配失败: {e}",
                observation="内部错误，请检查 Parser 配置。"
            )


print("\n" + "=" * 60)
print("二、Parser 内置异常处理")
print("=" * 60)

safe_parser = SafeJsonParser()

test_cases = [
    ("正常 JSON", '{"name": "Agent", "score": 95}'),
    ("多余文字", '这是分析结果：{"name": "Agent"}，请查收'),
    ("格式错误", '{"name": "Agent",}'),          # 尾随逗号
    ("非 JSON", '你好，这是我的分析结果'),         # 完全不是 JSON
]

for label, text in test_cases:
    print(f"\n测试: {label}")
    print(f"  输入: {text}")
    try:
        result = safe_parser.parse(text)
        print(f"  ✅ 结果: {result}")
    except OutputParserException as e:
        print(f"  ❌ OutputParserException")
        print(f"     {str(e)[:100]}")


# ==============================================================================
# 三、调用方视角：统一捕获与分类处理
# ==============================================================================

print("\n" + "=" * 60)
print("三、调用方统一捕获与分类处理")
print("=" * 60)


def call_parser_safely(parser, llm_output: str, default: Optional[Dict] = None) -> Dict:
    """
    安全调用 Parser 的封装函数：统一捕获所有可能的异常。

    参数:
      parser: PydanticOutputParser 或类似 Parser
      llm_output: LLM 输出的原始字符串
      default: 解析失败时返回的默认值（可选）

    返回:
      解析成功：Python 对象
      解析失败 + default 不为空：default 值
      解析失败 + default 为空：抛出异常
    """
    try:
        return parser.parse(llm_output)
    except OutputParserException as e:
        # 格式层错误：Parser 无法理解 LLM 输出
        # 策略1：降级返回默认值（静默处理）
        if default is not None:
            print(f"  ⚠️ 格式错误，降级返回: {default}")
            return default
        # 策略2：抛出异常并附带上下文（主动暴露问题）
        raise RuntimeError(f"Parser 解析失败: {e}") from e
    except ValidationError as e:
        # 数据层错误：LLM 输出不符合模型约束
        # 这种情况通常是 LLM 生成的 JSON 结构对，但值不合法
        if default is not None:
            print(f"  ⚠️ 验证失败，降级返回: {default}")
            return default
        raise RuntimeError(f"Pydantic 验证失败: {e}") from e


# 使用示例
sample_model = BaseModel
from pydantic import BaseModel as BM

class ProductInfo(BM):
    name: str
    price: float = Field(gt=0)

test_parser = PydanticOutputParser(pydantic_object=ProductInfo)

bad_outputs = [
    '{"name": "键盘", "price": 199}',      # ✅ 正常
    '错误：输出失败了',                       # ❌ 格式错误
    '{"name": "键盘", "price": -5}',        # ❌ 验证错误（price < 0）
]

print("\n[统一捕获测试]")
for i, output in enumerate(bad_outputs, 1):
    print(f"\n样本{i}: {output[:50]}")
    result = call_parser_safely(test_parser, output, default={"name": "未知", "price": 0})
    print(f"  结果: {result}")


# ==============================================================================
# 四、调试三步法
# ==============================================================================
"""
当 Parser 出现问题时，按以下顺序排查：

Step 1: 看原始输出
  - 在链中插入一个 logging 中间件，打印每次调用的中间结果
  - 或者直接打印 prompt.invoke() → model.invoke() → parser.invoke() 的每一步

Step 2: 分步调试
  - prompt.invoke(dict) → 看 PromptValue 是否正确渲染
  - model.invoke(PromptValue) → 看 LLM 实际返回了什么
  - parser.invoke(str) → 单独测试 Parser 解析 LLM 输出

Step 3: 单独测试 Parser
  - 用一个已知正确的 JSON 测试 Parser 是否正常
  - 用一个故意错误的 JSON 测试 Parser 是否正确报错
"""

print("\n" + "=" * 60)
print("四、调试三步法示例")
print("=" * 60)


def debug_parser_chain(prompt, model, parser, input_dict: dict):
    """
    调试工具：分步打印 Chain 中每个节点的输出。
    只需把 prompt / model / parser 传入，即可在终端看到完整流程。
    """
    print(f"\n[Step 1] Prompt 渲染")
    try:
        prompt_result = prompt.invoke(input_dict)
        print(f"  ✅ PromptValue: {str(prompt_result)[:200]}...")
    except Exception as e:
        print(f"  ❌ Prompt 渲染失败: {e}")
        return

    print(f"\n[Step 2] LLM 调用（模拟）")
    # 模拟 LLM 输出（实际使用时替换为真实 model.invoke()）
    fake_llm_output = '{"name": "调试商品", "price": 88.0}'
    print(f"  模拟 LLM 输出: {fake_llm_output}")

    print(f"\n[Step 3] Parser 解析")
    try:
        result = parser.parse(fake_llm_output)
        print(f"  ✅ 解析成功: {result}")
    except (OutputParserException, ValidationError) as e:
        print(f"  ❌ 解析失败: {e}")
        print(f"\n[诊断建议]")
        print(f"  - 检查 LLM 输出是否符合 Parser 的格式指令")
        print(f"  - 检查 LLM 输出是否满足 Pydantic Field 的所有约束")
        print(f"  - 考虑是否需要在 Parser 中加入容错处理")


# 演示调用
demo_parser = PydanticOutputParser(pydantic_object=ProductInfo)
demo_prompt = prompt = PromptTemplate.from_template(
    template="提取商品信息：{product_name}\n{format_instructions}",
    partial_variables={"format_instructions": demo_parser.get_format_instructions()},
)

debug_parser_chain(demo_prompt, None, demo_parser, {"product_name": "机械键盘"})


# ==============================================================================
# 五、降级策略：解析失败时的保底方案
# ==============================================================================

print("\n" + "=" * 60)
print("五、降级策略：解析失败时的保底方案")
print("=" * 60)


class FallbackParser:
    """
    带降级策略的 Parser：
      1. 尝试正常解析
      2. 失败时尝试容错修复
      3. 还失败则返回降级结果（而不是直接报错）
    """

    def __init__(self, model_class: type[BM]):
        self.parser = PydanticOutputParser(pydantic_object=model_class)
        self.fallback = {"name": "unknown", "price": 0.0, "fallback": True}

    def parse_with_fallback(self, text: str) -> Dict[str, Any]:
        """尝试解析，失败时返回降级结果"""
        try:
            return self.parser.parse(text)
        except (OutputParserException, ValidationError):
            return self.fallback


fallback_parser = FallbackParser(ProductInfo)

print("\n[降级策略测试]")
for output in ['{"name": "正常", "price": 100}', "不是 JSON"]:
    print(f"\n输入: {output}")
    result = fallback_parser.parse_with_fallback(output)
    is_fallback = result.get("fallback", False)
    print(f"  {'⚠️ 降级' if is_fallback else '✅ 正常'}: {result}")


print("\n✅ 05_错误处理与调试 演示完毕！")
