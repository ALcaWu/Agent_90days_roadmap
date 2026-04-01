"""
Day 01 代码示例：Python基础语法 - 模块与JSON
学习目标：掌握模块导入和JSON数据处理
"""

# ============================================
# 1. 常用内置模块
# ============================================

print("=== 常用内置模块 ===")

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# os模块
print(f"当前目录: {os.getcwd()}")
print(f"目录内容: {os.listdir('.')[:5]}...")  # 只显示前5个

# pathlib模块
project_path = Path("D:/AgentDeveloperCourse")
print(f"\n项目路径: {project_path}")
print(f"路径存在: {project_path.exists()}")

# datetime模块
now = datetime.now()
print(f"\n当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")

# ============================================
# 2. JSON处理（AI开发必备）
# ============================================

print("\n=== JSON处理 ===")

# 字典转JSON字符串
config = {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2048,
    "messages": [
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "Hello"}
    ]
}

json_str = json.dumps(config, indent=2, ensure_ascii=False)
print("JSON字符串:")
print(json_str)

# JSON字符串转字典
parsed = json.loads(json_str)
print(f"\n解析后类型: {type(parsed)}")
print(f"模型: {parsed['model']}")

# ============================================
# 3. 文件读写
# ============================================

print("\n=== 文件读写 ===")

# 写入JSON文件
config_path = Path("D:/AgentDeveloperCourse/Week01/Day01/代码/config.json")
with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
print(f"配置已保存: {config_path}")

# 读取JSON文件
with open(config_path, "r", encoding="utf-8") as f:
    loaded_config = json.load(f)
print(f"读取的模型: {loaded_config['model']}")

# ============================================
# 4. 实战：API响应处理
# ============================================

print("\n=== 实战：API响应处理 ===")

# 模拟OpenAI API响应
api_response_json = """
{
    "id": "chatcmpl-xxx",
    "object": "chat.completion",
    "created": 1234567890,
    "model": "gpt-4",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Agent是一种能够自主执行任务的AI系统。"
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 15,
        "completion_tokens": 25,
        "total_tokens": 40
    }
}
"""

# 解析响应
response = json.loads(api_response_json)

# 提取关键信息
content = response["choices"][0]["message"]["content"]
tokens = response["usage"]["total_tokens"]

print(f"AI回复: {content}")
print(f"消耗Token: {tokens}")

# 计算成本
cost_per_1k = 0.03
cost = (tokens / 1000) * cost_per_1k
print(f"调用成本: ${cost:.6f}")

# ============================================
# 5. 实战：配置管理
# ============================================

print("\n=== 实战：配置管理 ===")

def save_config(config, filepath):
    """保存配置到文件"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"配置已保存: {filepath}")

def load_config(filepath):
    """从文件加载配置"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_config(config):
    """验证配置"""
    required_keys = ["model", "temperature", "max_tokens"]
    for key in required_keys:
        if key not in config:
            return False, f"缺少配置项: {key}"
    
    if not 0 <= config["temperature"] <= 2:
        return False, "temperature必须在0-2之间"
    
    if config["max_tokens"] < 1:
        return False, "max_tokens必须大于0"
    
    return True, "配置有效"

# 测试
test_config = {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2048,
    "api_key": "sk-xxx"
}

is_valid, message = validate_config(test_config)
print(f"验证结果: {message}")

# ============================================
# 6. 实战：批量配置生成
# ============================================

print("\n=== 实战：批量配置 ===")

# 生成多个测试配置
base_config = {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 500
}

temperatures = [0.0, 0.3, 0.5, 0.7, 1.0]

batch_configs = []
for i, temp in enumerate(temperatures):
    config = base_config.copy()
    config["temperature"] = temp
    config["id"] = f"config_{i+1}"
    batch_configs.append(config)

print(f"生成 {len(batch_configs)} 个配置:")
for cfg in batch_configs[:3]:
    print(f"  {cfg['id']}: temperature={cfg['temperature']}")

# 保存批量配置
batch_path = Path("D:/AgentDeveloperCourse/Week01/Day01/代码/batch_configs.json")
with open(batch_path, "w", encoding="utf-8") as f:
    json.dump(batch_configs, f, indent=2)
print(f"\n批量配置已保存: {batch_path}")

print("\n" + "="*50)
print("Day 01 模块与JSON示例运行完成！")
print("="*50)