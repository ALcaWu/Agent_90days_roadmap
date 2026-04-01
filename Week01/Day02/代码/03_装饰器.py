"""Day 02 代码示例：装饰器"""
import time
from functools import wraps

# ============================================
# 1. 基本装饰器
# ============================================

def timer(func):
    """计时装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"[{func.__name__}] 耗时: {elapsed:.3f}s")
        return result
    return wrapper


@timer
def slow_function():
    time.sleep(0.1)
    return "完成"


print("=== 基本装饰器 ===")
print(slow_function())

# ============================================
# 2. 带参数的装饰器
# ============================================

def retry(max_attempts=3):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"重试 {attempt + 1}/{max_attempts}")
        return wrapper
    return decorator


@retry(max_attempts=2)
def risky_call():
    import random
    if random.random() < 0.7:
        raise ValueError("随机失败")
    return "成功"


print("\n=== 带参数的装饰器 ===")
try:
    print(risky_call())
except ValueError:
    print("最终失败")

# ============================================
# 3. 类装饰器（单例）
# ============================================

def singleton(cls):
    """单例装饰器"""
    instances = {}
    
    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance


@singleton
class APIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        print(f"初始化: {api_key}")


print("\n=== 单例装饰器 ===")
c1 = APIClient("key1")
c2 = APIClient("key2")
print(f"同一实例: {c1 is c2}")

# ============================================
# 4. 内置装饰器
# ============================================

class Config:
    def __init__(self):
        self._temperature = 0.7
    
    @property
    def temperature(self):
        return self._temperature
    
    @temperature.setter
    def temperature(self, value):
        if not 0 <= value <= 2:
            raise ValueError("temperature必须在0-2之间")
        self._temperature = value
    
    @staticmethod
    def get_default():
        return {"model": "gpt-4"}
    
    @classmethod
    def from_env(cls):
        return cls()


print("\n=== 内置装饰器 ===")
cfg = Config()
print(f"temperature: {cfg.temperature}")
cfg.temperature = 0.5
print(f"修改后: {cfg.temperature}")
print(f"静态方法: {Config.get_default()}")

print("\n" + "="*50)
print("Day 02 装饰器示例运行完成！")