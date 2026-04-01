"""Day 02 代码示例：继承与多态"""

# ============================================
# 1. 基本继承
# ============================================

class BaseAgent:
    """Agent基类"""
    
    def __init__(self, name):
        self.name = name
    
    def process(self, input_text):
        raise NotImplementedError("子类必须实现此方法")


class ChatAgent(BaseAgent):
    """对话Agent"""
    
    def __init__(self, name, model="gpt-4"):
        super().__init__(name)
        self.model = model
    
    def process(self, input_text):
        return f"[ChatAgent:{self.name}] 回复: {input_text}"


class CodeAgent(BaseAgent):
    """代码Agent"""
    
    def process(self, input_text):
        return f"[CodeAgent:{self.name}] 生成代码: {input_text}"


print("=== 基本继承 ===")
chat = ChatAgent("聊天机器人", "gpt-4")
code = CodeAgent("程序员")
print(chat.process("你好"))
print(code.process("排序算法"))

# ============================================
# 2. 多态
# ============================================

def run_agent(agent: BaseAgent, text: str):
    return agent.process(text)


print("\n=== 多态 ===")
agents = [ChatAgent("助手"), CodeAgent("开发者")]
for agent in agents:
    print(run_agent(agent, "测试"))

# ============================================
# 3. Mixin多重继承
# ============================================

class LoggerMixin:
    def log(self, message):
        print(f"[LOG] {self.__class__.__name__}: {message}")


class CacheMixin:
    def __init__(self):
        self._cache = {}
    
    def get_cache(self, key):
        return self._cache.get(key)
    
    def set_cache(self, key, value):
        self._cache[key] = value


class SmartAgent(BaseAgent, LoggerMixin, CacheMixin):
    def __init__(self, name):
        super().__init__(name)
        CacheMixin.__init__(self)
    
    def process(self, input_text):
        cached = self.get_cache(input_text)
        if cached:
            self.log(f"缓存命中: {input_text}")
            return cached
        
        result = f"[SmartAgent] {input_text}"
        self.set_cache(input_text, result)
        self.log(f"处理完成: {input_text}")
        return result


print("\n=== Mixin多重继承 ===")
smart = SmartAgent("智能助手")
print(smart.process("hello"))
print(smart.process("hello"))  # 缓存命中

print("\n" + "="*50)
print("Day 02 继承与多态示例运行完成！")