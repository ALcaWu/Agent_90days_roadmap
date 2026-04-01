"""
Day 01 代码示例：Python基础语法 - 函数
学习目标：掌握函数定义、参数类型和Lambda表达式
"""

# ============================================
# 1. 函数基础
# ============================================

print("=== 函数基础 ===")

def greet(name):
    """问候函数"""
    return f"你好，{name}！欢迎学习Agent开发。"

message = greet("吴文杰")
print(message)

# 无返回值函数
def log_info(message, level="INFO"):
    print(f"[{level}] {message}")

log_info("开始学习Python")
log_info("这是一个警告", "WARN")

# 多返回值
def get_model_config():
    model = "gpt-4"
    temperature = 0.7
    max_tokens = 2048
    return model, temperature, max_tokens

model, temp, tokens = get_model_config()
print(f"\n模型配置: {model}, temperature={temp}, max_tokens={tokens}")

# ============================================
# 2. 参数类型
# ============================================

print("\n=== 参数类型 ===")

# 默认参数
def create_prompt(question, system="你是一个有帮助的助手。"):
    return f"系统: {system}\n用户: {question}"

print(create_prompt("什么是Agent？"))

# 可变位置参数
def calculate_total_cost(*costs):
    total = sum(costs)
    print(f"各项成本: {costs}")
    return total

total = calculate_total_cost(0.03, 0.02, 0.05)
print(f"总成本: ${total}")

# 可变关键字参数
def build_request(endpoint, **params):
    print(f"端点: {endpoint}")
    for key, value in params.items():
        print(f"  {key}: {value}")

build_request("/chat/completions", model="gpt-4", temperature=0.7)

# ============================================
# 3. Lambda表达式
# ============================================

print("\n=== Lambda表达式 ===")

square = lambda x: x ** 2
print(f"5的平方: {square(5)}")

add = lambda a, b: a + b
print(f"3 + 5 = {add(3, 5)}")

# 与sorted配合
models = [
    {"name": "GPT-4", "cost": 0.03},
    {"name": "GPT-3.5", "cost": 0.002},
    {"name": "Claude-3", "cost": 0.015}
]

sorted_by_cost = sorted(models, key=lambda x: x["cost"])
print("\n按成本排序:")
for m in sorted_by_cost:
    print(f"  {m['name']}: ${m['cost']}")

# 与filter配合
expensive = list(filter(lambda x: x["cost"] > 0.01, models))
print(f"\n成本>$0.01: {[m['name'] for m in expensive]}")

# 与map配合
names = list(map(lambda x: x["name"].upper(), models))
print(f"模型名称: {names}")

# ============================================
# 4. 闭包
# ============================================

print("\n=== 闭包 ===")

def create_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

counter = create_counter()
print(f"计数: {counter()}")
print(f"计数: {counter()}")
print(f"计数: {counter()}")

# 配置工厂
def create_api_client(base_url, api_key):
    def request(endpoint, method="GET"):
        print(f"请求: {method} {base_url}{endpoint}")
        print(f"认证: {api_key[:10]}...")
        return {"status": "success"}
    return request

client = create_api_client("https://api.openai.com/v1", "sk-openai-key-xxx")
client("/chat/completions", "POST")

# ============================================
# 5. 实战：提示词模板
# ============================================

print("\n=== 实战：提示词模板 ===")

def create_prompt_template(system_prompt):
    def format_prompt(user_input, **context):
        prompt = f"系统: {system_prompt}\n用户: {user_input}"
        if context:
            prompt += f"\n上下文: {context}"
        return prompt
    return format_prompt

code_assistant = create_prompt_template("你是一个专业的编程助手。")
print(code_assistant("如何使用LangChain？", language="Python"))

# ============================================
# 6. 实战：API调用封装
# ============================================

print("\n=== 实战：API调用封装 ===")

def create_chat_function(model="gpt-3.5-turbo", temperature=0.7):
    def chat(message, **overrides):
        config = {
            "model": model,
            "temperature": temperature,
            "message": message
        }
        config.update(overrides)
        print(f"配置: {config}")
        return {"response": f"AI回复: {message[:20]}..."}
    return chat

gpt4_chat = create_chat_function("gpt-4", 0.5)
gpt4_chat("介绍一下Agent开发")

print("\n" + "="*50)
print("Day 01 函数基础示例运行完成！")
print("="*50)