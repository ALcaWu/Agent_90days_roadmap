"""
Day 01 代码示例：Python基础语法 - 数据类型
学习目标：掌握Python核心数据类型及其操作
"""

# ============================================
# 1. 变量与基本数据类型
# ============================================

name = "吴文杰"
age = 25
height = 1.75
is_developer = True

print("=== 基本数据类型 ===")
print(f"姓名: {name}, 类型: {type(name)}")
print(f"年龄: {age}, 类型: {type(age)}")
print(f"身高: {height}, 类型: {type(height)}")
print(f"是否开发者: {is_developer}, 类型: {type(is_developer)}")

# ============================================
# 2. 字符串操作
# ============================================

print("\n=== 字符串操作 ===")

text = "Agent Development Course"
print(f"原始字符串: {text}")
print(f"大写: {text.upper()}")
print(f"小写: {text.lower()}")
print(f"分割: {text.split()}")
print(f"替换: {text.replace('Agent', 'AI')}")

# f-string格式化
model = "GPT-4"
tokens = 1000
cost = 0.03
print(f"\n模型: {model}, Token数: {tokens}, 成本: ${cost:.4f}")

# ============================================
# 3. 数值运算
# ============================================

print("\n=== 数值运算 ===")

a, b = 10, 3
print(f"{a} + {b} = {a + b}")
print(f"{a} - {b} = {a - b}")
print(f"{a} * {b} = {a * b}")
print(f"{a} / {b} = {a / b:.2f}")
print(f"{a} // {b} = {a // b} (整除)")
print(f"{a} ** {b} = {a ** b} (幂运算)")

# AI开发中的成本计算
cost_per_1k_tokens = 0.002
input_tokens = 500
output_tokens = 300
total_cost = (input_tokens + output_tokens) / 1000 * cost_per_1k_tokens
print(f"\nAPI调用成本: ${total_cost:.6f}")

# ============================================
# 4. 列表操作
# ============================================

print("\n=== 列表操作 ===")

models = ["GPT-4", "Claude-3", "Gemini"]
print(f"模型列表: {models}")
print(f"第一个: {models[0]}, 最后一个: {models[-1]}")

# 添加和删除
models.append("Llama-3")
print(f"添加后: {models}")

# 列表切片
numbers = list(range(10))
print(f"\n原始列表: {numbers}")
print(f"前3个: {numbers[:3]}")
print(f"后3个: {numbers[-3:]}")

# 列表推导式
squares = [x**2 for x in range(10)]
print(f"\n平方数: {squares}")

evens = [x for x in range(20) if x % 2 == 0]
print(f"偶数: {evens}")

# ============================================
# 5. 字典操作
# ============================================

print("\n=== 字典操作 ===")

config = {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2048
}
print(f"配置: {config}")

# 访问值
print(f"模型: {config['model']}")
print(f"模型(推荐): {config.get('model')}")
print(f"不存在的键: {config.get('api_key', '未设置')}")

# 遍历字典
print("\n遍历配置:")
for key, value in config.items():
    print(f"  {key}: {value}")

# 模拟API响应
api_response = {
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": "你好！我是AI助手。"
            }
        }
    ],
    "usage": {
        "prompt_tokens": 15,
        "completion_tokens": 20,
        "total_tokens": 35
    }
}

print(f"\nAPI响应: {api_response['choices'][0]['message']['content']}")
print(f"Token使用: {api_response['usage']}")

# ============================================
# 6. 元组与集合
# ============================================

print("\n=== 元组与集合 ===")

# 元组
coordinates = (100, 200)
x, y = coordinates
print(f"坐标: x={x}, y={y}")

# 集合去重
duplicates = [1, 1, 2, 2, 3, 3]
unique = list(set(duplicates))
print(f"\n去重前: {duplicates}")
print(f"去重后: {unique}")

# 集合运算
set_a = {"GPT-4", "Claude", "Gemini"}
set_b = {"Claude", "Gemini", "Llama"}
print(f"\n并集: {set_a | set_b}")
print(f"交集: {set_a & set_b}")

# ============================================
# 7. 实战：模型配置管理
# ============================================

print("\n=== 实战：模型配置管理 ===")

model_configs = {
    "gpt-4": {
        "provider": "OpenAI",
        "context_window": 8192,
        "cost_per_1k": 0.03
    },
    "gpt-3.5-turbo": {
        "provider": "OpenAI",
        "context_window": 4096,
        "cost_per_1k": 0.002
    },
    "claude-3": {
        "provider": "Anthropic",
        "context_window": 100000,
        "cost_per_1k": 0.015
    }
}

# 找出上下文窗口最大的模型
max_context = max(model_configs.items(), key=lambda x: x[1]["context_window"])
print(f"最大上下文: {max_context[0]} ({max_context[1]['context_window']} tokens)")

# 找出最便宜的模型
cheapest = min(model_configs.items(), key=lambda x: x[1]["cost_per_1k"])
print(f"最便宜: {cheapest[0]} (${cheapest[1]['cost_per_1k']}/1k tokens)")

print("\n" + "="*50)
print("Day 01 数据类型示例运行完成！")
print("="*50)