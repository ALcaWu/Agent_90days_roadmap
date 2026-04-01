# -*- coding: utf-8 -*-
"""
Day 04 - 模块与包管理示例
知识点：import机制、__name__、包结构、常用标准库
"""

# ==================== 1. import的四种方式 ====================

# 方式1：导入整个模块
import math
print(f"math.sqrt(16) = {math.sqrt(16)}")

# 方式2：导入特定对象
from math import sqrt, pi
print(f"sqrt(25) = {sqrt(25)}")
print(f"pi = {pi:.6f}")

# 方式3：起别名（AI开发常用）
import datetime as dt
print(f"当前时间: {dt.datetime.now()}")

# 方式4：导入所有（不推荐，仅演示）
# from math import *  # 会污染命名空间

print("-" * 50)


# ==================== 2. __name__ == "__main__" ====================

def calculate_area(radius):
    """计算圆面积"""
    return pi * radius ** 2

def main():
    """主函数：直接运行时执行"""
    print("【主程序运行】")
    r = 5
    area = calculate_area(r)
    print(f"半径 {r} 的圆面积 = {area:.2f}")

# 关键：只有直接运行此文件时才执行main()
if __name__ == "__main__":
    main()
else:
    print(f"【模块被导入】模块名: {__name__}")

print("-" * 50)


# ==================== 3. 常用标准库 ====================

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional  # 类型提示（AI开发必备）

# os模块：环境变量、路径操作
print(f"当前工作目录: {os.getcwd()}")
print(f"HOME目录: {os.environ.get('HOME', '未设置')}")

# sys模块：Python解释器信息
print(f"Python版本: {sys.version}")
print(f"Python路径: {sys.executable}")

# pathlib：现代路径操作（推荐）
current_file = Path(__file__)
print(f"当前文件: {current_file}")
print(f"父目录: {current_file.parent}")

# typing：类型提示（让代码更清晰）
def process_messages(messages: List[Dict[str, str]]) -> Optional[str]:
    """
    处理消息列表（AI Agent中常见）
    
    Args:
        messages: 消息列表，如 [{"role": "user", "content": "你好"}]
    
    Returns:
        处理后的内容，或None
    """
    if not messages:
        return None
    return messages[-1].get("content", "")

# 测试类型提示函数
test_messages = [
    {"role": "system", "content": "你是助手"},
    {"role": "user", "content": "你好"}
]
print(f"最后一条消息: {process_messages(test_messages)}")

print("-" * 50)


# ==================== 4. 模块搜索路径 ====================

print("模块搜索路径（sys.path）：")
for i, p in enumerate(sys.path[:5], 1):  # 只显示前5个
    print(f"  {i}. {p}")

print("\n提示：自定义模块需要放在sys.path中的目录里才能被导入")
