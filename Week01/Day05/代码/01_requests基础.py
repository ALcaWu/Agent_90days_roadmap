# -*- coding: utf-8 -*-
"""
Day 05 - requests库基础
知识点：GET/POST请求、响应处理、超时与异常、Session
"""

import requests
import json


# ==================== 1. GET请求 ====================

print("=" * 50)
print("1. GET请求示例")
print("=" * 50)

# 使用公开API演示（httpbin.org 是专门用于测试HTTP请求的服务）
try:
    resp = requests.get(
        url="https://httpbin.org/get",
        params={"name": "agent", "version": "1.0"},  # 查询参数
        timeout=10  # 超时时间（秒）
    )

    print(f"状态码: {resp.status_code}")
    data = resp.json()
    print(f"请求URL: {data['url']}")
    print(f"传入参数: {data['args']}")

except requests.exceptions.Timeout:
    print("请求超时！")
except requests.exceptions.ConnectionError:
    print("网络连接失败！")

print()


# ==================== 2. POST请求（模拟AI API格式） ====================

print("=" * 50)
print("2. POST请求示例（模拟AI API格式）")
print("=" * 50)

try:
    # 构造OpenAI格式的请求体
    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "你是一个助手"},
            {"role": "user", "content": "你好"}
        ],
        "temperature": 0.7
    }

    # 模拟发送（用httpbin.org回显请求内容）
    resp = requests.post(
        url="https://httpbin.org/post",
        json=payload,           # 自动设置 Content-Type: application/json
        headers={
            "Authorization": "Bearer sk-test-xxx",  # API Key
            "User-Agent": "MyAgent/1.0"
        },
        timeout=10
    )

    data = resp.json()
    # 取回我们发送的JSON内容
    sent_body = json.loads(data["data"])
    print(f"发送的模型: {sent_body['model']}")
    print(f"发送的消息数: {len(sent_body['messages'])}")
    print(f"服务器收到的Authorization: {data['headers'].get('Authorization', '无')}")

except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}")

print()


# ==================== 3. 状态码处理 ====================

print("=" * 50)
print("3. 状态码处理")
print("=" * 50)

STATUS_MESSAGES = {
    200: "成功",
    400: "请求参数错误",
    401: "未授权（API Key无效）",
    403: "禁止访问",
    404: "资源不存在",
    429: "请求过于频繁（限流）",
    500: "服务器内部错误",
    503: "服务暂时不可用",
}

def check_response(resp: requests.Response) -> dict:
    """统一处理API响应"""
    status = resp.status_code
    msg = STATUS_MESSAGES.get(status, f"未知状态码: {status}")

    if status == 200:
        return {"success": True, "data": resp.json()}
    else:
        return {"success": False, "error": msg, "status": status}

# 测试不同状态码
for code in [200, 404, 500]:
    try:
        resp = requests.get(f"https://httpbin.org/status/{code}", timeout=10)
        result = check_response(resp)
        print(f"状态码 {code}: {result}")
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

print()


# ==================== 4. Session复用（推荐用法） ====================

print("=" * 50)
print("4. Session复用（生产环境推荐）")
print("=" * 50)

# Session的优势：
# - 复用TCP连接，减少握手开销
# - 统一设置Headers，不用每次重复写
# - 自动管理Cookie

class APIClient:
    """封装API客户端（AI开发中的常见模式）"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.session = requests.Session()
        # 统一设置请求头
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    def post(self, endpoint: str, payload: dict) -> dict:
        """发送POST请求"""
        try:
            resp = self.session.post(
                url=f"{self.base_url}{endpoint}",
                json=payload,
                timeout=30
            )
            resp.raise_for_status()  # 非2xx状态码自动抛出异常
            return {"success": True, "data": resp.json()}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": f"HTTP错误: {e}"}
        except requests.exceptions.Timeout:
            return {"success": False, "error": "请求超时"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def close(self):
        self.session.close()


# 演示使用
client = APIClient(
    base_url="https://httpbin.org",
    api_key="sk-test-demo"
)

result = client.post("/post", {"message": "hello"})
print(f"请求成功: {result['success']}")
if result["success"]:
    print(f"收到响应数据键: {list(result['data'].keys())}")

client.close()
