#!/usr/bin/env python3
"""
GitHub Actions Workflow Checker
检查GitHub Actions是否正在运行
"""
import subprocess
import sys
from datetime import datetime

def run_command(cmd):
    """运行命令并返回输出"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def main():
    print("=" * 60)
    print("GitHub Actions Workflow Status Check")
    print("=" * 60)
    print(f"\nCurrent time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 拉取最新代码
    print("Pulling latest changes...")
    import os
    os.chdir('C:/Users/yueyo/clawd/AgentTaskHub')
    pull_result = run_command("git pull origin master")
    print(pull_result)
    print()

    # 检查最近的GitHub Actions commits
    print("=" * 60)
    print("Recent GitHub Actions Bot Commits:")
    print("=" * 60)
    commits = run_command("git log --author='github-actions[bot]' --oneline -5")
    print(commits)
    print()

    # 检查最新commit的时间
    print("=" * 60)
    print("Latest Commit Details:")
    print("=" * 60)
    latest = run_command("git log --author='github-actions[bot]' --format='%H%n%ai%n%s' -1")
    print(latest)
    print()

    # 读取progress.md
    print("=" * 60)
    print("Recent progress.md entries:")
    print("=" * 60)
    try:
        with open('progress.md', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # 找到最后5次GitHub Actions Run
            runs = [line for line in lines if 'GitHub Actions Run' in line]
            for run in runs[-5:]:
                print(run.strip())
                # 打印该run后的几行
                idx = lines.index(run)
                for i in range(idx+1, min(idx+6, len(lines))):
                    if lines[i].strip() and not lines[i].startswith('##'):
                        print(lines[i].strip())
                    elif lines[i].startswith('##'):
                        break
    except Exception as e:
        print(f"Error reading progress.md: {e}")
    print()

    print("=" * 60)
    print("If you see commits with timestamp within last 15 minutes,")
    print("workflow is actively running!")
    print("=" * 60)

if __name__ == "__main__":
    main()
