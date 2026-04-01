"""
Day03 - 正则表达式示例
演示文本匹配、提取、替换等常用操作
"""

import re


def demo_basic_match():
    """基础匹配"""
    print("=== 基础匹配 ===")
    
    # match 从开头匹配
    result = re.match(r'Hello', 'Hello World')
    print(f"match结果: {result.group() if result else None}")
    
    # search 搜索任意位置
    result = re.search(r'\d+', 'abc123def')
    print(f"search结果: {result.group() if result else None}")
    
    # findall 查找所有
    numbers = re.findall(r'\d+', 'a1b23c456')
    print(f"findall结果: {numbers}")


def demo_groups():
    """分组捕获"""
    print("\n=== 分组捕获 ===")
    
    # 普通分组
    text = "张三: 13812345678"
    match = re.search(r'(\w+):\s*(\d+)', text)
    if match:
        print(f"姓名: {match.group(1)}")
        print(f"电话: {match.group(2)}")
    
    # 命名分组
    text = "2024-01-15"
    match = re.search(r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})', text)
    if match:
        print(f"年份: {match.group('year')}")
        print(f"月份: {match.group('month')}")


def demo_replace():
    """替换操作"""
    print("\n=== 替换操作 ===")
    
    # 基础替换
    text = "价格: 100元, 数量: 5个"
    result = re.sub(r'\d+', 'X', text)
    print(f"替换数字: {result}")
    
    # 使用函数替换
    def double_price(match):
        return str(int(match.group()) * 2)
    
    text = "原价: 100元"
    result = re.sub(r'\d+', double_price, text)
    print(f"价格翻倍: {result}")


def demo_validation():
    """数据验证"""
    print("\n=== 数据验证 ===")
    
    def is_valid_email(email):
        pattern = r'^[\w.-]+@[\w.-]+\.\w+$'
        return bool(re.match(pattern, email))
    
    def is_valid_phone(phone):
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))
    
    emails = ['test@example.com', 'invalid-email', 'user@domain.cn']
    for email in emails:
        print(f"{email}: {'有效' if is_valid_email(email) else '无效'}")
    
    phones = ['13812345678', '12345678901', '18888888888']
    for phone in phones:
        print(f"{phone}: {'有效' if is_valid_phone(phone) else '无效'}")


def demo_text_processing():
    """文本预处理（AI开发常用）"""
    print("\n=== 文本预处理 ===")
    
    def clean_text(text):
        """清理文本"""
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()
    
    def extract_urls(text):
        """提取URL"""
        return re.findall(r'https?://[\w./-]+', text)
    
    def extract_numbers(text):
        """提取数字"""
        return [int(n) for n in re.findall(r'\d+', text)]
    
    # 测试
    raw_text = "  <p>Hello</p>   World  访问 https://example.com 查看详情  "
    print(f"原始: {raw_text}")
    print(f"清理: {clean_text(raw_text)}")
    
    text_with_urls = "网站: https://python.org 和 https://github.com"
    print(f"URLs: {extract_urls(text_with_urls)}")
    
    text_with_numbers = "买了3个苹果，5个橙子，共花费28元"
    print(f"数字: {extract_numbers(text_with_numbers)}")


if __name__ == '__main__':
    demo_basic_match()
    demo_groups()
    demo_replace()
    demo_validation()
    demo_text_processing()
    print("\n演示完成！")