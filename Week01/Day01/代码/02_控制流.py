"""
Day 01 代码示例：Python基础语法 - 控制流
学习目标：掌握条件判断和循环语句
"""

# ============================================
# 1. 条件语句
# ============================================

print("=== 条件语句 ===")

score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "D"

print(f"分数 {score} 对应等级: {grade}")

# 三元表达式
status = "通过" if score >= 60 else "不通过"
print(f"状态: {status}")

# 多条件判断
print("\n--- API调用条件检查 ---")
has_api_key = True
has_quota = True

if has_api_key and has_quota:
    print("✓ 可以调用API")
elif has_api_key and not has_quota:
    print("✗ API额度不足")
else:
    print("✗ 请先配置API Key")

# 检查值是否在列表中
allowed_models = ["gpt-4", "gpt-3.5-turbo", "claude-3"]
requested_model = "gpt-4"

if requested_model in allowed_models:
    print(f"✓ 模型 '{requested_model}' 可用")

# ============================================
# 2. for循环
# ============================================

print("\n=== for循环 ===")

models = ["GPT-4", "Claude-3", "Gemini", "Llama-3"]
print("可用模型:")
for model in models:
    print(f"  - {model}")

# 带索引遍历
print("\n带索引遍历:")
for index, model in enumerate(models):
    print(f"  [{index}] {model}")

# 遍历字典
model_costs = {"gpt-4": 0.03, "gpt-3.5-turbo": 0.002}
print("\n模型成本:")
for model, cost in model_costs.items():
    print(f"  {model}: ${cost}/1k tokens")

# ============================================
# 3. while循环
# ============================================

print("\n=== while循环 ===")

count = 0
print("倒计时:")
while count < 5:
    print(f"  {5 - count}")
    count += 1
print("  发射！")

# ============================================
# 4. 循环控制
# ============================================

print("\n=== 循环控制 ===")

# break示例
models = [
    {"name": "gpt-3.5-turbo", "context": 4096},
    {"name": "gpt-4", "context": 8192},
    {"name": "claude-3", "context": 100000}
]

print("查找上下文>10000的模型:")
for model in models:
    if model["context"] > 10000:
        print(f"  找到: {model['name']} (上下文: {model['context']})")
        break

# continue示例
print("\n只处理偶数:")
for i in range(10):
    if i % 2 != 0:
        continue
    print(f"  {i}", end=" ")
print()

# ============================================
# 5. 列表推导式
# ============================================

print("\n=== 列表推导式 ===")

squares = [x**2 for x in range(10)]
print(f"平方数: {squares}")

evens = [x for x in range(20) if x % 2 == 0]
print(f"偶数: {evens}")

# 复杂示例
configs = [
    {"model": "gpt-4", "cost": 0.03, "available": True},
    {"model": "gpt-3.5-turbo", "cost": 0.002, "available": True},
    {"model": "claude-3", "cost": 0.015, "available": False}
]

available_models = [c["model"] for c in configs if c["available"]]
print(f"可用模型: {available_models}")

cheap_models = [c["model"] for c in configs if c["cost"] < 0.01]
print(f"便宜模型: {cheap_models}")

# ============================================
# 6. 实战：API重试机制
# ============================================

print("\n=== 实战：API重试机制 ===")

import random

max_retries = 3
retry_count = 0
success = False

while retry_count < max_retries and not success:
    retry_count += 1
    if random.random() > 0.5:
        success = True
        print(f"  第{retry_count}次尝试: 成功 ✓")
    else:
        print(f"  第{retry_count}次尝试: 失败，重试中...")

if success:
    print("  ✓ API调用成功")
else:
    print(f"  ✗ {max_retries}次重试后仍失败")

# ============================================
# 7. 实战：模型选择器
# ============================================

print("\n=== 实战：模型选择器 ===")

def select_best_model(requirements):
    """根据需求选择最佳模型"""
    models = {
        "gpt-4": {"cost": 0.03, "vision": True, "context": 8192},
        "gpt-3.5-turbo": {"cost": 0.002, "vision": False, "context": 4096},
        "claude-3": {"cost": 0.015, "vision": True, "context": 100000}
    }
    
    candidates = []
    for name, specs in models.items():
        if requirements.get("budget") and specs["cost"] > requirements["budget"]:
            continue
        if requirements.get("need_vision") and not specs["vision"]:
            continue
        if requirements.get("min_context") and specs["context"] < requirements["min_context"]:
            continue
        candidates.append((name, specs))
    
    if not candidates:
        return None
    
    candidates.sort(key=lambda x: x[1]["cost"])
    return candidates[0][0]

# 测试
test_cases = [
    {"budget": 0.01, "need_vision": False, "min_context": 4000},
    {"budget": 0.05, "need_vision": True, "min_context": 8000},
]

for i, req in enumerate(test_cases, 1):
    best = select_best_model(req)
    print(f"场景{i}: {req}")
    print(f"  推荐: {best if best else '无符合条件的模型'}")

print("\n" + "="*50)
print("Day 01 控制流示例运行完成！")
print("="*50)