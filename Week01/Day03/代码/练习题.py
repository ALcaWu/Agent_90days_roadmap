"""
Day03 - 练习题
文件操作与正则表达式综合练习
"""

import re
import json
from pathlib import Path


# ============ 练习1: 日志文件分析 ============
def analyze_log_file(log_content: str) -> dict:
    """
    分析日志内容，统计各级别日志数量
    
    日志格式示例:
    2024-01-15 10:30:15 [INFO] User logged in
    2024-01-15 10:31:20 [ERROR] Database connection failed
    2024-01-15 10:32:00 [WARNING] Memory usage high
    
    返回: {"INFO": 5, "ERROR": 2, "WARNING": 3}
    """
    result = {"INFO": 0, "ERROR": 0, "WARNING": 0}
    
    # 使用正则提取日志级别
    pattern = r'\[(INFO|ERROR|WARNING)\]'
    for match in re.finditer(pattern, log_content):
        level = match.group(1)
        result[level] += 1
    
    return result


# ============ 练习2: 配置文件管理器 ============
class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = self._load()
    
    def _load(self) -> dict:
        """加载配置"""
        if self.config_path.exists():
            return json.loads(self.config_path.read_text(encoding='utf-8'))
        return {}
    
    def get(self, key: str, default=None):
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """设置配置值"""
        self.config[key] = value
    
    def save(self):
        """保存配置到文件"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(
            json.dumps(self.config, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )


# ============ 练习3: 文本数据提取器 ============
class DataExtractor:
    """从文本中提取结构化数据"""
    
    @staticmethod
    def extract_emails(text: str) -> list:
        """提取邮箱地址"""
        pattern = r'[\w.-]+@[\w.-]+\.\w+'
        return re.findall(pattern, text)
    
    @staticmethod
    def extract_phones(text: str) -> list:
        """提取手机号"""
        pattern = r'1[3-9]\d{9}'
        return re.findall(pattern, text)
    
    @staticmethod
    def extract_urls(text: str) -> list:
        """提取URL"""
        pattern = r'https?://[\w./-]+'
        return re.findall(pattern, text)
    
    @staticmethod
    def extract_dates(text: str) -> list:
        """提取日期（YYYY-MM-DD格式）"""
        pattern = r'\d{4}-\d{2}-\d{2}'
        return re.findall(pattern, text)


# ============ 练习4: 文件内容替换工具 ============
def replace_in_file(file_path: str, old_pattern: str, new_text: str) -> int:
    """
    在文件中替换匹配的内容
    
    Args:
        file_path: 文件路径
        old_pattern: 要替换的正则模式
        new_text: 替换后的文本
    
    Returns:
        替换的次数
    """
    path = Path(file_path)
    if not path.exists():
        return 0
    
    content = path.read_text(encoding='utf-8')
    new_content, count = re.subn(old_pattern, new_text, content)
    
    if count > 0:
        path.write_text(new_content, encoding='utf-8')
    
    return count


# ============ 测试代码 ============
if __name__ == '__main__':
    print("=== 练习1: 日志分析 ===")
    log_content = """
2024-01-15 10:30:15 [INFO] User logged in
2024-01-15 10:31:20 [ERROR] Database connection failed
2024-01-15 10:32:00 [WARNING] Memory usage high
2024-01-15 10:33:10 [INFO] Request processed
2024-01-15 10:34:00 [ERROR] API timeout
"""
    result = analyze_log_file(log_content)
    print(f"日志统计: {result}")
    
    print("\n=== 练习2: 配置管理器 ===")
    config = ConfigManager('output/test_config.json')
    config.set('app_name', 'AI Agent')
    config.set('debug', True)
    config.save()
    print(f"应用名: {config.get('app_name')}")
    print(f"调试模式: {config.get('debug')}")
    
    print("\n=== 练习3: 数据提取 ===")
    text = """
联系方式: 邮箱 test@example.com，电话 13812345678
官网: https://example.com
日期: 2024-01-15
"""
    print(f"邮箱: {DataExtractor.extract_emails(text)}")
    print(f"电话: {DataExtractor.extract_phones(text)}")
    print(f"URL: {DataExtractor.extract_urls(text)}")
    print(f"日期: {DataExtractor.extract_dates(text)}")
    
    print("\n所有练习完成！")