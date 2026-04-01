# -*- coding: utf-8 -*-
"""
Day 07 - Git常用命令参考 + 项目结构规范
知识点：Git三区模型、常用命令、.gitignore、AI项目结构

注意：本文件以注释形式展示Git命令，实际操作在终端执行
"""

# ==================== 1. Git 日常工作流 ====================
"""
【初始化项目】
git init
git config --global user.name "吴文杰"
git config --global user.email "your@email.com"

【第一次提交】
git add .
git commit -m "init: 初始化项目结构"

【日常开发循环】
# 1. 查看状态（养成习惯，每次操作前先看）
git status

# 2. 查看具体改动
git diff

# 3. 暂存
git add .                    # 暂存全部
git add src/agent.py         # 暂存指定文件

# 4. 提交（写清楚做了什么）
git commit -m "feat: 添加对话记忆功能"

# 5. 查看历史
git log --oneline
"""

# ==================== 2. Commit Message 规范 ====================
"""
格式：<类型>: <简短描述>

类型说明：
  feat     新功能
  fix      修复Bug
  docs     文档更新
  refactor 重构（不影响功能）
  test     添加测试
  chore    构建/工具变更

示例：
  feat: 添加RAG检索功能
  fix: 修复token计算溢出问题
  docs: 更新README安装说明
  test: 添加Agent工具调用测试
  refactor: 拆分chain.py为独立模块
"""

# ==================== 3. 撤销操作速查 ====================
"""
场景1：改了文件，还没add，想撤销
  git restore <file>

场景2：已经add，想取消暂存（保留文件改动）
  git restore --staged <file>

场景3：已经commit，想撤销提交（保留改动在工作区）
  git reset --soft HEAD~1

场景4：已经commit，想完全丢弃（危险！）
  git reset --hard HEAD~1
"""

# ==================== 4. 分支工作流 ====================
"""
主分支保持稳定，新功能在独立分支开发：

git checkout -b feature/rag-retrieval   # 创建并切换到新分支
# ... 开发、提交 ...
git checkout main                        # 切回主分支
git merge feature/rag-retrieval          # 合并
git branch -d feature/rag-retrieval      # 删除已合并的分支
"""

# ==================== 5. 用Python检查Git状态 ====================

import subprocess
from pathlib import Path


def get_git_status(repo_path: str = ".") -> dict:
    """
    获取Git仓库状态信息
    
    Returns:
        包含分支名、修改文件数等信息的字典
    """
    result = {"is_git_repo": False}

    try:
        # 检查是否是Git仓库
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=repo_path,
            capture_output=True,
            check=True
        )
        result["is_git_repo"] = True

        # 获取当前分支
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=repo_path, capture_output=True, text=True
        ).stdout.strip()
        result["branch"] = branch

        # 获取状态
        status = subprocess.run(
            ["git", "status", "--short"],
            cwd=repo_path, capture_output=True, text=True
        ).stdout.strip()
        result["changed_files"] = len(status.splitlines()) if status else 0

        # 获取最近一次提交
        log = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=repo_path, capture_output=True, text=True
        ).stdout.strip()
        result["last_commit"] = log or "暂无提交"

    except subprocess.CalledProcessError:
        result["is_git_repo"] = False
    except FileNotFoundError:
        result["error"] = "Git未安装"

    return result


# 检查当前课程目录
repo_path = r"D:\AgentDeveloperCourse"
status = get_git_status(repo_path)

print("=" * 50)
print("Git仓库状态检查")
print("=" * 50)

if status.get("error"):
    print(f"错误: {status['error']}")
elif not status["is_git_repo"]:
    print(f"路径 {repo_path} 不是Git仓库")
    print("初始化命令：cd D:\\AgentDeveloperCourse && git init")
else:
    print(f"当前分支: {status.get('branch', '未知')}")
    print(f"修改文件数: {status.get('changed_files', 0)}")
    print(f"最近提交: {status.get('last_commit', '无')}")
