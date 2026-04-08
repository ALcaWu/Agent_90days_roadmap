"""
Day 12 - 代码示例 3：自定义 Output Parser
学习如何创建满足特殊需求的 Output Parser
"""

from langchain_core.output_parsers import BaseOutputParser
from langchain_core.outputs import Generation
from typing import Any, List
import re
import xml.etree.ElementTree as ET


# =============================================
# 1. 数字列表解析器
# =============================================
print("=" * 50)
print("1. 数字列表解析器")
print("=" * 50)

class NumberListParser(BaseOutputParser[List[float]]):
    """从文本中提取所有数字"""

    def parse(self, text: str) -> List[float]:
        # 提取所有数字（整数和浮点数）
        numbers = re.findall(r'-?\d+\.?\d*', text)
        result = []
        for num in numbers:
            try:
                result.append(float(num))
            except ValueError:
                continue
        if not result:
            raise ValueError(f"未找到有效数字，输入: {text}")
        return result

    def get_format_instructions(self) -> str:
        return """请输出一组数字，用空格分隔。
例如：3.14 2.718 1.414 42"""


parser = NumberListParser()

# 测试各种输入
test_cases = [
    "答案是 42 和 3.14 以及 100",
    "温度：25.5度，湿度：60%",
    "价格区间：99.9 - 199.9 元",
    "没有数字在这里",
]

for test in test_cases:
    try:
        result = parser.parse(test)
        print(f"输入: '{test}'")
        print(f"输出: {result}")
    except ValueError as e:
        print(f"输入: '{test}'")
        print(f"错误: {e}")
    print()

# =============================================
# 2. XML 解析器
# =============================================
print("=" * 50)
print("2. XML 解析器")
print("=" * 50)

class XMLParser(BaseOutputParser):
    """解析 XML 格式输出"""

    def parse(self, text: str) -> dict:
        # 尝试提取 XML 内容
        match = re.search(r'<root>(.*?)</root>', text, re.DOTALL)
        if match:
            xml_content = match.group(1)
        else:
            # 尝试直接解析整个文本
            xml_content = text.strip()

        try:
            root = ET.fromstring(f"<root>{xml_content}</root>")
            return self._element_to_dict(root)
        except ET.ParseError as e:
            raise ValueError(f"XML 解析失败: {e}")

    def _element_to_dict(self, element) -> dict:
        result = {}
        for child in element:
            if len(child) == 0:  # 叶子节点
                result[child.tag] = child.text
            else:  # 有子节点
                result[child.tag] = self._element_to_dict(child)
        return result

    def get_format_instructions(self) -> str:
        return """请用 XML 格式输出，包含 <root> 标签。
例如：
<root>
  <name>张三</name>
  <age>25</age>
</root>"""


parser = XMLParser()

llm_output = """
以下是信息：
<root>
  <name>张三</name>
  <age>25</age>
  <address>
    <city>北京</city>
    <street>中关村大街1号</street>
  </address>
</root>
"""

result = parser.parse(llm_output)
print(f"XML 解析结果:")
print(f"  {result}")
print()

# =============================================
# 3. Markdown 列表解析器
# =============================================
print("=" * 50)
print("3. Markdown 列表解析器")
print("=" * 50)

class MarkdownListParser(BaseOutputParser[List[str]]):
    """解析 Markdown 格式的列表"""

    def parse(self, text: str) -> List[str]:
        lines = text.strip().split('\n')
        result = []

        for line in lines:
            # 去除列表标记
            cleaned = re.sub(r'^\s*[-*+]|\d+\.\s+', '', line).strip()
            if cleaned:
                result.append(cleaned)

        return result

    def get_format_instructions(self) -> str:
        return """请用 Markdown 列表格式输出，每行以 '-' 开头。
例如：
- 项目一
- 项目二
- 项目三"""


parser = MarkdownListParser()

llm_output = """
主要特点：
- 第一个特点：高性能
- 第二个特点：易用性强
- 第三个特点：社区活跃
"""

result = parser.parse(llm_output)
print(f"Markdown 列表解析结果:")
for item in result:
    print(f"  - {item}")
print()

# =============================================
# 4. Markdown 表格解析器
# =============================================
print("=" * 50)
print("4. Markdown 表格解析器")
print("=" * 50)

class MarkdownTableParser(BaseOutputParser[List[dict]]):
    """解析 Markdown 表格"""

    def parse(self, text: str) -> List[dict]:
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]

        # 找到表头行
        header_line = None
        separator_idx = None
        data_start = 0

        for i, line in enumerate(lines):
            if '|' in line and not re.match(r'^\s*\|[\s:|]+\|$', line):
                header_line = line
                data_start = i + 2
                break

        if not header_line:
            raise ValueError("未找到有效的 Markdown 表格")

        # 解析表头
        headers = [h.strip() for h in header_line.split('|') if h.strip()]

        # 解析数据行
        result = []
        for line in lines[data_start:]:
            if '|' in line and not re.match(r'^\s*\|[\s:|]+\|$', line):
                cells = [c.strip() for c in line.split('|') if c.strip()]
                if len(cells) == len(headers):
                    result.append(dict(zip(headers, cells)))

        return result

    def get_format_instructions(self) -> str:
        return """请用 Markdown 表格格式输出。
例如：
| 姓名 | 年龄 | 城市 |
|------|------|------|
| 张三 | 25   | 北京 |
| 李四 | 30   | 上海 |"""


parser = MarkdownTableParser()

llm_output = """
| 姓名 | 年龄 | 城市 | 职业 |
|------|------|------|------|
| 张三 | 25   | 北京 | 工程师 |
| 李四 | 30   | 上海 | 设计师 |
| 王五 | 28   | 广州 | 产品经理 |
"""

result = parser.parse(llm_output)
print(f"Markdown 表格解析结果:")
for row in result:
    print(f"  {row}")
print()

# =============================================
# 5. 键值对解析器
# =============================================
print("=" * 50)
print("5. 键值对解析器")
print("=" * 50)

class KeyValueParser(BaseOutputParser[dict]):
    """解析键值对格式输出"""

    def parse(self, text: str) -> dict:
        result = {}
        lines = text.strip().split('\n')

        for line in lines:
            # 匹配 "键: 值" 或 "键 = 值" 格式
            match = re.match(r'^[\u4e00-\u9fa5a-zA-Z\s]+[：:=]\s*(.+)$', line.strip())
            if match:
                key = re.sub(r'[：:=]', '', line).strip()
                value = match.group(1).strip()
                result[key] = value

        return result

    def get_format_instructions(self) -> str:
        return """请用键值对格式输出，每行一个，用中文冒号分隔。
例如：
姓名：张三
年龄：25
城市：北京"""


parser = KeyValueParser()

llm_output = """
用户信息：
姓名：张三
年龄：25
邮箱：zhangsan@example.com
电话：138-0013-8000
"""

result = parser.parse(llm_output)
print(f"键值对解析结果:")
for key, value in result.items():
    print(f"  {key}: {value}")
print()

# =============================================
# 6. 带验证的 URL 列表解析器
# =============================================
print("=" * 50)
print("6. 带验证的 URL 列表解析器")
print("=" * 50)

class URLListParser(BaseOutputParser[List[str]]):
    """提取并验证 URL"""

    def parse(self, text: str) -> List[str]:
        # URL 正则表达式
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)

        # 去除末尾的标点符号
        cleaned_urls = []
        for url in urls:
            # 去除常见标点
            url = url.rstrip('.,;:!?。，；：！？')
            cleaned_urls.append(url)

        if not cleaned_urls:
            raise ValueError("未找到有效 URL")
        return cleaned_urls

    def get_format_instructions(self) -> str:
        return """请列出相关链接，每行一个 URL。
例如：
https://example.com
https://docs.python.org"""


parser = URLListParser()

llm_output = """
以下是参考资料：
- Python文档：https://docs.python.org
- LangChain文档：https://python.langchain.com
- GitHub仓库：https://github.com

学有余力可以查看：https://pydantic-docs.logicalclocks.ai/
"""

result = parser.parse(llm_output)
print(f"URL 列表解析结果:")
for url in result:
    print(f"  - {url}")
print()

print("=" * 50)
print("所有自定义 Parser 示例执行完成！")
print("=" * 50)