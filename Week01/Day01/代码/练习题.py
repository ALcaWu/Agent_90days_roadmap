"""
Day 01 练习题
完成以下练习，巩固今日所学内容
"""

# ============================================
# 练习1：数据结构操作
# ============================================

print("=== 练习1：数据结构操作 ===")

# 给定模型配置列表
models = [
    {"name": "GPT-4", "provider": "OpenAI", "cost_per_1k": 0.03, "context": 8192},
    {"name": "GPT-3.5-Turbo", "provider": "OpenAI", "cost_per_1k": 0.002, "context": 4096},
    {"name": "Claude-3-Opus", "provider": "Anthropic", "cost_per_1k": 0.015, "context": 200000},
    {"name": "Claude-3-Sonnet", "provider": "Anthropic", "cost_per_1k": 0.003, "context": 200000},
    {"name": "Gemini-Pro", "provider": "Google", "cost_per_1k": 0.001, "context": 32000},
]

# TODO 1: 找出成本最低的模型
cheapest = min(models, key=lambda x: x["cost_per_1k"])
print(f"最便宜的模型: {cheapest['name']} (${cheapest['cost_per_1k']}/1k)")

# TODO 2: 找出上下文窗口最大的模型
largest_context = max(models, key=lambda x: x["context"])
print(f"最大上下文: {largest_context['name']} ({largest_context['context']:,} tokens)")

# TODO 3: 按提供商分组
from collections import defaultdict
grouped = defaultdict(list)
for m in models:
    grouped[m["provider"]].append(m["name"])

print("\n按提供商分组:")
for provider, names in grouped.items():
    print(f"  {provider}: {names}")

# TODO 4: 筛选出成本低于$0.01的模型
cheap_models = [m for m in models if m["cost_per_1k"] < 0.01]
print(f"\n成本低于$0.01: {[m['name'] for m in cheap_models]}")

# ============================================
# 练习2：API调用模拟
# ============================================

print("\n=== 练习2：API调用模拟 ===")

def mock_api_call(prompt, model="gpt-3.5-turbo", temperature=0.7):
    """模拟API调用"""
    import random
    
    # 模拟延迟
    response = {
        "id": f"chatcmpl-{random.randint(1000, 9999)}",
        "model": model,
        "choices": [{
            "message": {
                "role": "assistant",
                "content": f"这是对'{prompt[:20]}...'的回答"
            }
        }],
        "usage": {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": random.randint(50, 200),
            "total_tokens": len(prompt.split()) + random.randint(50, 200)
        }
    }
    return response

# 测试调用
result = mock_api_call("介绍一下Python的优点", model="gpt-4")
print(f"模型: {result['model']}")
print(f"回复: {result['choices'][0]['message']['content']}")
print(f"Token: {result['usage']['total_tokens']}")

# ============================================
# 练习3：配置文件处理
# ============================================

print("\n=== 练习3：配置文件处理 ===")

import json
from pathlib import Path

# 创建配置
config = {
    "api_settings": {
        "base_url": "https://api.openai.com/v1",
        "timeout": 30,
        "max_retries": 3
    },
    "default_params": {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2048
    },
    "models": ["gpt-4", "gpt-3.5-turbo", "claude-3"]
}

# 保存配置
config_path = Path("D:/AgentDeveloperCourse/Week01/Day01/代码/practice_config.json")
with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
print(f"配置已保存: {config_path}")

# 读取并验证
with open(config_path, "r", encoding="utf-8") as f:
    loaded = json.load(f)

print(f"默认模型: {loaded['default_params']['model']}")
print(f"支持模型: {loaded['models']}")

# ============================================
# 练习4：错误处理
# ============================================

print("\n=== 练习4：错误处理 ===")

def safe_api_call(prompt, max_retries=3):
    """带重试的安全API调用"""
    import random
    
    for attempt in range(max_retries):
        try:
            # 模拟随机失败
            if random.random() < 0.3:
                raise Exception("API Error: Rate Limited")
            
            return {"status": "success", "response": f"回答: {prompt[:20]}..."}
        
        except Exception as e:
            print(f"  第{attempt+1}次失败: {e}")
            if attempt < max_retries - 1:
                print("  重试中...")
    
    return {"status": "failed", "error": "超过最大重试次数"}

result = safe_api_call("测试问题")
print(f"结果: {result['status']}")

# ============================================
# 练习5：综合应用
# ============================================

print("\n=== 练习5：综合应用 ===")

class SimpleAgent:
    """简单的Agent类"""
    
    def __init__(self, name, model="gpt-3.5-turbo"):
        self.name = name
        self.model = model
        self.history = []
    
    def chat(self, message):
        """发送消息"""
        self.history.append({"role": "user", "content": message})
        
        # 模拟响应
        response = f"[{self.name}] 收到: {message}"
        self.history.append({"role": "assistant", "content": response})
        
        return response
    
    def get_history(self):
        """获取历史记录"""
        return self.history
    
    def clear_history(self):
        """清空历史"""
        self.history = []

# 使用Agent
agent = SimpleAgent("学习助手", "gpt-4")
print(agent.chat("你好"))
print(agent.chat("介绍一下Agent"))

print(f"\n历史记录: {len(agent.get_history())}条")

print("\n" + "="*50)
print("Day 01 练习题完成！")
print("="*50)