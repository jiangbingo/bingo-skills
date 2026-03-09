#!/usr/bin/env python3
"""
Code Churn Tracker - 追踪代码变更率，识别高频修改文件
"""

import subprocess
import re
import os
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

def parse_git_date(date_str):
    """解析 Git 日期字符串，处理各种格式"""
    # Git format: "2026-01-30 19:58:09 +0800"
    # Python < 3.11 的 fromisoformat 不支持带空格的 ISO 格式
    # 使用 strptime 作为可靠的替代方案
    try:
        # 尝试标准 ISO 格式（Python 3.11+）
        return datetime.fromisoformat(date_str)
    except ValueError:
        # 回退到 strptime（适用于所有 Python 版本）
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S %z')

# 需要排除的文件模式
EXCLUDE_PATTERNS = [
    r'node_modules/',
    r'vendor/',
    r'\.git/',
    r'dist/',
    r'build/',
    r'\.venv/',
    r'venv/',
    r'__pycache__/',
    r'\.pyc$',
    r'\.min\.js$',
    r'\.min\.css$',
    r'package-lock\.json',
    r'yarn\.lock',
    r'Pods/',
    r'\.xcodeproj/',
    r'\.xcworkspace/',
    r'DerivedData/',
]

def should_exclude(file_path):
    """检查文件是否应该被排除"""
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, file_path):
            return True
    return False

def get_git_root():
    """获取 Git 仓库根目录"""
    result = subprocess.run(
        ['git', 'rev-parse', '--show-toplevel'],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()

def get_file_size(file_path, git_root):
    """获取文件大小（字节）"""
    full_path = os.path.join(git_root, file_path)
    if os.path.exists(full_path):
        return os.path.getsize(full_path)
    return 0

def get_git_commits(days=90):
    """获取指定天数内的 Git 提交历史"""
    since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    result = subprocess.run([
        'git', 'log',
        f'--since={since_date}',
        '--name-status',
        '--pretty=format:%H|%ai|%an',
        '-m',
    ], capture_output=True, text=True)

    if result.returncode != 0:
        return []

    lines = result.stdout.strip().split('\n')
    commits = []
    current_commit = None

    for line in lines:
        if not line:
            continue

        if '|' in line:
            # 提交信息行
            parts = line.split('|')
            if len(parts) == 3:
                current_commit = {
                    'hash': parts[0],
                    'date': parts[1],
                    'author': parts[2],
                    'files': []
                }
                commits.append(current_commit)
        elif current_commit and line:
            # 文件变更行
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                status = parts[0]
                file_path = parts[1]
                if not should_exclude(file_path):
                    current_commit['files'].append((status, file_path))

    return commits

def analyze_commits(commits, git_root):
    """分析提交历史，计算代码变更指标"""
    file_stats = defaultdict(lambda: {
        'commits': 0,
        'additions': 0,
        'deletions': 0,
        'modifications': 0,
        'renames': 0,
        'first_commit': None,
        'last_commit': None,
        'size': 0,
        'authors': set(),
    })

    if not commits:
        return {}, {}

    total_commits = len(commits)
    start_date = parse_git_date(commits[-1]['date'])
    end_date = parse_git_date(commits[0]['date'])
    days_span = max(1, (end_date - start_date).days)

    for commit in commits:
        commit_date = parse_git_date(commit['date'])
        author = commit['author']

        for status, file_path in commit['files']:
            if should_exclude(file_path):
                continue

            stats = file_stats[file_path]

            if stats['first_commit'] is None:
                stats['first_commit'] = commit_date
            stats['last_commit'] = commit_date
            stats['authors'].add(author)

            if status == 'A':
                stats['additions'] += 1
            elif status == 'D':
                stats['deletions'] += 1
            elif status == 'M':
                stats['modifications'] += 1
            elif status.startswith('R'):
                stats['renames'] += 1

            stats['commits'] += 1
            stats['size'] = get_file_size(file_path, git_root)

    # 计算稳定性评分
    stability_scores = {}
    for file_path, stats in file_stats.items():
        churn_rate = stats['commits'] / days_span if days_span > 0 else 0
        max_commits = total_commits

        # 稳定性评分：100 = 非常稳定，0 = 非常不稳定
        # 考虑因素：提交次数、修改频率、文件大小
        base_score = 100 - (stats['commits'] / max_commits * 50)
        churn_penalty = min(churn_rate * 100, 30)
        size_factor = min(stats['size'] / 100000 * 10, 20)  # 大文件更容易不稳定

        stability = max(0, min(100, base_score - churn_penalty - size_factor))
        stability_scores[file_path] = int(stability)

    return dict(file_stats), stability_scores

def generate_report(file_stats, stability_scores, commits, days=90):
    """生成代码变更率分析报告"""
    now = datetime.now()
    since_date = (now - timedelta(days=days)).strftime('%Y-%m-%d')

    report = []
    report.append("=" * 140)
    report.append("代码变更率分析报告 (Code Churn Analysis)")
    report.append(f"分析时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"分析周期: {since_date} 至今 ({days} 天)")
    report.append("=" * 140)

    if not commits:
        report.append("")
        report.append("⚠️  在指定时间范围内没有找到提交记录")
        report.append("")
        report.append("可能原因:")
        report.append("  - 仓库是新建的，还没有提交")
        report.append("  - 指定的时间范围内没有活动")
        report.append("  - 不是 Git 仓库")
        return '\n'.join(report)

    total_commits = len(commits)
    total_files = len(file_stats)

    report.append(f"总提交数: {total_commits}")
    report.append(f"涉及文件数: {total_files}")
    report.append("")

    # 统计摘要
    report.append("=" * 140)
    report.append("📊 变更统计摘要")
    report.append("=" * 140)

    total_additions = sum(s['additions'] for s in file_stats.values())
    total_modifications = sum(s['modifications'] for s in file_stats.values())
    total_deletions = sum(s['deletions'] for s in file_stats.values())

    report.append(f"新增文件: {total_additions}")
    report.append(f"修改操作: {total_modifications}")
    report.append(f"删除文件: {total_deletions}")
    report.append("")

    # 稳定性分布
    high_stability = sum(1 for s in stability_scores.values() if s >= 80)
    medium_stability = sum(1 for s in stability_scores.values() if 50 <= s < 80)
    low_stability = sum(1 for s in stability_scores.values() if s < 50)

    report.append("稳定性分布:")
    report.append(f"  🟢 高稳定性 (80-100): {high_stability} 个文件")
    report.append(f"  🟡 中稳定性 (50-79):  {medium_stability} 个文件")
    report.append(f"  🔴 低稳定性 (0-49):   {low_stability} 个文件")
    report.append("")

    # 高变动文件
    report.append("=" * 140)
    report.append("🔥 高变动文件 (Top 20)")
    report.append("=" * 140)
    report.append(f"{'文件路径':<50} {'提交数':<8} {'稳定性':<10} {'大小':<12} {'修改者数'}")
    report.append("-" * 140)

    sorted_by_churn = sorted(
        file_stats.items(),
        key=lambda x: x[1]['commits'],
        reverse=True
    )

    for file_path, stats in sorted_by_churn[:20]:
        commits_count = stats['commits']
        stability = stability_scores[file_path]
        size = stats['size']
        authors = len(stats['authors'])

        # 稳定性指示器
        if stability >= 80:
            stability_indicator = f"🟢 {stability}"
        elif stability >= 50:
            stability_indicator = f"🟡 {stability}"
        else:
            stability_indicator = f"🔴 {stability}"

        # 文件大小格式化
        if size >= 1024 * 1024:
            size_str = f"{size / (1024 * 1024):.1f} MB"
        elif size >= 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size} B"

        # 截断过长的路径
        display_path = file_path if len(file_path) <= 48 else '...' + file_path[-45:]

        report.append(f"{display_path:<50} {commits_count:<8} {stability_indicator:<10} {size_str:<12} {authors}")

    report.append("")

    # 风险区域分析
    report.append("=" * 140)
    report.append("⚠️  风险区域识别")
    report.append("=" * 140)

    high_risk = []
    for file_path, stats in file_stats.items():
        stability = stability_scores[file_path]
        churn_rate = stats['commits'] / days if days > 0 else 0
        size = stats['size']

        # 高风险标准：低稳定性 + 高变动率 或 大文件 + 高变动
        if (stability < 50 and churn_rate > 0.1) or (size > 50000 and stats['commits'] > 10):
            high_risk.append((file_path, stats, stability, churn_rate))

    high_risk.sort(key=lambda x: x[3], reverse=True)

    if high_risk:
        report.append(f"发现 {len(high_risk)} 个高风险文件:")
        report.append("")
        for file_path, stats, stability, churn_rate in high_risk[:15]:
            risk_reason = []
            if stability < 50:
                risk_reason.append(f"低稳定性({stability})")
            if churn_rate > 0.1:
                risk_reason.append(f"高频变动({churn_rate:.2f}/天)")
            if stats['size'] > 50000:
                risk_reason.append(f"大文件({stats['size']//1024}KB)")

            report.append(f"  - {file_path}")
            report.append(f"    原因: {', '.join(risk_reason)}")
            report.append(f"    提交: {stats['commits']} 次 | 修改者: {len(stats['authors'])} 人")
            report.append("")
    else:
        report.append("✅ 未发现明显的高风险文件")
        report.append("")

    # 按文件类型分析
    report.append("=" * 140)
    report.append("📁 按文件类型分析")
    report.append("=" * 140)

    ext_stats = defaultdict(lambda: {'files': 0, 'commits': 0, 'total_size': 0})
    for file_path, stats in file_stats.items():
        ext = Path(file_path).suffix or '(no extension)'
        ext_stats[ext]['files'] += 1
        ext_stats[ext]['commits'] += stats['commits']
        ext_stats[ext]['total_size'] += stats['size']

    sorted_exts = sorted(ext_stats.items(), key=lambda x: x[1]['commits'], reverse=True)
    for ext, data in sorted_exts[:10]:
        avg_size = data['total_size'] / data['files'] if data['files'] > 0 else 0
        report.append(f"  {ext:<20} 文件: {data['files']:<4} | 提交: {data['commits']:<5} | 平均大小: {avg_size/1024:.1f} KB")

    report.append("")

    # 建议
    report.append("=" * 140)
    report.append("💡 改进建议")
    report.append("=" * 140)

    if low_stability > 0:
        report.append("")
        report.append("针对低稳定性文件:")
        report.append("  1. 审查频繁修改的原因")
        report.append("  2. 考虑重构设计以减少变更需求")
        report.append("  3. 增加单元测试以提高变更信心")
        report.append("  4. 评估是否需要拆分复杂模块")

    if high_risk:
        report.append("")
        report.append("针对高风险文件:")
        report.append("  1. 优先进行代码审查")
        report.append("  2. 考虑模块化拆分")
        report.append("  3. 建立更严格的测试覆盖")
        report.append("  4. 评估技术债务偿还计划")

    report.append("")
    report.append("通用建议:")
    report.append("  - 定期运行此分析跟踪代码健康度")
    report.append("  - 在代码审查时关注高变动文件")
    report.append("  - 对频繁变更的区域进行架构审查")
    report.append("  - 考虑使用特性开关减少直接修改")

    return '\n'.join(report)

def save_report(report, output_file):
    """保存报告到文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

def main():
    print("🔍 正在分析 Git 提交历史...")

    git_root = get_git_root()
    if not git_root:
        print("❌ 错误: 当前目录不是 Git 仓库")
        return

    print(f"✅ Git 仓库根目录: {git_root}")

    commits = get_git_commits(days=90)
    print(f"✅ 获取到 {len(commits)} 个提交记录")

    if not commits:
        print("⚠️  在过去 90 天内没有找到提交记录")
        print("📊 正在生成空报告...")
        report = generate_report({}, {}, commits, days=90)
    else:
        print("📊 正在分析文件变更...")
        file_stats, stability_scores = analyze_commits(commits, git_root)
        print(f"✅ 分析了 {len(file_stats)} 个文件")

        print("📝 正在生成分析报告...")
        report = generate_report(file_stats, stability_scores, commits, days=90)

    output_file = 'code_churn_report.txt'
    save_report(report, output_file)
    print(f"✅ 报告已保存到: {output_file}")

    print("\n" + "=" * 60)
    print("📋 分析摘要")
    print("=" * 60)
    print(f"  分析周期: 最近 90 天")
    print(f"  总提交数: {len(commits)}")
    print(f"  涉及文件: {len(commits) > 0 and len(set(f for c in commits for _, f in c['files'])) or 0}")
    print(f"  报告文件: {output_file}")

if __name__ == '__main__':
    main()
