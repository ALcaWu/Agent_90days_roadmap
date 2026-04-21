# -*- coding: utf-8 -*-
"""
================================================================================
Day 13 - 06_Parser工厂模式
================================================================================
本文件演示 Parser 工厂模式（Parser Factory Pattern）的完整实现，包括：
  1. ParserConfig 数据类：统一描述 Parser 的配置参数
  2. ParserFactory 工厂类：注册 / 获取 Parser，支持运行时扩展
  3. 与 LangChain LCEL 的无缝集成
  4. 真实场景：多业务场景的 Parser 切换

核心理解：
  工厂模式的本质：将"创建对象"的逻辑从调用方分离。
  当你有多个相似但不同的 Parser 时，用工厂模式可以：
    - 避免大量 if-elif 分支
    - 集中管理 Parser 配置
    - 运行时动态注册新 Parser（插件化）
================================================================================
"""

from typing import Dict, Any, Type
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser, BaseOutputParser
from langchain_core.prompts import PromptTemplate


# ==============================================================================
# 一、为什么需要 Parser 工厂？
# ==============================================================================
"""
没有工厂时，每增加一个 Parser 就要加 if-elif 分支：

  if parser_type == "movie":
      p = PydanticOutputParser(pydantic_object=MovieReview)
  elif parser_type == "order":
      p = PydanticOutputParser(pydantic_object=OrderStatus)
  elif parser_type == "resume":
      p = PydanticOutputParser(pydantic_object=Resume)
  ...  # 分支越来越多，难以维护

工厂模式后：所有 Parser 在一个地方注册，按名字获取：

  parser = ParserFactory.get("movie")  # 一行搞定
"""

print("=" * 60)
print("一、为什么需要 Parser 工厂？")
print("=" * 60)
print("""
业务场景：同一套 LLM 链路，需要支持多种输出格式。

方案A：if-elif（反模式）
  - 分支多，难以维护
  - 每次新增 Parser 都要改核心逻辑
  - 违反开闭原则（对扩展开放，对修改封闭）

方案B：工厂模式（推荐）
  - 所有 Parser 在工厂注册
  - 按名字获取，新增 Parser 只需注册
  - 调用方无需知道具体 Parser 类名
""")


# ==============================================================================
# 二、定义业务模型（用于工厂演示）
# ==============================================================================

class MovieReview(BaseModel):
    """影评模型"""
    title: str = Field(description="电影名称")
    rating: float = Field(ge=0, le=10, description="评分 0-10")
    summary: str = Field(max_length=200, description="影评摘要")


class OrderStatus(BaseModel):
    """订单模型"""
    order_id: str = Field(description="订单编号")
    status: str = Field(description="订单状态")
    amount: float = Field(gt=0, description="金额")


class NewsItem(BaseModel):
    """新闻条目模型"""
    headline: str = Field(description="新闻标题")
    category: str = Field(description="分类")


# ==============================================================================
# 三、ParserConfig 数据类：描述 Parser 的元信息
# ==============================================================================

@dataclass
class ParserConfig:
    """
    Parser 配置数据类：用数据描述 Parser，而非用代码。

    dataclass vs 普通类：
      - 自动生成 __init__, __repr__, __eq__
      - 代码更简洁，适合纯数据容器
      - field() 支持默认值配置
    """
    name: str                          # Parser 唯一名称（工厂的 key）
    model_class: Type[BaseModel]        # Pydantic 模型类（用于构造 PydanticOutputParser）
    description: str = ""              # Parser 描述（用于文档和调试）
    # 自定义格式指令（可选，不提供则用 PydanticOutputParser 默认生成的）
    custom_instructions: str = ""
    # 额外元数据（可用于存储业务参数，如超时时间、重试次数等）
    metadata: Dict[str, Any] = field(default_factory=dict)


# ==============================================================================
# 四、ParserFactory：Parser 注册与获取
# ==============================================================================

class ParserFactory:
    """
    Parser 工厂：根据配置动态创建 Parser 实例。

    设计要点：
      - 类变量 _registry：存储所有已注册的 Parser 配置
      - @classmethod：工厂不需要实例化
      - get()：根据名字查找配置，创建对应的 Parser
      - register()：运行时注册新 Parser
      - list_parsers()：查看所有可用 Parser（调试用）
    """

    # 类变量：所有已注册的 Parser 配置 {name: ParserConfig}
    _registry: Dict[str, ParserConfig] = {}

    @classmethod
    def register(cls, config: ParserConfig) -> None:
        """
        注册一个 Parser 配置。

        使用示例：
          ParserFactory.register(ParserConfig(
              name="movie",
              model_class=MovieReview,
              description="影评解析器"
          ))
        """
        if config.name in cls._registry:
            # 已有同名 Parser，覆盖（允许热更新）
            print(f"  ⚠️ Parser '{config.name}' 已存在，将被覆盖")
        cls._registry[config.name] = config
        print(f"  ✅ Parser '{config.name}' 注册成功")

    @classmethod
    def get(cls, name: str) -> "ParserWithPrompt":
        """
        根据名字获取 Parser。

        返回的不是原始的 PydanticOutputParser，而是包装后的 ParserWithPrompt：
          ParserWithPrompt 包含 parser + prompt_template，
          调用方可以直接拿到完整可用的 chain。
        """
        config = cls._registry.get(name)
        if not config:
            available = list(cls._registry.keys())
            raise ValueError(
                f"未知的 Parser: '{name}'\n"
                f"可选: {available}"
            )
        return ParserWithPrompt.from_config(config)

    @classmethod
    def list_parsers(cls) -> Dict[str, ParserConfig]:
        """列出所有已注册的 Parser（用于调试和文档）"""
        return dict(cls._registry)

    @classmethod
    def has(cls, name: str) -> bool:
        """检查某个 Parser 是否已注册"""
        return name in cls._registry

    @classmethod
    def unregister(cls, name: str) -> bool:
        """取消注册（用于测试或热卸载）"""
        if name in cls._registry:
            del cls._registry[name]
            return True
        return False


# ==============================================================================
# 五、ParserWithPrompt：Parser + Prompt 的组合封装
# ==============================================================================

class ParserWithPrompt:
    """
    Parser + Prompt 组合封装：包含 Parser 本身及其配套的 PromptTemplate。

    为什么需要这个封装？
      - 一个 Parser 总是需要配套的 Prompt 才能工作
      - 如果只返回 PydanticOutputParser，调用方还需要自己写 Prompt
      - 封装后，调用方直接拿到 Prompt | Parser 的组合，零配置使用

    工厂 get() 返回的是这个类的实例，而非原始 Parser。
    """

    def __init__(
        self,
        config: ParserConfig,
        parser: BaseOutputParser,
        prompt: PromptTemplate,
    ):
        self.config = config
        self.parser = parser
        self.prompt = prompt

    @classmethod
    def from_config(cls, config: ParserConfig) -> "ParserWithPrompt":
        """从配置构造 ParserWithPrompt"""
        # 构造 PydanticOutputParser
        parser = PydanticOutputParser(pydantic_object=config.model_class)

        # 构造 PromptTemplate（包含 format_instructions 占位符）
        instructions = (
            config.custom_instructions
            if config.custom_instructions
            else parser.get_format_instructions()
        )
        prompt = PromptTemplate.from_template(
            template="{input}\n{format_instructions}",
            partial_variables={"format_instructions": instructions},
        )

        return cls(config=config, parser=parser, prompt=prompt)

    def get_chain(self, model):
        """
        生成完整的 LCEL 链：prompt | model | parser
        调用方只需传入 model，即可得到完整可用的 chain。
        """
        return self.prompt | model | self.parser

    def invoke(self, input_text: str, model) -> BaseModel:
        """快捷方法：直接传入输入文本和模型，得到解析结果"""
        return self.get_chain(model).invoke({"input": input_text})


# ==============================================================================
# 六、工厂使用示例：注册 + 获取
# ==============================================================================

print("\n" + "=" * 60)
print("六、Parser 工厂使用示例")
print("=" * 60)

# 注册所有业务 Parser
print("\n[注册 Parser]")
ParserFactory.register(ParserConfig(
    name="movie",
    model_class=MovieReview,
    description="影评解析：提取电影名称、评分和摘要",
    metadata={"category": "entertainment"},
))

ParserFactory.register(ParserConfig(
    name="order",
    model_class=OrderStatus,
    description="订单状态解析：提取订单编号、状态和金额",
))

ParserFactory.register(ParserConfig(
    name="news",
    model_class=NewsItem,
    description="新闻解析：提取新闻标题和分类",
    # 自定义格式指令（覆盖默认生成）
    custom_instructions="请以简洁的新闻风格输出，包含标题和分类。",
))

# 列出所有已注册的 Parser
print("\n[已注册的 Parser]")
for name, cfg in ParserFactory.list_parsers().items():
    print(f"  - {name}: {cfg.description}")

# 按名字获取 Parser
print("\n[获取 Parser]")
parser_with_prompt = ParserFactory.get("movie")
print(f"Parser 名称: {parser_with_prompt.config.name}")
print(f"模型类: {parser_with_prompt.config.model_class.__name__}")
print(f"Prompt 模板: {parser_with_prompt.prompt.template}")

# 查看格式指令
print(f"\n[格式指令预览]")
print(parser_with_prompt.parser.get_format_instructions()[:200])


# ==============================================================================
# 七、运行时扩展：动态注册新 Parser（插件化）
# ==============================================================================

print("\n" + "=" * 60)
print("七、运行时扩展：动态注册新 Parser")
print("=" * 60)


# 定义一个新模型
class TaskItem(BaseModel):
    """任务解析模型"""
    title: str = Field(description="任务标题")
    priority: str = Field(description="优先级：高/中/低")
    deadline: str | None = Field(default=None, description="截止日期")


# 动态注册（无需修改工厂代码）
print("\n[动态注册新 Parser：task]")
ParserFactory.register(ParserConfig(
    name="task",
    model_class=TaskItem,
    description="任务解析：提取任务标题、优先级和截止日期",
))

# 立即可用
task_parser = ParserFactory.get("task")
print(f"✅ task Parser 已就绪，模型类: {task_parser.config.model_class.__name__}")
print(f"   可用 Parser 总数: {len(ParserFactory.list_parsers())}")


# ==============================================================================
# 八、模拟完整 Chain 调用（使用工厂获取的 Parser）
# ==============================================================================

print("\n" + "=" * 60)
print("八、工厂 Parser 完整 Chain 调用（模拟）")
print("=" * 60)


class MockModel:
    """模拟 LLM：根据 Parser 类型返回对应的 JSON"""
    def __init__(self):
        # 预定义各 Parser 对应的模拟输出
        self.responses = {
            "movie": '{"title": "流浪地球2", "rating": 8.8, "summary": "震撼的科幻巨制"}',
            "order": '{"order_id": "ORD-20260410", "status": "shipped", "amount": 299.5}',
            "news": '{"headline": "AI Agent 取得重大进展", "category": "科技"}',
            "task": '{"title": "完成报告", "priority": "高", "deadline": "2026-04-15"}',
        }

    def invoke(self, prompt_value):
        # 从 prompt 中推断 parser 类型（简化版）
        text = str(prompt_value)
        for name, response in self.responses.items():
            if name in text or "Movie" in text or "title" in text:
                return response
        return '{"title": "unknown"}'


print("\n[模拟 Chain 调用]")
mock_model = MockModel()

for parser_name in ["movie", "order", "task"]:
    parser_wp = ParserFactory.get(parser_name)
    chain = parser_wp.get_chain(mock_model)

    # 模拟输入
    test_input = {"input": f"请解析以下{parser_name}数据"}

    result = chain.invoke(test_input)
    print(f"\n  [{parser_name}]")
    print(f"    输入: {test_input['input']}")
    print(f"    结果类型: {type(result).__name__}")
    if hasattr(result, "title"):
        print(f"    title: {result.title}")


print("\n✅ 06_Parser工厂模式 演示完毕！")
print("\n💡 工厂模式的核心价值：")
print("   - 新增 Parser 只需注册，无需修改工厂代码（开闭原则）")
print("   - 所有 Parser 配置集中管理，便于文档和调试")
print("   - ParserWithPrompt 封装了 Parser + Prompt，调用方零配置使用")
