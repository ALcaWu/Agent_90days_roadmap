"""Day 02 练习题：面向对象编程"""

# ============================================
# 练习1：实现单例配置管理器
# ============================================

class ConfigManager:
    """单例配置管理器"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = {}
        return cls._instance
    
    def set(self, key, value):
        self._config[key] = value
    
    def get(self, key, default=None):
        return self._config.get(key, default)


print("=== 练习1：单例配置管理器 ===")
cm1 = ConfigManager()
cm1.set("model", "gpt-4")

cm2 = ConfigManager()
print(f"cm1 is cm2: {cm1 is cm2}")  # True
print(f"从cm2获取: {cm2.get('model')}")  # gpt-4

# ============================================
# 练习2：实现带缓存的Agent
# ============================================

class CachedAgent:
    """带缓存的Agent"""
    
    def __init__(self, name):
        self.name = name
        self._cache = {}
        self._hit_count = 0
        self._total_count = 0
    
    def chat(self, message):
        self._total_count += 1
        
        if message in self._cache:
            self._hit_count += 1
            print(f"缓存命中 ({self.hit_rate:.1%})")
            return self._cache[message]
        
        # 模拟API调用
        response = f"[{self.name}] 回复: {message}"
        self._cache[message] = response
        return response
    
    @property
    def hit_rate(self):
        if self._total_count == 0:
            return 0
        return self._hit_count / self._total_count


print("\n=== 练习2：带缓存的Agent ===")
agent = CachedAgent("助手")
print(agent.chat("你好"))
print(agent.chat("hello"))
print(agent.chat("你好"))  # 缓存命中
print(f"缓存命中率: {agent.hit_rate:.1%}")

# ============================================
# 练习3：实现计时装饰器
# ============================================

import time
from functools import wraps

def measure_time(func):
    """计时装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[{func.__name__}] 耗时: {elapsed:.6f}s")
        return result
    return wrapper


@measure_time
def process_data(n):
    """模拟数据处理"""
    return sum(i ** 2 for i in range(n))


print("\n=== 练习3：计时装饰器 ===")
result = process_data(100000)
print(f"结果: {result}")

# ============================================
# 练习4：实现链式Agent
# ============================================

class Pipeline:
    """链式处理管道"""
    
    def __init__(self):
        self._steps = []
    
    def add(self, step):
        """添加处理步骤"""
        self._steps.append(step)
        return self  # 返回self支持链式调用
    
    def run(self, input_data):
        """依次执行所有步骤"""
        result = input_data
        for step in self._steps:
            result = step(result)
        return result


print("\n=== 练习4：链式Agent ===")

def step1(text):
    return text.strip().lower()

def step2(text):
    return text.replace(" ", "_")

def step3(text):
    return f"processed_{text}"


pipeline = Pipeline()
pipeline.add(step1).add(step2).add(step3)
result = pipeline.run("  Hello World  ")
print(f"链式处理结果: {result}")

# ============================================
# 练习5：实现验证器类
# ============================================

class Validator:
    """配置验证器"""
    
    @staticmethod
    def validate_model(model, allowed):
        if model not in allowed:
            raise ValueError(f"不支持的模型: {model}")
        return True
    
    @staticmethod
    def validate_temperature(temp):
        if not 0 <= temp <= 2:
            raise ValueError(f"temperature必须在0-2之间: {temp}")
        return True
    
    @classmethod
    def validate_config(cls, config):
        """验证完整配置"""
        cls.validate_model(config.get("model"), ["gpt-4", "gpt-3.5-turbo"])
        cls.validate_temperature(config.get("temperature", 0.7))
        return True


print("\n=== 练习5：验证器类 ===")

configs = [
    {"model": "gpt-4", "temperature": 0.7},
    {"model": "invalid", "temperature": 0.7},
]

for cfg in configs:
    try:
        Validator.validate_config(cfg)
        print(f"配置有效: {cfg}")
    except ValueError as e:
        print(f"配置无效: {e}")

print("\n" + "="*50)
print("Day 02 练习题运行完成！")