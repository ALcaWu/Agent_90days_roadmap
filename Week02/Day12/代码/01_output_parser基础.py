"""
Day 12 - 代码示例 1：Output Parser 基础
学习 LangChain 内置的各种 Output Parser 的基本用法
"""

from langchain_core.output_parsers import (
    StrOutputParser,
    JsonOutputParser,
    JsonLinesOutputParser,
    CommaSeparatedListOutputParser,
    DatetimeOutputParser,
    EnumOutputParser,
)
from langchain.prompts import PromptTemplate
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
# 3. JsonLinesOutputParser - JSON Lines 解析器
# =============================================
print("=" * 50)
print("3. JsonLinesOutputParser 示例")
print("=" * 50)

jsonlines_parser = JsonLinesOutputParser()

llm_output = '{"name": "Alice", "score": 95}\n{"name": "Bob", "score": 87}\n{"name": "Charlie", "score": 92}'
result = jsonlines_parser.parse(llm_output)
print(f"输入: {llm_output}")
print(f"输出: {result}")
print(f"类型: {type(result)}")
print()

# =============================================
# 4. CommaSeparatedListOutputParser - 列表分隔解析器
# =============================================
print("=" * 50)
print("4. CommaSeparatedListOutputParser 示例")
print("=" * 50)

list_parser = CommaSeparatedListOutputParser()

result = list_parser.parse("Apple, Banana, Cherry, Date, Elderberry")
print(f"输入: 'Apple, Banana, Cherry, Date, Elderberry'")
print(f"输出: {result}")
print(f"类型: {type(result)}")
print()

# =============================================
# 5. DatetimeOutputParser - 日期时间解析器
# =============================================
print("=" * 50)
print("5. DatetimeOutputParser 示例")
print("=" * 50)

datetime_parser = DatetimeOutputParser()

result = datetime_parser.parse("2024-06-15T14:30:00")
print(f"输入: '2024-06-15T14:30:00'")
print(f"输出: {result}")
print(f"类型: {type(result)}")
print(f"年份: {result.year}, 月份: {result.month}, 日: {result.day}")
print()

# =============================================
# 6. EnumOutputParser - 枚举解析器
# =============================================
print("=" * 50)
print("6. EnumOutputParser 示例")
print("=" * 50)

class Status(Enum):
    PENDING = "待处理"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"
    CANCELLED = "已取消"

enum_parser = EnumOutputParser(enum=Status)

# 测试不同的输入
test_inputs = ["待处理", "进行中", "已完成", "已取消"]
for inp in test_inputs:
    try:
        result = enum_parser.parse(inp)
        print(f"输入: '{inp}' -> 输出: {result} (类型: {type(result)})")
    except Exception as e:
        print(f"输入: '{inp}' -> 错误: {e}")
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
print(list_parser.get_format_instructions())
print()

print("DatetimeOutputParser 格式指令:")
print(datetime_parser.get_format_instructions())
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
from langchain_core.output_parsers import PydanticOutputParser

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
# 9. Parser 的 parse_with_retry 方法
# =============================================
print("=" * 50)
print("9. parse_with_retry 方法")
print("=" * 50)

from langchain_core.output_parsers import RetryOutputParser

# 基本 JSON Parser
base_json_parser = JsonOutputParser()

# 包装为带重试的 Parser
retry_parser = RetryOutputParser(
    parser=base_json_parser,
    max_retries=3,
    retry_on_parse_error=True
)

# 模拟有格式问题的输出
bad_output = '''
这是一个无效的 JSON 输出。
没有正确的 JSON 格式。
'''

try:
    result = retry_parser.parse(bad_output)
    print(f"结果: {result}")
except Exception as e:
    print(f"重试后仍然失败: {type(e).__name__}")
print()

print("=" * 50)
print("所有示例执行完成！")
print("=" * 50)