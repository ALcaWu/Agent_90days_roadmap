# -*- coding: utf-8 -*-
"""
================================================================================
Day 13 - 03_自定义Parser进阶
================================================================================
本文件演示自定义 OutputParser 的进阶用法，包括：
  1. 继承 BaseOutputParser 构建自定义 Parser
  2. 组合 Parser：同时解析前言（YAML/纯文本）和正文（JSON）
  3. 容错 JSON Parser：自动修复 LLM 常见格式错误
  4. 流式累积器 StreamingParser：处理流式输出
  5. 分步骤链式解析：清洗 → 预处理 → 主解析

核心理解：
  - BaseOutputParser 是所有自定义 Parser 的基类
  - 必须实现 get_format_instructions() 和 parse() 两个方法
  - get_format_instructions() 决定 LLM 输出格式，parse() 按相同格式解析
================================================================================
"""

import re
import json
from typing import List, Dict, Any, Union
from abc import ABC
from langchain_core.output_parsers import BaseOutputParser
from pydantic import BaseModel, Field


# ==============================================================================
# 一、BaseOutputParser 基类解析
# ==============================================================================
"""
BaseOutputParser 是 LangChain 所有 OutputParser 的抽象基类。
要创建自定义 Parser，需要继承它并实现：

  get_format_instructions() -> str
      返回格式指令字符串，告诉 LLM 应该怎么输出。
      这个方法的返回值通常会被塞进 PromptTemplate 的 {format_instructions} 占位符。

  parse(text: str) -> T
      接收 LLM 的原始输出字符串，返回解析后的 Python 对象。
      这里是最容易出错的地方，需要处理各种边缘情况。

可选重写：
  + invoke(input: Any, **kwargs) -> T
      BaseOutputParser.invoke() 默认实现：
        text = coerce_to_text(input)  # 把输入统一转成字符串
        return self.parse(text)         # 调用 parse() 处理
      所以只需要实现 parse()，invoke() 就能正常工作。
"""

print("=" * 60)
print("一、BaseOutputParser 结构解析")
print("=" * 60)
print("""
class MyParser(BaseOutputParser):
    # 必须实现这两个方法：
    def get_format_instructions(self) -> str:
        '''告诉 LLM：输出格式是什么'''
        return "请用 JSON 格式输出..."

    def parse(self, text: str) -> dict:
        '''解析 LLM 的原始输出'''
        return json.loads(text)

    # 可选：重写 invoke(input, **kwargs) 做预处理
    def invoke(self, input, **kwargs):
        # 默认实现是：coerce_to_text(input) → parse(text)
        return super().invoke(input, **kwargs)
""")


# ==============================================================================
# 二、组合 Parser：同时解析前言（YAML/纯文本）和正文（JSON）
# ==============================================================================

class CombinedResponse(BaseModel):
    """组合解析器的输出模型：包含元数据和主体数据"""
    # 元数据：从前言提取
    label: str = Field(description="标签/分类")
    timestamp: str = Field(description="时间戳，格式 YYYY-MM-DD")
    # 主体数据：从 JSON 提取
    data: Dict[str, Any] = Field(description="JSON 解析出的主体数据")


class CombinedYamlJsonParser(BaseOutputParser):
    """
    组合 Parser：同时支持 YAML 格式前言和 JSON 代码块正文。

    LLM 输出格式：
    ---
    标签: 产品反馈
    时间: 2026-04-10
    ---
    ```json
    {"product": "Agent", "score": 95, "comments": ["很好用", "速度快"]}
    ```

    本 Parser 分别提取这两部分，合成为一个 CombinedResponse 对象。
    """

    @property
    def lc_namespace(self) -> List[str]:
        """返回命名空间，用于 LCEL 中的类型标识"""
        return ["langchain_core", "output_parsers"]

    def get_format_instructions(self) -> str:
        """明确告诉 LLM 要输出两段内容：YAML 前言 + JSON 正文"""
        return """请按以下格式输出：
---
标签: <你的标签>
时间: <时间戳，格式 YYYY-MM-DD>
---
```json
<你的 JSON 数据>
```"""

    def parse(self, text: str) -> CombinedResponse:
        """
        解析逻辑分两步：
          Step 1: 用正则提取 YAML 前言部分，解析 label 和 timestamp
          Step 2: 用正则提取 JSON 代码块，解析主体数据
          Step 3: 合并为 CombinedResponse
        """
        # 提取 YAML 前言（--- 之间的内容）
        yaml_match = re.search(r"---(.*?)---", text, re.DOTALL)
        yaml_content = yaml_match.group(1).strip() if yaml_match else ""

        # 从 YAML 内容中提取标签和时间（简单行解析，不依赖 PyYAML）
        label = ""
        timestamp = ""
        for line in yaml_content.splitlines():
            line = line.strip()
            if line.startswith("标签:"):
                label = line.split(":", 1)[1].strip()
            elif line.startswith("时间:"):
                timestamp = line.split(":", 1)[1].strip()

        # 提取 JSON 代码块内容
        json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        json_str = json_match.group(1).strip() if json_match else "{}"
        data = json.loads(json_str)  # 内部已有 json.loads 保护，外部用 try-except

        return CombinedResponse(label=label, timestamp=timestamp, data=data)


# 演示组合 Parser
combined_parser = CombinedYamlJsonParser()
fake_combined_output = """---
标签: 用户反馈
时间: 2026-04-10
---
```json
{"满意度": 4.8, "功能点": ["解析快", "容错好"], "建议": "继续优化"}
```"""

print("\n" + "=" * 60)
print("二、组合 Parser：YAML 前言 + JSON 正文")
print("=" * 60)
result = combined_parser.parse(fake_combined_output)
print(f"标签: {result.label}")
print(f"时间: {result.timestamp}")
print(f"数据: {result.data}")


# ==============================================================================
# 三、容错 JSON Parser：自动修复 LLM 常见格式错误
# ==============================================================================

class RobustJsonParser(BaseOutputParser):
    """
    容错 JSON Parser：专门解决 LLM 输出 JSON 时的常见格式问题。

    LLM 的 JSON 输出常见错误：
      1. 尾随逗号: {"a": 1, "b": 2, }  ❌
      2. 单引号代替双引号: {'a': 1}     ❌
      3. 键没有引号: {a: 1}            ❌
      4. 注释混在 JSON 中               ❌
      5. 多了逗号在数组末尾             ❌

    本 Parser 在 json.loads() 之前做预处理，修复这些问题。
    """

    def get_format_instructions(self) -> str:
        """仍然要求 LLM 输出 JSON，但告诉它尽量不要犯常见错误"""
        return "请输出标准 JSON 格式，放在 ```json 代码块中。不要加尾随逗号，不要用单引号。"

    def _preprocess(self, text: str) -> str:
        """
        JSON 预处理：修复常见格式错误。
        注意：这些修复可能有副作用（误伤正常内容），所以尽量保守。
        """
        # 提取 json 代码块内容（如果有）
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        json_str = match.group(1) if match else text

        json_str = json_str.strip()

        # 1. 移除行内注释（// 开头的注释，JSON 标准不支持注释）
        json_str = re.sub(r"//.*$", "", json_str, flags=re.MULTILINE)
        # 2. 移除块注释（/* ... */）
        json_str = re.sub(r"/\*.*?\*/", "", json_str, flags=re.DOTALL)

        # 3. 修复尾随逗号（这是 LLM 最常犯的错误）
        # 匹配 { ..., } 或 [ ..., ] 模式
        json_str = re.sub(r",(\s*[}\]])", r"\1", json_str)

        # 4. 修复单引号为双引号（保守：只在明显是字符串的地方替换）
        # 注意：这可能影响包含单引号的字符串内容，所以用负向前瞻更安全
        json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)
        json_str = re.sub(r"'\s*,\s*}","\" ,}", json_str)
        json_str = re.sub(r"'\s*\]\s*", "\"]", json_str)

        # 5. 允许无引号的键（有些 LLM 会输出 {key: value}）
        json_str = re.sub(r"(\w+)(\s*:)", r'"\1"\2', json_str)

        return json_str

    def parse(self, text: str) -> Dict[str, Any]:
        """
        容错解析：
          Step 1: 预处理（修复格式）
          Step 2: json.loads()（标准解析）
          Step 3: 若失败，给出有意义的错误信息
        """
        from langchain_core.exceptions import OutputParserException

        try:
            cleaned = self._preprocess(text)
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            # 抛出 LangChain 标准解析异常，提供上下文帮助调试
            raise OutputParserException(
                f"JSON 解析失败: {e}\n"
                f"已尝试修复格式错误，当前文本: {text[:300]}",
                observation="LLM 输出不符合 JSON 格式，请检查格式指令或尝试更简洁的结构。"
            )


# 演示容错 Parser
robust_parser = RobustJsonParser()

# 模拟 LLM 输出的有错误 JSON
bad_json_samples = [
    # 尾随逗号
    '{"name": "Agent", "version": "2.0",}',
    # 单引号
    "{'rating': 4.8, 'review': '非常棒'}",
    # 无引号键
    '{name: "Agent", score: 95}',
    # 混合错误
    "{'product': 'AI助手', 'tags': ['llm', 'agent'], }",
]

print("\n" + "=" * 60)
print("三、容错 JSON Parser：自动修复 LLM 格式错误")
print("=" * 60)

for i, bad_json in enumerate(bad_json_samples, 1):
    print(f"\n样本 {i}: {bad_json[:60]}")
    try:
        result = robust_parser.parse(bad_json)
        print(f"  ✅ 解析成功: {result}")
    except Exception as e:
        print(f"  ❌ 解析失败: {e}")


# ==============================================================================
# 四、流式累积器：处理流式输出
# ==============================================================================

class StreamingTagParser(BaseOutputParser):
    """
    流式 Parser：用于累积流式输出（一个字一个字接收），在特定条件满足时触发解析。

    典型场景：LLM 流式返回时，逐 token 拼接buffer，
    当收到完整的 JSON 块时触发解析并返回。
    """

    def __init__(self):
        super().__init__()
        self.buffer = ""        # 累积接收到的文本
        self.trigger = "```json"  # 当缓冲区包含此内容时开始解析

    def get_format_instructions(self) -> str:
        return "请输出 JSON，放在 ```json 代码块中。"

    def parse(self, text: str) -> Union[Dict[str, Any], str]:
        """
        接收新增的文本片段，追加到 buffer。
        如果缓冲区包含触发词，则尝试解析；否则返回 buffer。
        """
        self.buffer += text

        # 检查是否包含完整的 JSON 代码块
        match = re.search(r"```json\s*(.*?)\s*```", self.buffer, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                # JSON 不完整，继续累积
                pass

        # 未触发，返回累积内容（字符串类型）
        return self.buffer

    def reset(self):
        """重置缓冲区，用于处理下一轮流"""
        self.buffer = ""


# 模拟流式输入（分片接收）
print("\n" + "=" * 60)
print("四、流式 Parser 模拟")
print("=" * 60)

stream_parser = StreamingTagParser()
stream_chunks = [
    "正在分析",
    "数据，请稍候",
    "...\n",
    "```json\n",
    '{"status":',
    ' "ok", ',
    '"data": [1, 2, 3]',
    "}\n",
    "```",
]

print("流式接收:")
for chunk in stream_chunks:
    print(f"  收到: {repr(chunk)}")
    result = stream_parser.parse(chunk)
    if isinstance(result, dict):
        print(f"  🎯 完整 JSON 已解析: {result}")
        stream_parser.reset()  # 重置，准备下一轮
        break


# ==============================================================================
# 五、分步骤链式解析：清洗 → 预处理 → 主解析
# ==============================================================================

class MarkdownCleanerParser(BaseOutputParser):
    """
    多步骤解析器：将复杂的解析流程拆成多个步骤，职责分离。

    步骤 1（清洗）: 去掉 Markdown 标记（```、--- 等）
    步骤 2（预处理）: 修复常见错误
    步骤 3（主解析）: json.loads()

    与 RobustJsonParser 不同的是：这个 Parser 在 parse() 内部
    串联了多个处理函数，而不是把所有逻辑堆在一个函数里。
    """

    def get_format_instructions(self) -> str:
        return "请输出 JSON，放在 ```json 代码块中。"

    def _clean_markdown(self, text: str) -> str:
        """步骤1：去掉 Markdown 代码块标记"""
        # 去掉 ```json 和结束 ```
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"\s*```", "", text)
        # 去掉独立的前言标记
        text = re.sub(r"^---\s*$", "", text, flags=re.MULTILINE)
        return text.strip()

    def _fix_common_errors(self, text: str) -> str:
        """步骤2：修复 JSON 常见错误"""
        text = re.sub(r",(\s*[}\]])", r"\1", text)  # 尾随逗号
        text = re.sub(r"'([^']*)'", r'"\1"', text)   # 单引号
        text = re.sub(r"(\w+):", r'"\1":', text)    # 无引号键
        return text

    def parse(self, text: str) -> Dict[str, Any]:
        """步骤3：主解析"""
        from langchain_core.exceptions import OutputParserException

        # 串联三步骤
        cleaned = self._clean_markdown(text)
        fixed = self._fix_common_errors(cleaned)

        try:
            return json.loads(fixed)
        except json.JSONDecodeError as e:
            raise OutputParserException(
                f"JSON 解析失败: {e}\n修复后文本: {fixed[:200]}"
            )


print("\n" + "=" * 60)
print("五、多步骤链式解析")
print("=" * 60)

multistep_parser = MarkdownCleanerParser()
messy_input = """以下是分析结果：
---
```json
{'score': 92, 'summary': '表现优秀', 'tags': ['llm', 'agent',], }
```
"""
result = multistep_parser.parse(messy_input)
print(f"输入（包含 Markdown 标记和格式错误）:")
print(f"  {messy_input[:80]}")
print(f"解析结果: {result}")


print("\n✅ 03_自定义Parser进阶 演示完毕！")
