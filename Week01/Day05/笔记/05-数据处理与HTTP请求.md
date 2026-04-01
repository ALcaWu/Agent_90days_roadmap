# Day 05 - 数据处理与HTTP请求

> 学习日期：2026-04-02
> 学习时长：约2-3小时

---

## 一、requests库基础

### 1.1 核心方法

```python
import requests

# GET请求
resp = requests.get(url, params={"key": "val"}, headers={...}, timeout=10)

# POST请求（发送JSON）
resp = requests.post(url, json=payload, headers={...}, timeout=30)

# 响应处理
resp.status_code   # 状态码
resp.json()        # 解析JSON
resp.text          # 原始文本
resp.raise_for_status()  # 非2xx自动抛异常
```

### 1.2 常见状态码

| 状态码 | 含义 | AI开发场景 |
|--------|------|-----------|
| 200 | 成功 | 正常返回 |
| 401 | 未授权 | API Key无效 |
| 429 | 限流 | 请求过于频繁，需重试 |
| 500 | 服务器错误 | 需重试 |

### 1.3 Session复用（推荐）

```python
session = requests.Session()
session.headers.update({"Authorization": "Bearer sk-xxx"})
# 后续请求自动携带headers，复用TCP连接
resp = session.post(url, json=payload)
session.close()
```

---

## 二、JSON数据处理

### 2.1 基础操作

```python
import json

# 序列化（Python → JSON字符串）
json_str = json.dumps(data, ensure_ascii=False, indent=2)

# 反序列化（JSON字符串 → Python）
data = json.loads(json_str)
```

### 2.2 列表推导式处理数据

```python
# 清洗：去空格 + 过滤空消息
cleaned = [
    {**msg, "content": msg["content"].strip()}
    for msg in messages
    if msg["content"].strip()
]

# 提取：只取user消息
user_msgs = [m["content"] for m in messages if m["role"] == "user"]
```

### 2.3 安全提取嵌套数据

```python
def extract_content(response: dict) -> Optional[str]:
    try:
        return response["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return None
```

---

## 三、重试机制

```python
def call_with_retry(func, max_retries=3, retry_delay=1.0):
    for attempt in range(1, max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt < max_retries:
                time.sleep(retry_delay * attempt)  # 递增等待
            else:
                raise
```

**重试场景：** 429限流、500/503服务器错误、网络超时

---

## 四、AI API调用完整流程

```
1. 构造请求体（build_request）
       ↓
2. 发送HTTP POST请求（带重试）
       ↓
3. 检查状态码
       ↓
4. 解析响应（extract_content）
       ↓
5. 统计Token用量
```

---

## 五、今日要点总结

| 知识点 | 核心要点 |
|--------|----------|
| requests | GET/POST、timeout、raise_for_status |
| Session | 复用连接、统一Headers |
| JSON | dumps/loads、列表推导式清洗 |
| 重试机制 | 递增等待、最大次数限制 |
| 安全提取 | try/except处理KeyError/IndexError |

---

## 六、学习心得

_（学习完成后填写）_

1.
2.
3.
