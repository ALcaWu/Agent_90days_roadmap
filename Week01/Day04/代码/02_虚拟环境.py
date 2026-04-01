# -*- coding: utf-8 -*-
"""
Day 04 - 虚拟环境与pip示例
知识点：venv操作、pip命令、requirements.txt

注意：虚拟环境操作通常在命令行完成
这个文件演示如何在代码中获取环境信息
"""

import sys
import subprocess
from pathlib import Path


# ==================== 1. 检测当前环境 ====================

print("=" * 50)
print("当前Python环境信息")
print("=" * 50)

print(f"Python路径: {sys.executable}")
print(f"Python版本: {sys.version}")
print(f"虚拟环境: {sys.prefix}")

# 判断是否在虚拟环境中
in_venv = sys.prefix != sys.base_prefix
print(f"是否在虚拟环境中: {'是' if in_venv else '否'}")

print()


# ==================== 2. pip命令参考 ====================

print("=" * 50)
print("pip常用命令参考")
print("=" * 50)

pip_commands = """
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\\Scripts\\activate

# 激活虚拟环境（macOS/Linux）
source venv/bin/activate

# 安装包
pip install langchain
pip install langchain==0.1.0       # 指定版本
pip install langchain>=0.1.0,<0.3  # 版本范围

# 查看已安装的包
pip list
pip list --outdated  # 查看可升级的包

# 查看包详情
pip show langchain

# 导出依赖
pip freeze > requirements.txt

# 从文件安装依赖
pip install -r requirements.txt

# 卸载包
pip uninstall langchain

# 升级pip
python -m pip install --upgrade pip
"""
print(pip_commands)


# ==================== 3. requirements.txt格式 ====================

print("=" * 50)
print("requirements.txt 示例格式")
print("=" * 50)

requirements_example = """
# AI开发常用依赖

# LangChain核心
langchain>=0.1.0
langchain-openai>=0.0.5

# 向量数据库
chromadb>=0.4.0
faiss-cpu>=1.7.0

# 工具库
python-dotenv>=1.0.0
requests>=2.31.0
pydantic>=2.0.0

# 开发工具
pytest>=7.0.0
black>=23.0.0
"""
print(requirements_example)


# ==================== 4. 在代码中执行pip命令 ====================

print("=" * 50)
print("已安装的部分包（演示）")
print("=" * 50)

try:
    # 获取已安装包列表
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=freeze"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # 筛选AI相关包
    ai_packages = ["langchain", "openai", "requests", "pydantic", "numpy", "pandas"]
    lines = result.stdout.strip().split("\n")
    
    print("AI开发相关包:")
    found = False
    for line in lines:
        if any(pkg in line.lower() for pkg in ai_packages):
            print(f"  {line}")
            found = True
    
    if not found:
        print("  （未安装AI相关包，后续课程会安装）")
        
except Exception as e:
    print(f"获取包列表失败: {e}")


# ==================== 5. 最佳实践 ====================

print()
print("=" * 50)
print("虚拟环境最佳实践")
print("=" * 50)

best_practices = """
1. 每个项目一个虚拟环境
   - 项目目录下创建 venv/ 或 .venv/
   
2. 将 venv/ 加入 .gitignore
   - 不要提交虚拟环境到Git
   
3. 使用 requirements.txt 管理依赖
   - pip freeze > requirements.txt
   - 版本锁定确保团队环境一致
   
4. 区分开发依赖和生产依赖
   - requirements.txt（生产）
   - requirements-dev.txt（开发：pytest, black等）
   
5. AI项目典型依赖结构
   langchain          # 核心框架
   langchain-openai   # OpenAI集成
   langchain-community # 社区工具
   chromadb/faiss     # 向量数据库
   python-dotenv      # 环境变量管理
"""
print(best_practices)
