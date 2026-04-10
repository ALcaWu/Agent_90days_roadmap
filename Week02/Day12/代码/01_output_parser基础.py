"""
Day 12 - 代码示例 1：Output Parser 基础
学习 LangChain 内置的各种 Output Parser 的基本用法
"""

from langchain_core.output_parsers import (
    StrOutputParser,
    JsonOutputParser,
    CommaSeparatedListOutputParser,
    PydanticOutputParser,
)
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

# =============================================
# 1. StrOutputParser - 字符串输出解析器
# =============================================
print("=" * 50)
print("1. StrOutputParser 示例")
print("=" * 50)

str_parser = StrOutputParser()
result = str_parser.parse("Hello, LangChain!")
print(f"输入: 'Hello, LangChain!'")
print(f"输出: {result}")
print(f"类型: {type(result)}")
print()

# =============================================
# 2. JsonOutputParser - JSON 输出解析器
# =============================================
print("=" * 50)
print("2. JsonOutputParser 示例")
print("=" * 50)

json_parser = JsonOutputParser()

# 模拟 LLM 输出的 JSON 字符串
llm_output = '''
{
    "name": "张三",
    "age": 28,
    "city": "北京"
}
'''

result = json_parser.parse(llm_output)
print(f"输入: {llm_output}")
print(f"输出: {result}")
print(f"类型: {type(result)}")
print(f"姓名: {result['name']}, 年龄: {result['age']}")
print()

# =============================================
# 3. CommaSeparatedListOutputParser - 逗号分隔列表解析器
# =============================================
print("=" * 50)
print("3. CommaSeparatedListOutputParser 示例")
print("=" * 50)

comma_list_parser = CommaSeparatedListOutputParser()

result = comma_list_parser.parse("Apple, Banana, Cherry, Date, Elderberry")
print(f"输入: 'Apple, Banana, Cherry, Date, Elderberry'")
print(f"输出: {result}")
print(f"类型: {type(result)}")
print()

# =============================================
# 4. MarkdownListOutputParser - Markdown 列表解析器
# =============================================
print("=" * 50)
print("4. MarkdownListOutputParser 示例")
print("=" * 50)

from langchain_core.output_parsers import MarkdownListOutputParser

markdown_list_parser = MarkdownListOutputParser()

result = markdown_list_parser.parse("- Apple\n- Banana\n- Cherry\n- Date")
print(f"输入: '- Apple\\n- Banana\\n- Cherry\\n- Date'")
print(f"输出: {result}")
print(f"类型: {type(result)}")
print()

# =============================================
# 5. NumberedListOutputParser - 编号列表解析器
# =============================================
print("=" * 50)
print("5. NumberedListOutputParser 示例")
print("=" * 50)

from langchain_core.output_parsers import NumberedListOutputParser

numbered_list_parser = NumberedListOutputParser()

result = numbered_list_parser.parse("1. 第一步\n2. 第二步\n3. 第三步")
print(f"输入: '1. 第一步\\n2. 第二步\\n3. 第三步'")
print(f"输出: {result}")
print(f"类型: {type(result)}")
print()

# =============================================
# 6. XML 解析（手动实现，不依赖 defusedxml）
# =============================================
# 注意：langchain_core 的 XMLOutputParser.parse() 在新版本要求安装 defusedxml。
# 如需使用：pip install defusedxml
# 此处改用标准库 xml.etree.ElementTree 演示相同的解析效果。
print("=" * 50)
print("6. XML 解析示例（标准库实现）")
print("=" * 50)

import xml.etree.ElementTree as ET

def parse_xml_to_dict(text: str) -> dict:
    """从 XML 文本中提取 <root> 内容，返回字典"""
    import re
    match = re.search(r'<root>(.*?)</root>', text, re.DOTALL)
    xml_str = f"<root>{match.group(1)}</root>" if match else text.strip()

    def elem_to_dict(elem):
        result = {}
        for child in elem:
            result[child.tag] = child.text if len(child) == 0 else elem_to_dict(child)
        return result

    root = ET.fromstring(xml_str)
    return elem_to_dict(root)

xml_output = '''<root>
    <name>张三</name>
    <age>28</age>
    <city>北京</city>
</root>'''

result = parse_xml_to_dict(xml_output)
print(f"输入: {xml_output}")
print(f"输出: {result}")
print(f"类型: {type(result)}")
print()

# =============================================
# 7. get_format_instructions() 格式化指令
# =============================================
print("=" * 50)
print("7. get_format_instructions() 格式化指令")
print("=" * 50)

print("JsonOutputParser 格式指令:")
print(json_parser.get_format_instructions())
print()

print("CommaSeparatedListOutputParser 格式指令:")
comma_parser = CommaSeparatedListOutputParser()
print(comma_parser.get_format_instructions())
print()

# =============================================
# 8. 在 LCEL 链中使用 Parser
# =============================================
print("=" * 50)
print("8. 在 LCEL 链中使用 Parser")
print("=" * 50)

# 定义 Pydantic 模型
class WeatherInfo(BaseModel):
    city: str = Field(description="城市名称")
    temperature: float = Field(description="温度，单位摄氏度")
    condition: str = Field(description="天气状况")
    humidity: int = Field(description="湿度百分比", ge=0, le=100)

# 创建带格式指令的提示模板
weather_parser = PydanticOutputParser(pydantic_object=WeatherInfo)

weather_prompt = PromptTemplate.from_template(
    """请提供{city}的天气信息。

    {format_instructions}

    城市：{city}""",
        partial_variables={"format_instructions": weather_parser.get_format_instructions()}
    )

print("提示模板:")
print(weather_prompt.format(city="北京"))
print()

print("PydanticOutputParser 格式指令:")
print(weather_parser.get_format_instructions())
print()

# =============================================
# 9. 异常处理与手动重试（替代已废弃的 RetryOutputParser）
# =============================================
# 注意：RetryOutputParser 已从 langchain_core 中移除。
# 在实际应用中，可通过 try-except 配合 LLM 调用重试来实现相同效果。
# 如需自动重试功能，可参考 langchain 的 OutputFixingParser。
print("=" * 50)
print("9. 异常处理与手动重试演示")
print("=" * 50)

def parse_with_retry(parser, text: str, max_retries: int = 3):
    """手动实现解析重试逻辑"""
    for attempt in range(1, max_retries + 1):
        try:
            return parser.parse(text)
        except Exception as e:
            print(f"  第 {attempt} 次尝试失败: {type(e).__name__}")
            if attempt == max_retries:
                print(f"  已达最大重试次数 {max_retries}，放弃解析")
                return None

# 测试：有效 JSON
good_output = '{"name": "测试", "value": 100}'
result = parse_with_retry(json_parser, good_output)
print(f"有效 JSON 解析结果: {result}")

# 测试：无效 JSON
bad_output = "这是一个无效的 JSON 输出。"
result = parse_with_retry(json_parser, bad_output, max_retries=3)
print(f"无效 JSON 最终结果: {result}")
print()

print("=" * 50)
print("所有示例执行完成！")
print("=" * 50)
