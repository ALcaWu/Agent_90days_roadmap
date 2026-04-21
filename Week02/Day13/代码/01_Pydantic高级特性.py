# -*- coding: utf-8 -*-
"""
================================================================================
Day 13 - 01_Pydantic高级特性
================================================================================
本文件演示 Pydantic v2 的核心高级特性，为理解 LangChain 的 PydanticOutputParser 打基础。

涵盖内容：
  1. Field 高级约束（min_length / ge / le / gt / lt / max_length）
  2. field_validator 字段验证器（mode="before"/"after"，输入预处理）
  3. model_validator 模型级验证器（跨字段关联校验）
  4. 嵌套模型（自动递归验证子模型）
  5. 枚举类型、默认值、computed_field 计算字段
  6. model_config 配置（ConfigDict）
  7. 综合示例：构建可序列化配置模型

依赖：pydantic>=2.0
================================================================================
"""

from pydantic import (
    BaseModel,           # Pydantic 模型基类，所有自定义模型继承它
    Field,               # 字段约束与元数据定义
    field_validator,     # 单字段验证器，对输入值做预处理（before）或后验（after）
    model_validator,     # 模型级验证器，可访问所有字段进行关联校验
    ConfigDict,          # Pydantic v2 配置对象，替代旧的 model_config = {...}
    computed_field,      # 计算字段装饰器，根据其他字段自动生成新字段
)
from typing import List, Optional   # 类型注解
from datetime import date            # 日期类型
from enum import Enum                # 枚举类型


# ==============================================================================
# 一、枚举类型 + Field 基础约束
# ==============================================================================

# 定义任务优先级枚举，限制字段只能取 HIGH/MEDIUM/LOW 三个值
# 如果 LLM 输出 "priority": "高"，Pydantic 会自动映射到 Priority.HIGH
class Priority(Enum):
    HIGH   = "高"
    MEDIUM = "中"
    LOW    = "低"


class Task(BaseModel):
    """
    任务模型，演示 Field 的各种约束参数。

    Field 常用参数说明：
      ...          ：省略号表示必填字段（等价于 ellipsis=...）
      default      ：默认值，当字段未提供时使用
      default_factory：工厂函数，适合可变默认值（如 list/dict），避免共享引用问题
      ge/le/gt/lt  ：数值比较约束（greater-equal / less-equal / greater-than / less-than）
      min_length/max_length：字符串或列表的长度约束
      description  ：字段描述，会被 PydanticOutputParser 用作格式指令给 LLM
    """
    # 必填字段，限制长度 1~100
    title: str = Field(..., min_length=1, max_length=100)

    # 默认值为 MEDIUM，可选字段
    priority: Priority = Field(default=Priority.MEDIUM)

    # 使用 default_factory=list 创建空列表（避免多实例共享同一列表对象）
    # 最多允许 10 个标签
    tags: List[str] = Field(default_factory=list, max_length=10)

    # 可选日期字段，默认 None
    deadline: Optional[date] = None

    # 布尔字段，默认 False（未完成）
    is_completed: bool = Field(default=False)

    @field_validator("tags", mode="before")
    @classmethod
    def split_tags_from_string(cls, v):
        """
        将字符串 "tag1, tag2" 自动拆分为列表 ["tag1", "tag2"]。
        mode="before" 表示在 Pydantic 类型转换之前执行，用于数据预处理。
        返回值会继续经过类型验证（如 List[str] 约束）。
        """
        if isinstance(v, str):
            # 按逗号拆分，去除两端空格，丢弃空字符串
            return [t.strip() for t in v.split(",") if t.strip()]
        # 如果不是字符串，直接返回（交给后续验证器处理）
        return v


# ----- 示例调用 -----
# 传入 tags 字符串，会被 split_tags_from_string 自动拆分
task1 = Task(title="完成任务", tags="coding, test, docs", priority=Priority.HIGH)
print("=== Task 模型验证 ===")
print("title:", task1.title)
print("tags:", task1.tags)


# ============================================================================
# 二、嵌套模型（自动递归验证子模型）
# ==============================================================================

class Address(BaseModel):
    """地址模型，嵌套在 Person 中使用"""
    city: str
    street: str
    # 邮政编码，限制长度 6~10 位（支持中国/美国等不同格式）
    zip_code: str = Field(min_length=6, max_length=10)


class Person(BaseModel):
    """
    人物模型，演示嵌套和 field_validator 容错处理。
    Pydantic 会自动将 address 字典转换为 Address 子模型（递归验证）。
    """
    name: str
    # 年龄限制在 0~150 之间
    age: int = Field(ge=0, le=150)
    # 嵌套 Address，Pydantic 收到 dict 时自动调用 Address.model_validate
    address: Address

    @field_validator("age", mode="before")
    @classmethod
    def coerce_age_to_int(cls, v):
        """
        容错处理：支持 "28岁"、"age: 28" 等格式，自动提取数字。
        这样即使 LLM 输出自然语言格式的年龄，模型也能正确解析。
        """
        if isinstance(v, str):
            import re
            # 匹配连续数字
            m = re.search(r"\d+", v)
            if m:
                return int(m.group())
        return v


person = Person(
    name="张三",
    age="28岁",  # 字符串格式，会被 coerce_age_to_int 转为 int
    address={"city": "北京", "street": "中关村", "zip_code": "100000"}
)
print("\n=== 嵌套模型 ===")
print("姓名:", person.name, "年龄:", person.age)
print("地址:", person.address.city, person.address.street)


# ==============================================================================
# 三、计算字段 computed_field（自动派生，无需存储）
# ==============================================================================

class Order(BaseModel):
    """
    订单模型，演示 @computed_field 装饰器。
    计算字段：根据 unit_price 和 quantity 自动派生 total_price 和 summary。
    这些字段不存储在模型内部，只在访问时动态计算。
    """
    # 商品列表，至少 1 个
    items: List[str] = Field(min_length=1)
    # 单价，必须 > 0
    unit_price: float = Field(gt=0)
    # 数量，必须 >= 1
    quantity: int = Field(ge=1)

    @computed_field
    @property
    def total_price(self) -> float:
        """总价 = 单价 × 数量，每次访问时实时计算"""
        return self.unit_price * self.quantity

    @computed_field
    @property
    def summary(self) -> str:
        """生成订单摘要字符串，供打印或日志使用"""
        sep = ", "
        return sep.join(self.items) + " x " + str(self.quantity) + " = " + str(self.total_price) + "\u5143"


order = Order(items=["Python书籍", "鼠标"], unit_price=99.5, quantity=2)
print("\n=== 计算字段 ===")
print("总价:", order.total_price)
print("摘要:", order.summary)


# ==============================================================================
# 四、model_config 配置（ConfigDict）
# ==============================================================================

class Product(BaseModel):
    """商品模型，演示 ConfigDict 配置"""
    name: str
    price: float = Field(gt=0)
    # frozen=False 表示实例属性可修改（默认行为）
    # 设置为 True 时模型变为不可变对象，类似 dataclasses frozen
    model_config = ConfigDict(frozen=False)


product = Product(name="机械键盘", price=399.0)
print("\n=== model_config ===")
print("商品:", product.name)
product.name = "静电容键盘"  # frozen=False，允许修改
print("修改后:", product.name)


# ==============================================================================
# 五、model_validator 跨字段验证（关联校验）
# ==============================================================================

class Subscription(BaseModel):
    """
    订阅模型，演示 model_validator 的跨字段校验。
    与 field_validator 不同，model_validator 可以访问 self 上的所有字段，
    适合处理字段之间的逻辑关系。
    """
    start_date: date
    end_date: date
    status: str = "active"

    @model_validator(mode="after")
    def check_dates(self):
        """
        检查结束日期必须 >= 开始日期。
        mode="after" 表示在所有字段验证完成后执行，此时可以安全访问所有字段。
        """
        if self.end_date < self.start_date:
            raise ValueError("end_date 不能早于 start_date")
        return self


sub = Subscription(start_date=date(2026, 1, 1), end_date=date(2026, 12, 31))
print("\n=== model_validator 跨字段验证 ===")
print("订阅:", sub.start_date, "~", sub.end_date)

# 捕获验证错误，确认跨字段校验生效
try:
    bad = Subscription(start_date=date(2026, 12, 31), end_date=date(2026, 1, 1))
except Exception as e:
    print("错误:", type(e).__name__)


# ==============================================================================
# 六、综合示例：构建可序列化的配置模型
# ==============================================================================

class Config(BaseModel):
    """
    综合配置模型，整合本文件所有特性：
      - Field 约束（长度/范围/默认值）
      - field_validator 预处理（去空格）
      - 枚举类型（Priority）
      - computed_field 派生（env_label / tag_count）
    """
    app_name: str = Field(default="MyApp")
    debug: bool = Field(default=False)
    priority: Priority = Field(default=Priority.MEDIUM)
    allowed_tags: List[str] = Field(default_factory=list, max_length=20)

    @field_validator("app_name", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        """去除 app_name 两端空格，防止用户误输入空格"""
        return v.strip() if isinstance(v, str) else v

    @computed_field
    @property
    def env_label(self) -> str:
        """根据 debug 字段自动派生环境标签"""
        return "DEBUG" if self.debug else "PRODUCTION"

    @computed_field
    @property
    def tag_count(self) -> int:
        """自动统计 allowed_tags 的数量"""
        return len(self.allowed_tags)


# 使用 model_validate 从字典创建模型（支持部分字段和自动类型转换）
config = Config.model_validate({
    "app_name": "  WorkBuddy  ",   # 会被 strip_whitespace 去除空格
    "debug": True,
    "priority": "高",               # 字符串 "高" 自动映射为 Priority.HIGH
    "allowed_tags": ["ai", "agent"]
})
print("\n=== 综合配置模型 ===")
print("应用名:", repr(config.app_name))  # repr 显示引号，确认空格已去除
print("环境:", config.env_label)
print("标签数:", config.tag_count)


print("\naay 01_Pydantic高级特性 done!")
