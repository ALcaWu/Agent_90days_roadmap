# -*- coding: utf-8 -*-
"""
Day 10 - Prompt Template 练习题
学习目标：通过练习巩固 PromptTemplate 和 ChatPromptTemplate 的使用

说明：
1. 所有练习题只给出题目和提示（pass 留空）
2. 完成后说"验证答案"，我会给出解析和标准答案
3. 代码需要实际运行，确保正确性

运行测试：python 练习题.py
"""

import unittest
from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


# ============================================
# 练习1：创建翻译模板
# ============================================


def exercise_1():
    """
    任务：创建一个翻译模板，支持源语言、目标语言和待翻译文本三个变量

    要求：
    1. 使用 PromptTemplate.from_template 创建
    2. 模板内容：将{source_language}翻译成{target_language}：{text}
    3. 返回填充后的提示文本

    提示：使用 invoke() 方法填充变量
    """
    template = PromptTemplate.from_template(
        "将{source_language}翻译成{target_language}：{text}"
    )
    return template.invoke(
        {
            "source_language": "English",
            "target_language": "Chinese",
            "text": "I love programming.",
        }
    )
    pass


# ============================================
# 练习2：部分填充模板
# ============================================


def exercise_2():
    """
    任务：创建一个代码审查模板，预填充角色信息

    要求：
    1. 模板：你是{role}，请审查以下{language}代码：{code}
    2. 使用 partial() 预填充 role="资深Python工程师"
    3. 返回填充 language="Python", code="print('hello')" 后的提示文本

    提示：先 partial 预填充，再 invoke 填充剩余变量
    """
    template_1 = PromptTemplate.from_template(
        "你是{role}，请审查以下{language}代码：{code}"
    )
    template = template_1.partial(role="资深Python工程师")

    return template.invoke(
        {
            "language": "Python",
            "code": "print('hello')",
        }
    )
    pass


# ============================================
# 练习3：创建对话模板
# ============================================


def exercise_3():
    """
    任务：创建一个包含对话历史的 ChatPromptTemplate

    要求：
    1. 系统消息：你是一个{role}，擅长{skill}
    2. 使用 MessagesPlaceholder 插入对话历史
    3. 用户消息：{input}
    4. 返回填充后的消息列表

    参数：
    - role: "AI助手"
    - skill: "Python编程"
    - history: [HumanMessage("你好"), AIMessage("你好！")]
    - input: "请介绍一下自己"

    提示：使用 MessagesPlaceholder("history") 创建占位符
    """
    template = ChatPromptTemplate.from_messages(
        [
            ("system", "你是一个{role}，擅长{skill}"),
            MessagesPlaceholder("history"),  # 动态消息占位符
            ("human", "{input}"),
        ]
    )
    history = [HumanMessage(content="你好"), AIMessage(content="你好！")]
    message = template.invoke(
        {
            "role": "AI助手",
            "skill": "Python编程",
            "history": history,
            "input": "请介绍一下自己",
        }
    )
    print("\n完整消息列表:")
    for i, msg in enumerate(message.messages, 1):
        content_preview = (
            msg.content[:30] + "..." if len(msg.content) > 30 else msg.content
        )

    return message.messages
    pass


# ============================================
# 练习4：Few-shot 示例模板
# ============================================


def exercise_4():
    """
    任务：创建一个情感分析的 Few-shot 模板

    要求：
    1. 系统消息：你是一个情感分析助手
    2. 嵌入2个示例：
       - 示例1：human="今天真开心！" -> ai="积极情感"
       - 示例2：human="太糟糕了" -> ai="消极情感"
    3. 最后是实际输入：{text}
    4. 返回填充 text="还行吧" 后的消息列表

    提示：在 from_messages 中直接使用 ("human", ...) 和 ("ai", ...) 格式
    """
    template = ChatPromptTemplate.from_messages(
        [
            ("system", "你是一个情感分析助手"),
            (
                "human",
                "今天真开心！",
            ),
            # ("ai", "itivesentiment"),   # ❌ 原答案：英文，测试要求中文"积极"
            (
                "ai",
                "积极情感",
            ),
            (
                "human",
                "太糟糕了",
            ),
            # ("ai", "Negativesentiment"),  # ❌ 原答案：英文，测试要求中文"消极"
            (
                "ai",
                "消极情感",
            ),
            ("human", "{text}"),
        ]
    )
    message = template.invoke(
        {
            "text": "还行吧",
        }
    )
    return message.messages
    pass


# ============================================
# 练习5：模板组合
# ============================================


def exercise_5():
    """
    任务：使用 + 操作符组合多个模板

    要求：
    1. 创建三个模板：
       - role_template: "你是一个{role}。\n"
       - task_template: "请完成以下任务：{task}\n"
       - format_template: "输出格式：{format}"
    2. 使用 + 组合成完整模板
    3. 返回填充后的提示文本

    参数：
    - role: "数据分析师"
    - task: "分析销售数据趋势"
    - format: "JSON格式，包含趋势和预测"

    提示：template1 + template2 + template3
    """
    role_template = ChatPromptTemplate.from_messages(
        [
            ("system", "你是一个{role}。\n"),
        ]
    )
    task_template = ChatPromptTemplate.from_messages(
        [
            ("system", "请完成以下任务：{task}\n"),
        ]
    )
    format_template = ChatPromptTemplate.from_messages(
        [
            ("system", "输出格式：{format}"),
        ]
    )
    combined_template = role_template + task_template + format_template
    return combined_template.invoke(
        {
            "role": "数据分析师",
            "task": "分析销售数据趋势",
            "format": "JSON格式，包含趋势和预测",
        }
    )
    pass


# ============================================
# 练习6：实战 - 构建智能助手模板
# ============================================


def exercise_6():
    """
    任务：构建一个完整的智能助手对话模板

    要求：
    1. 系统消息包含：
       - 角色定义：你是{role}
       - 能力说明：你擅长{skills}（多个技能用逗号分隔）
       - 回答风格：请用{style}的风格回答
    2. 使用 MessagesPlaceholder 支持对话历史
    3. 用户消息：{question}
    4. 返回填充后的消息列表

    参数：
    - role: "AI编程助手"
    - skills: "Python, JavaScript, SQL"
    - style: "简洁专业"
    - history: [HumanMessage("什么是变量？"), AIMessage("变量是存储数据的容器。")]
    - question: "那函数是什么呢？"

    提示：系统消息可以使用多行字符串
    """
    chat_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                你是{role}，擅长{skills}。
                请用{style}的风格回答。
            """,
            ),
            MessagesPlaceholder("history"),
            ("human", "{question}"),
        ]
    )
    history = [
        HumanMessage(content="什么是变量？"),
        AIMessage(content="变量是存储数据的容器。"),
    ]
    message = chat_template.invoke(
        {
            "role": "AI编程助手",
            "skills": "Python, JavaScript, SQL",
            "style": "简洁专业",
            "history": history,
            "question": "那函数是什么呢？",
        }
    )
    return message.messages
    pass


# ============================================
# 单元测试
# ============================================


class TestExercise1(unittest.TestCase):
    """测试练习1：创建翻译模板"""

    def test_returns_string(self):
        """返回值不为 None"""
        result = exercise_1()
        self.assertIsNotNone(result)

    def test_contains_target_language(self):
        """结果中包含目标语言 Chinese"""
        result = exercise_1()
        self.assertIn("Chinese", str(result))

    def test_contains_source_language(self):
        """结果中包含源语言 English"""
        result = exercise_1()
        self.assertIn("English", str(result))

    def test_contains_text(self):
        """结果中包含待翻译文本"""
        result = exercise_1()
        self.assertIn("I love programming.", str(result))


class TestExercise2(unittest.TestCase):
    """测试练习2：部分填充模板"""

    def test_returns_value(self):
        """返回值不为 None"""
        result = exercise_2()
        self.assertIsNotNone(result)

    def test_contains_role(self):
        """结果中包含预填充的角色信息"""
        result = exercise_2()
        self.assertIn("资深Python工程师", str(result))

    def test_contains_language(self):
        """结果中包含编程语言"""
        result = exercise_2()
        self.assertIn("Python", str(result))

    def test_contains_code(self):
        """结果中包含代码"""
        result = exercise_2()
        self.assertIn("print('hello')", str(result))


class TestExercise3(unittest.TestCase):
    """测试练习3：创建对话模板"""

    def test_returns_list(self):
        """返回值是消息列表"""
        result = exercise_3()
        self.assertIsInstance(result, list)

    def test_has_system_message(self):
        """第一条消息是 SystemMessage"""
        result = exercise_3()
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0].type, "system")

    def test_system_contains_role(self):
        """SystemMessage 包含角色信息"""
        result = exercise_3()
        self.assertIn("AI助手", result[0].content)

    def test_system_contains_skill(self):
        """SystemMessage 包含技能信息"""
        result = exercise_3()
        self.assertIn("Python编程", result[0].content)

    def test_contains_history_messages(self):
        """消息列表中包含历史消息"""
        result = exercise_3()
        types = [m.type for m in result]
        self.assertIn("human", types)
        self.assertIn("ai", types)

    def test_last_message_is_human(self):
        """最后一条消息是用户输入"""
        result = exercise_3()
        self.assertEqual(result[-1].type, "human")
        self.assertIn("请介绍一下自己", result[-1].content)


class TestExercise4(unittest.TestCase):
    """测试练习4：Few-shot 示例模板"""

    def test_returns_list(self):
        """返回值是消息列表"""
        result = exercise_4()
        self.assertIsInstance(result, list)

    def test_has_system_message(self):
        """包含 SystemMessage"""
        result = exercise_4()
        types = [m.type for m in result]
        self.assertIn("system", types)

    def test_contains_few_shot_examples(self):
        """包含 Few-shot 示例（至少有2条human和2条ai）"""
        result = exercise_4()
        human_msgs = [m for m in result if m.type == "human"]
        ai_msgs = [m for m in result if m.type == "ai"]
        self.assertGreaterEqual(len(human_msgs), 2)
        self.assertGreaterEqual(len(ai_msgs), 2)

    def test_contains_positive_example(self):
        """包含积极情感示例"""
        result = exercise_4()
        contents = " ".join([m.content for m in result])
        self.assertIn("积极", contents)

    def test_contains_negative_example(self):
        """包含消极情感示例"""
        result = exercise_4()
        contents = " ".join([m.content for m in result])
        self.assertIn("消极", contents)

    def test_last_message_contains_input(self):
        """最后一条消息包含实际输入"""
        result = exercise_4()
        self.assertIn("还行吧", result[-1].content)


class TestExercise5(unittest.TestCase):
    """测试练习5：模板组合"""

    def test_returns_value(self):
        """返回值不为 None"""
        result = exercise_5()
        self.assertIsNotNone(result)

    def test_contains_role(self):
        """结果中包含角色"""
        result = exercise_5()
        self.assertIn("数据分析师", str(result))

    def test_contains_task(self):
        """结果中包含任务"""
        result = exercise_5()
        self.assertIn("分析销售数据趋势", str(result))

    def test_contains_format(self):
        """结果中包含输出格式"""
        result = exercise_5()
        self.assertIn("JSON", str(result))


class TestExercise6(unittest.TestCase):
    """测试练习6：构建智能助手对话模板"""

    def test_returns_list(self):
        """返回值是消息列表"""
        result = exercise_6()
        self.assertIsInstance(result, list)

    def test_has_system_message(self):
        """包含 SystemMessage"""
        result = exercise_6()
        self.assertEqual(result[0].type, "system")

    def test_system_contains_role(self):
        """SystemMessage 包含角色定义"""
        result = exercise_6()
        self.assertIn("AI编程助手", result[0].content)

    def test_system_contains_skills(self):
        """SystemMessage 包含技能信息"""
        result = exercise_6()
        self.assertIn("Python", result[0].content)

    def test_system_contains_style(self):
        """SystemMessage 包含回答风格"""
        result = exercise_6()
        self.assertIn("简洁专业", result[0].content)

    def test_contains_history(self):
        """包含对话历史"""
        result = exercise_6()
        contents = " ".join([m.content for m in result])
        self.assertIn("什么是变量", contents)

    def test_last_message_is_user_question(self):
        """最后一条消息是用户提问"""
        result = exercise_6()
        self.assertEqual(result[-1].type, "human")
        self.assertIn("函数", result[-1].content)


# ============================================
# 入口：运行测试 / 查看结果
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("Day 10 - Prompt Template 练习题 & 单元测试")
    print("=" * 50)
    print()
    unittest.main(verbosity=2)
