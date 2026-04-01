"""Day 02 代码示例：异常处理"""

# ============================================
# 1. 基本异常处理
# ============================================

def divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("错误: 除数不能为0")
        return None
    except TypeError as e:
        print(f"类型错误: {e}")
        return None
    else:
        print("计算成功")
        return result
    finally:
        print("执行完毕")


print("=== 基本异常处理 ===")
print(f"10/2 = {divide(10, 2)}")
print(f"10/0 = {divide(10, 0)}")

# ============================================
# 2. 自定义异常
# ============================================

class AgentError(Exception):
    """Agent基础异常"""
    pass


class TokenLimitError(AgentError):
    """Token超限异常"""
    def __init__(self, current, limit):
        self.current = current
        self.limit = limit
        super().__init__(f"Token超限: {current}/{limit}")


def validate_tokens(tokens, limit=4096):
    if tokens > limit:
        raise TokenLimitError(tokens, limit)
    return True


print("\n=== 自定义异常 ===")
try:
    validate_tokens(5000)
except TokenLimitError as e:
    print(f"捕获异常: {e}")

# ============================================
# 3. 上下文管理器
# ============================================

from contextlib import contextmanager

@contextmanager
def api_context(api_key):
    """API上下文管理器"""
    print("初始化连接...")
    client = {"api_key": api_key, "connected": True}
    try:
        yield client
    finally:
        print("关闭连接...")
        client["connected"] = False


print("\n=== 上下文管理器 ===")
with api_context("sk-xxx") as client:
    print(f"使用API: {client['api_key']}")

# ============================================
# 4. 实战：API调用错误处理
# ============================================

class APIError(Exception):
    pass


def call_api(prompt, max_retries=3):
    """带重试的API调用"""
    import random
    
    for attempt in range(max_retries):
        try:
            # 模拟API调用
            if random.random() < 0.5:
                raise ConnectionError("网络错误")
            
            return {"content": f"回复: {prompt}", "tokens": 100}
        
        except ConnectionError as e:
            print(f"尝试 {attempt + 1}/{max_retries}: {e}")
            if attempt == max_retries - 1:
                raise APIError(f"重试{max_retries}次后仍失败") from e


print("\n=== 实战：API错误处理 ===")
try:
    result = call_api("你好", max_retries=3)
    print(f"结果: {result}")
except APIError as e:
    print(f"最终失败: {e}")

print("\n" + "="*50)
print("Day 02 异常处理示例运行完成！")