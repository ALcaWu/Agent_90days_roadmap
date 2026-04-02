# -*- coding: utf-8 -*-
"""
Day 08 - 环境配置与API Key管理
知识点：.env文件、python-dotenv、安全管理

使用前请确保安装所需依赖：
pip install python-dotenv
pip install langchain-openai
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    dotenv_available = True
except ImportError:
    print("警告: python-dotenv 未安装，请运行以下命令安装:")
    print("pip install python-dotenv")
    dotenv_available = False


# ==================== 1. .env 文件配置 ====================

print("=" * 50)
print("1. .env 文件配置")
print("=" * 50)

# .env 文件示例内容
env_example = """
# OpenAI API Key
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 可选：自定义模型
# OPENAI_MODEL=gpt-4

# 可选：API基础URL（使用代理）
# OPENAI_API_BASE=https://api.openai.com/v1
"""
print(".env 文件示例:")
print(env_example)


# ==================== 2. 加载环境变量 ====================

print("\n" + "=" * 50)
print("2. 加载环境变量")
print("=" * 50)

# 方式1：在项目根目录创建 .env 文件
# 然后使用 python-dotenv 加载

if dotenv_available:
    env_file = Path("D:/AgentDeveloperCourse/.env")
    if env_file.exists():
        load_dotenv(env_file)
        print(f"已从 {env_file} 加载环境变量")
    else:
        # 创建示例 .env 文件
        with open(env_file, "w", encoding="utf-8") as f:
            f.write("# OpenAI API Key\n")
            f.write("# OPENAI_API_KEY=sk-your-key-here\n")
        print(f"已创建示例 .env 文件: {env_file}")

    # 检查是否加载成功
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        # 显示部分Key（安全起见）
        masked = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 15 else "***"
        print(f"OPENAI_API_KEY: {masked}")
    else:
        print("OPENAI_API_KEY: 未设置 (请在 .env 文件中配置)")
else:
    print("由于缺少 dotenv 模块，跳过环境变量加载")


# ==================== 3. 安全最佳实践 ====================

print("\n" + "=" * 50)
print("3. API Key 安全最佳实践")
print("=" * 50)

security_tips = """
安全规范：

1. 绝对不要把真实 API Key 提交到 Git！
   - .env 文件已加入 .gitignore

2. 生产环境使用环境变量或密钥管理服务：
   - AWS Secrets Manager
   - GCP Secret Manager
   - Azure Key Vault

3. 定期轮换 API Key

4. 设置使用限额，防止超额
"""
print(security_tips)


# ==================== 4. 代码中的安全使用 ====================

print("\n" + "=" * 50)
print("4. 代码中的安全使用")
print("=" * 50)


def get_openai_llm(temperature: float = 0.7):
    """
    安全获取 OpenAI LLM 实例
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "未设置 OPENAI_API_KEY 环境变量\n"
            "请在 .env 文件中配置: OPENAI_API_KEY=sk-xxx"
        )

    # 验证Key格式（简单检查）
    if not api_key.startswith("sk-"):
        raise ValueError("API Key 格式不正确，应以 'sk-' 开头")

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=temperature,
    )


# 测试获取LLM
try:
    llm = get_openai_llm()
    print("成功创建 LLM 实例")
    print(f"  模型: {llm.model_name}")
except ValueError as e:
    print(f"错误: {e}")


# ==================== 5. 多模型配置示例 ====================

print("\n" + "=" * 50)
print("5. 多模型配置")
print("=" * 50)


def create_llm(provider: str = "openai", model: str = "gpt-5.1", **kwargs):
    """
    统一的LLM创建函数
    """
    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=model, **kwargs)
    elif provider == "anthropic":
        # Claude 需要安装 langchain-anthropic
        # from langchain_anthropic import ChatAnthropic
        # return ChatAnthropic(model=model, **kwargs)
        print("Claude 集成需要: pip install langchain-anthropic")
        return None
    else:
        raise ValueError(f"不支持的 provider: {provider}")


# 配置示例
llm_configs = [
    {"provider": "openai", "model": "gpt-5.1", "temperature": 0.7},
    {"provider": "openai", "model": "gpt-4", "temperature": 0.5},
]

for config in llm_configs:
    print(f"配置: {config['provider']} - {config['model']}")
    # llm = create_llm(**config)
