# Day 07 - Git基础与Week01总结

> 学习日期：2026-04-01
> 学习时长：约2-3小时

---

## 一、Git 三区模型

```
工作区  →(git add)→  暂存区  →(git commit)→  本地仓库  →(git push)→  远程仓库
```

| 区域 | 说明 |
|------|------|
| 工作区 | 实际编辑的文件 |
| 暂存区 | 准备提交的快照（git add后） |
| 本地仓库 | 永久保存的历史记录 |

---

## 二、常用命令速查

### 初始化
```bash
git init
git config --global user.name "姓名"
git config --global user.email "邮箱"
```

### 日常工作流
```bash
git status                          # 查看状态（最常用）
git add .                           # 暂存全部
git commit -m "feat: 添加功能"      # 提交
git log --oneline                   # 查看历史
git diff                            # 查看未暂存改动
```

### 撤销
```bash
git restore <file>                  # 丢弃工作区修改
git restore --staged <file>         # 取消暂存
git reset --soft HEAD~1             # 撤销提交（保留改动）
```

### 分支
```bash
git checkout -b feature/xxx         # 创建并切换分支
git merge feature/xxx               # 合并分支
git branch -d feature/xxx           # 删除已合并分支
```

---

## 三、Commit Message 规范

```
feat:     新功能
fix:      修复Bug
docs:     文档更新
refactor: 重构
test:     添加测试
chore:    构建/工具变更
```

---

## 四、.gitignore 核心规则（AI项目）

```gitignore
venv/               # 虚拟环境
.env                # API Key（绝对不提交！）
__pycache__/        # Python缓存
*.pyc
*.log
chroma_db/          # 向量数据库
models/             # 模型文件
.DS_Store
```

---

## 五、AI项目标准目录结构

```
my-agent/
├── README.md
├── requirements.txt
├── .env.example        # 模板（提交）
├── .env                # 真实Key（不提交）
├── .gitignore
├── src/
│   ├── agent.py
│   ├── chains.py
│   ├── tools.py
│   └── config.py
├── tests/
│   └── test_agent.py
└── data/
```

---

## 六、Week01 知识点总览

| Day | 主题 | 核心知识点 |
|-----|------|-----------|
| 01 | Python基础 | 数据结构、函数、JSON |
| 02 | 面向对象 | 类、继承、装饰器、异常 |
| 03 | 文件与正则 | pathlib、re、日志 |
| 04 | 模块与测试 | import、venv、unittest |
| 05 | HTTP请求 | requests、数据清洗、重试 |
| 06 | 异步编程 | asyncio、gather、aiohttp |
| 07 | Git与总结 | 三区模型、规范、项目结构 |

---

## 七、学习心得

_（学习完成后填写）_

1.了解python的基本语法
2.学会了使用git进行版本控制
3.对异步编程有了一定的了解
