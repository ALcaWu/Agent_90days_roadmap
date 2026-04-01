# Day 01：Python基础语法

> 学习日期：2026-03-30
> 学习时长：2-3小时
> 学习目标：掌握Python核心语法，为AI开发打下坚实基础

---

## 一、变量与数据类型

### 1.1 变量定义

Python是动态类型语言，变量无需声明类型，直接赋值即可：

```python
# 基本变量定义
name = "吴文杰"
age = 25
height = 1.75
is_developer = True

# 查看变量类型
print(type(name))        # <class 'str'>
print(type(age))         # <class 'int'>
print(type(height))      # <class 'float'>
print(type(is_developer)) # <class 'bool'>
```

### 1.2 数据类型详解

#### 字符串（String）

```python
# 字符串定义
single_quote = 'Hello'
double_quote = "World"
multi_line = """
这是一个
多行字符串
"""

# 字符串操作
text = "Agent Development"
print(text.upper())          # AGENT DEVELOPMENT
print(text.lower())          # agent development
print(text.split())          # ['Agent', 'Development']
print(text.replace("Agent", "AI"))  # AI Development

# f-string格式化（AI开发常用）
model = "GPT-4"
tokens = 1000
print(f"使用模型：{model}，消耗Token：{tokens}")

# 字符串拼接
api_endpoint = "https://api.openai.com" + "/v1/chat/completions"
```

#### 数值类型

```python
# 整数与浮点数
int_num = 42
float_num = 3.14159

# 数值运算
print(10 + 3)    # 加法：13
print(10 - 3)    # 减法：7
print(10 * 3)    # 乘法：30
print(10 / 3)    # 除法：3.333...
print(10 // 3)   # 整除：3
print(10 % 3)    # 取余：1
print(2 ** 10)   # 幂运算：1024

# AI开发中的数值计算
temperature = 0.7
max_tokens = 2048
cost_per_1k_tokens = 0.002
total_cost = (max_tokens / 1000) * cost_per_1k_tokens
```

#### 布尔类型

```python
# 布尔值
is_valid = True
is_empty = False

# 比较运算符返回布尔值
print(5 > 3)   # True
print(5 == 3)  # False
print(5 != 3)  # True

# 逻辑运算
has_api_key = True
has_model = False
print(has_api_key and has_model)  # False
print(has_api_key or has_model)   # True
print(not has_model)              # True
```

### 1.3 数据结构

#### 列表（List）- 最常用

```python
# 列表定义
models = ["GPT-4", "Claude", "Gemini"]
print(models[0])      # GPT-4
print(models[-1])     # Gemini（倒数第一个）
print(len(models))    # 3

# 列表操作
models.append("Llama")        # 添加元素
models.remove("Gemini")       # 删除元素
models.insert(0, "GPT-3.5")   # 插入元素

# 列表切片
numbers = [0, 1, 2, 3, 4, 5]
print(numbers[1:4])    # [1, 2, 3]
print(numbers[:3])     # [0, 1, 2]
print(numbers[3:])     # [3, 4, 5]
print(numbers[::2])    # [0, 2, 4]（步长为2）

# 列表推导式（AI开发常用）
squares = [x**2 for x in range(10)]
filtered = [x for x in range(10) if x > 5]

# 嵌套列表
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
```

#### 字典（Dictionary）- API数据处理核心

```python
# 字典定义
config = {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2048
}

# 访问值
print(config["model"])           # gpt-4
print(config.get("model"))       # gpt-4（推荐方式）
print(config.get("api_key", "无")) # 无（默认值）

# 修改与添加
config["temperature"] = 0.5      # 修改
config["api_key"] = "sk-xxx"     # 添加

# 遍历字典
for key, value in config.items():
    print(f"{key}: {value}")

# 字典推导式
squared = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# 嵌套字典（API响应常见格式）
api_response = {
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": "Hello!"
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 5,
        "total_tokens": 15
    }
}

# 访问嵌套数据
content = api_response["choices"][0]["message"]["content"]
```

#### 元组（Tuple）- 不可变序列

```python
# 元组定义
coordinates = (10, 20)
rgb_color = (255, 128, 0)

# 元组解包
x, y = coordinates
r, g, b = rgb_color

# 函数返回多值时常用元组
def get_model_info():
    return "gpt-4", 0.7, 2048

model, temp, tokens = get_model_info()
```

#### 集合（Set）- 去重与集合运算

```python
# 集合定义
unique_models = {"GPT-4", "Claude", "Gemini"}

# 去重
duplicates = [1, 1, 2, 2, 3, 3]
unique = list(set(duplicates))  # [1, 2, 3]

# 集合运算
a = {1, 2, 3}
b = {2, 3, 4}
print(a | b)  # 并集：{1, 2, 3, 4}
print(a & b)  # 交集：{2, 3}
print(a - b)  # 差集：{1}
```

---

## 二、控制流

### 2.1 条件语句

```python
# if-elif-else结构
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "D"

# 三元表达式（简洁写法）
status = "valid" if score >= 60 else "invalid"

# 多条件判断
has_api_key = True
has_quota = False

if has_api_key and has_quota:
    print("可以调用API")
elif has_api_key:
    print("API额度不足")
else:
    print("请先配置API Key")

# 检查值是否存在
allowed_models = ["gpt-4", "gpt-3.5-turbo", "claude-3"]
model = "gpt-4"

if model in allowed_models:
    print(f"{model} 是支持的模型")
```

### 2.2 循环语句

#### for循环

```python
# 遍历列表
models = ["GPT-4", "Claude", "Gemini"]
for model in models:
    print(f"可用模型：{model}")

# 遍历范围
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4

# 带索引遍历
for index, model in enumerate(models):
    print(f"{index}: {model}")

# 遍历字典
config = {"model": "gpt-4", "temperature": 0.7}
for key, value in config.items():
    print(f"{key} = {value}")

# 嵌套循环
for i in range(3):
    for j in range(3):
        print(f"({i}, {j})", end=" ")
    print()
```

#### while循环

```python
# 基本while循环
count = 0
while count < 5:
    print(count)
    count += 1

# 带条件的循环（API重试场景）
max_retries = 3
retry_count = 0

while retry_count < max_retries:
    # 模拟API调用
    success = False  # 假设调用失败
    
    if success:
        print("调用成功")
        break
    else:
        retry_count += 1
        print(f"重试 {retry_count}/{max_retries}")
```

#### 循环控制

```python
# break - 跳出循环
for i in range(10):
    if i == 5:
        break
    print(i)  # 输出 0-4

# continue - 跳过当前迭代
for i in range(10):
    if i % 2 == 0:
        continue
    print(i)  # 输出奇数 1, 3, 5, 7, 9

# else子句（循环正常结束时执行）
for i in range(5):
    print(i)
else:
    print("循环完成")
```

---

## 三、函数定义与调用

### 3.1 基本函数

```python
# 定义函数
def greet(name):
    """问候函数"""
    return f"你好，{name}！"

# 调用函数
message = greet("吴文杰")
print(message)

# 无返回值函数
def log_info(message):
    print(f"[INFO] {message}")
    # 隐式返回 None

# 多返回值
def get_model_config():
    model = "gpt-4"
    temperature = 0.7
    max_tokens = 2048
    return model, temperature, max_tokens

# 解包返回值
m, t, tk = get_model_config()
```

### 3.2 参数类型

```python
# 位置参数
def call_api(endpoint, method):
    print(f"请求 {method} {endpoint}")

call_api("/chat", "POST")

# 关键字参数
call_api(method="GET", endpoint="/models")

# 默认参数
def create_completion(prompt, model="gpt-3.5-turbo", temperature=0.7):
    return {
        "prompt": prompt,
        "model": model,
        "temperature": temperature
    }

result = create_completion("Hello")
result2 = create_completion("Hello", model="gpt-4", temperature=0.5)

# 可变位置参数 (*args)
def sum_all(*numbers):
    return sum(numbers)

print(sum_all(1, 2, 3, 4, 5))  # 15

# 可变关键字参数 (**kwargs)
def build_config(**options):
    for key, value in options.items():
        print(f"{key}: {value}")

build_config(model="gpt-4", temperature=0.7, max_tokens=2048)

# 组合使用（AI开发常见模式）
def api_call(endpoint, method="GET", *args, **kwargs):
    print(f"调用 {method} {endpoint}")
    if args:
        print(f"位置参数：{args}")
    if kwargs:
        print(f"关键字参数：{kwargs}")
```

### 3.3 Lambda表达式

```python
# 基本语法
square = lambda x: x ** 2
print(square(5))  # 25

# 多参数
add = lambda a, b: a + b
print(add(3, 5))  # 8

# 与内置函数配合使用
models = [
    {"name": "GPT-4", "cost": 0.03},
    {"name": "GPT-3.5", "cost": 0.002},
    {"name": "Claude", "cost": 0.015}
]

# 按成本排序
sorted_models = sorted(models, key=lambda x: x["cost"])

# 过滤
expensive = list(filter(lambda x: x["cost"] > 0.01, models))

# 映射
names = list(map(lambda x: x["name"], models))
```

---

## 四、模块与包管理

### 4.1 导入模块

```python
# 导入整个模块
import os
print(os.getcwd())

# 导入特定函数
from datetime import datetime, timedelta
print(datetime.now())

# 别名导入
import numpy as np
import pandas as pd

# 导入所有（不推荐）
from os import *
```

### 4.2 常用内置模块

```python
import os
import sys
import json
import datetime
import pathlib

# os模块 - 操作系统接口
print(os.getcwd())           # 当前工作目录
print(os.listdir("."))       # 列出目录内容
os.makedirs("new_dir", exist_ok=True)  # 创建目录

# json模块 - JSON处理（AI开发必备）
data = {"model": "gpt-4", "tokens": 1000}
json_str = json.dumps(data, indent=2)  # 字典转JSON字符串
parsed = json.loads(json_str)          # JSON字符串转字典

# pathlib模块 - 现代路径操作
from pathlib import Path
project_path = Path("D:/AgentDeveloperCourse")
print(project_path.exists())
print(project_path / "Week01" / "Day01")  # 路径拼接

# datetime模块 - 时间处理
now = datetime.datetime.now()
formatted = now.strftime("%Y-%m-%d %H:%M:%S")
```

### 4.3 第三方包管理

```bash
# 安装包
pip install openai
pip install langchain
pip install requests

# 指定版本
pip install openai==1.0.0

# 从requirements.txt安装
pip install -r requirements.txt

# 卸载包
pip uninstall openai

# 查看已安装
pip list
pip freeze > requirements.txt
```

---

## 五、AI开发实战：调用OpenAI API

### 5.1 基础调用示例

```python
import os
from openai import OpenAI

# 设置API Key
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 发送请求
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "你是一个有帮助的助手。"},
        {"role": "user", "content": "介绍一下Python的优点"}
    ],
    temperature=0.7,
    max_tokens=500
)

# 获取响应
print(response.choices[0].message.content)
print(f"消耗Token: {response.usage.total_tokens}")
```

### 5.2 错误处理

```python
from openai import OpenAI, APIError, RateLimitError, APIConnectionError

client = OpenAI()

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}]
    )
except RateLimitError:
    print("请求频率超限，请稍后重试")
except APIConnectionError:
    print("网络连接失败")
except APIError as e:
    print(f"API错误: {e}")
```

---

## 六、今日练习

### 练习1：数据结构操作

```python
# 创建一个包含多个AI模型信息的列表
models = [
    {"name": "GPT-4", "provider": "OpenAI", "cost_per_1k": 0.03},
    {"name": "Claude-3", "provider": "Anthropic", "cost_per_1k": 0.015},
    {"name": "Gemini Pro", "provider": "Google", "cost_per_1k": 0.001},
]

# 1. 找出成本最低的模型
cheapest = min(models, key=lambda x: x["cost_per_1k"])

# 2. 按提供商分组
from collections import defaultdict
grouped = defaultdict(list)
for model in models:
    grouped[model["provider"]].append(model["name"])

# 3. 计算总成本（假设每个模型调用1000次）
total_cost = sum(m["cost_per_1k"] * 1000 for m in models)
```

### 练习2：配置文件处理

```python
import json

# 模拟API配置
config = {
    "api_key": "sk-your-api-key",
    "model": "gpt-4",
    "parameters": {
        "temperature": 0.7,
        "max_tokens": 2048,
        "top_p": 1.0
    },
    "allowed_models": ["gpt-4", "gpt-3.5-turbo", "claude-3"]
}

# 保存配置
with open("config.json", "w") as f:
    json.dump(config, f, indent=2)

# 读取配置
with open("config.json", "r") as f:
    loaded_config = json.load(f)

# 验证配置
def validate_config(cfg):
    required_keys = ["api_key", "model", "parameters"]
    for key in required_keys:
        if key not in cfg:
            return False, f"缺少配置项: {key}"
    
    if cfg["model"] not in cfg["allowed_models"]:
        return False, f"不支持的模型: {cfg['model']}"
    
    return True, "配置有效"

is_valid, message = validate_config(loaded_config)
print(message)
```

---

## 七、学习检查清单

- [ ] 理解Python变量与动态类型
- [ ] 掌握字符串、数值、布尔类型的操作
- [ ] 熟练使用列表和字典（重点）
- [ ] 能够编写条件判断和循环语句
- [ ] 理解函数定义与参数类型
- [ ] 掌握模块导入与常用内置模块
- [ ] 了解JSON数据处理
- [ ] 完成今日练习题

---

## 八、明日预告

Day 02 将学习：
- 面向对象编程（类、继承、多态）
- 装饰器的原理与应用
- 异常处理机制
- 文件操作与序列化

---

> 学习建议：今日内容是Python基础的核心，务必确保理解透彻。建议动手运行所有代码示例，并尝试修改参数观察输出变化。