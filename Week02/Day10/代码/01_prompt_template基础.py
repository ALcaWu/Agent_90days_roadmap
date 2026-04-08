"""
Day 10 - PromptTemplate 基础用法
学习目标：掌握 PromptTemplate 的创建、变量替换和部分填充
"""

from langchain_core.prompts import PromptTemplate

# ============================================
# 1. 创建模板的两种方式
# ============================================

print("=" * 50)
print("1. 创建模板的两种方式")
print("=" * 50)

# 方式1：from_template（推荐，自动提取变量）
template1 = PromptTemplate.from_template("给我讲一个关于{topic}的笑话")
print(f"模板1变量: {template1.input_variables}")

# 方式2：构造函数（显式声明变量）
template2 = PromptTemplate(
    input_variables=["topic"],
    template="给我讲一个关于{topic}的笑话"
)
print(f"模板2变量: {template2.input_variables}")

# ============================================
# 2. 变量替换
# ============================================

print("\n" + "=" * 50)
print("2. 变量替换")
print("=" * 50)

# 单变量替换
single_template = PromptTemplate.from_template("翻译成{language}：{text}")
prompt = single_template.invoke({"language": "英语", "text": "你好世界"})
print(f"单变量结果:\n{prompt.text}")

# 多变量替换
multi_template = PromptTemplate.from_template("""
你是一个{role}，请用{style}风格回答问题：
{question}
""")
prompt = multi_template.invoke({
    "role": "资深工程师",
    "style": "简洁专业",
    "question": "什么是微服务？"
})
print(f"\n多变量结果:\n{prompt.text}")

# ============================================
# 3. 部分填充（Partial）
# ============================================

print("\n" + "=" * 50)
print("3. 部分填充（Partial）")
print("=" * 50)

# 场景：某些变量在创建模板时就已知，其他变量后续填充
full_template = PromptTemplate.from_template(
    "你是{role}，请用{tone}的语气回答：{question}"
)

# 先填充 role 和 tone
partial_template = full_template.partial(
    role="AI编程助手",
    tone="友好且专业"
)
print(f"部分填充后的剩余变量: {partial_template.input_variables}")

# 后填充 question
final_prompt = partial_template.invoke({"question": "什么是装饰器？"})
print(f"\n最终提示:\n{final_prompt.text}")

# ============================================
# 4. 模板组合
# ============================================

print("\n" + "=" * 50)
print("4. 模板组合")
print("=" * 50)

# 使用 + 操作符拼接模板
intro = PromptTemplate.from_template("你是一个{role}。\n")
task = PromptTemplate.from_template("请完成以下任务：{task}\n")
format_rule = PromptTemplate.from_template("输出格式要求：{format}")

# 组合多个模板
combined = intro + task + format_rule
print(f"组合后的变量: {combined.input_variables}")

# 使用组合模板
prompt = combined.invoke({
    "role": "Python专家",
    "task": "解释什么是生成器",
    "format": "Markdown格式，包含代码示例"
})
print(f"\n组合模板结果:\n{prompt.text}")

# ============================================
# 5. 格式化方法对比
# ============================================

print("\n" + "=" * 50)
print("5. 格式化方法对比")
print("=" * 50)

# 传统字符串格式化（不推荐用于复杂场景）
traditional = "你好，{}！今天是{}".format("吴文杰", "星期五")
print(f"传统方式: {traditional}")

# PromptTemplate 方式（推荐）
template_way = PromptTemplate.from_template("你好，{name}！今天是{day}")
result = template_way.invoke({"name": "吴文杰", "day": "星期五"})
print(f"模板方式: {result.text}")

# PromptTemplate 的优势：变量验证
try:
    # 缺少变量时会报错
    bad_template = PromptTemplate.from_template("{a}和{b}")
    # bad_template.invoke({"a": "1"})  # 会抛出 ValidationError
except Exception as e:
    print(f"变量验证错误: {type(e).__name__}")

print("\n✅ PromptTemplate 基础用法学习完成")