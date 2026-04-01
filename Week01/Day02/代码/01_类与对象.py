"""Day 02 代码示例：类与对象"""

# ============================================
# 1. 基本类定义
# ============================================

class Agent:
    """Agent基类"""
    
    def __init__(self, name, model="gpt-4"):
        self.name = name
        self.model = model
        self.history = []
    
    def chat(self, message):
        self.history.append({"role": "user", "content": message})
        return f"[{self.name}] 收到: {message}"
    
    def get_history(self):
        return self.history


print("=== 基本类定义 ===")
agent = Agent("助手A", "gpt-3.5-turbo")
print(agent.chat("你好"))
print(f"历史记录: {agent.get_history()}")

# ============================================
# 2. 类属性 vs 实例属性
# ============================================

class ModelConfig:
    # 类属性（共享）
    default_temperature = 0.7
    supported_models = ["gpt-4", "gpt-3.5-turbo", "claude-3"]
    
    def __init__(self, model):
        # 实例属性（独立）
        self.model = model
        self.temperature = self.default_temperature


print("\n=== 类属性 vs 实例属性 ===")
config1 = ModelConfig("gpt-4")
config2 = ModelConfig("claude-3")
print(f"config1.model: {config1.model}")
print(f"config2.model: {config2.model}")
print(f"共享温度: {config1.temperature}")

# ============================================
# 3. 特殊方法
# ============================================

class TokenCounter:
    def __init__(self, tokens=0):
        self.tokens = tokens
    
    def __str__(self):
        return f"TokenCounter(tokens={self.tokens})"
    
    def __add__(self, other):
        return TokenCounter(self.tokens + other.tokens)
    
    def __len__(self):
        return self.tokens


print("\n=== 特殊方法 ===")
c1 = TokenCounter(100)
c2 = TokenCounter(50)
print(f"str: {str(c1)}")
print(f"相加: {c1 + c2}")
print(f"长度: {len(c1)}")

print("\n" + "="*50)
print("Day 02 类与对象示例运行完成！")