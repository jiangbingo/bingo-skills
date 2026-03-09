#!/usr/bin/env python3
"""
Git Commit Analyzer - 分析 Git 提交历史
提供提交统计、贡献者排行、活跃时段热图和提交信息质量分析
"""

import json
import subprocess
import re
from datetime import datetime
from collections import Counter, defaultdict
import os
import sys

def check_git_repo():
    """检查当前目录是否为 Git 仓库"""
    if not os.path.exists('.git'):
        print("❌ 错误: 当前目录不是 Git 仓库")
        print("   请在 Git 仓库目录中运行此脚本")
        sys.exit(1)

def fetch_commits(limit=None):
    """
    使用 git log 获取提交数据
    返回提交列表
    """
    try:
        cmd = 'git log --pretty=format:\'{"hash":"%H","author":"%an","date":"%ad","message":"%s"}\' --date=iso'
        if limit:
            cmd += f' -n {limit}'

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"❌ Git 命令执行失败: {result.stderr}")
            sys.exit(1)

        if not result.stdout.strip():
            print("⚠️  警告: 没有找到任何提交记录")
            return []

        commits = []
        for line in result.stdout.strip().split('\n'):
            try:
                commit = json.loads(line)
                commits.append(commit)
            except json.JSONDecodeError:
                continue

        return commits

    except Exception as e:
        print(f"❌ 获取提交数据时出错: {e}")
        sys.exit(1)

def parse_date(date_str):
    """解析 ISO 格式日期字符串"""
    try:
        return datetime.fromisoformat(date_str)
    except (ValueError, AttributeError):
        return None

def analyze_contributors(commits):
    """分析贡献者统计"""
    authors = Counter(c['author'] for c in commits)
    total = len(commits)

    contributor_stats = []
    for author, count in authors.most_common():
        percentage = (count / total) * 100 if total > 0 else 0
        contributor_stats.append({
            'author': author,
            'commits': count,
            'percentage': percentage
        })

    return contributor_stats

def analyze_activity_heatmap(commits):
    """分析活跃时段热图"""
    hourly = defaultdict(int)
    daily = defaultdict(int)
    monthly = defaultdict(int)

    for commit in commits:
        dt = parse_date(commit['date'])
        if dt:
            hourly[dt.hour] += 1
            daily[dt.strftime('%A')] += 1
            monthly[dt.strftime('%Y-%m')] += 1

    # 按星期排序
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_sorted = {day: daily.get(day, 0) for day in day_order}

    return {
        'hourly': dict(hourly),
        'daily': daily_sorted,
        'monthly': dict(sorted(monthly.items()))
    }

def analyze_commit_patterns(commits):
    """分析提交模式"""
    message_lengths = [len(c['message']) for c in commits]
    avg_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0

    # 分析提交频率
    if len(commits) >= 2:
        first_commit = parse_date(commits[-1]['date'])
        last_commit = parse_date(commits[0]['date'])
        if first_commit and last_commit:
            days_span = (last_commit - first_commit).days + 1
            commits_per_day = len(commits) / days_span if days_span > 0 else 0
        else:
            commits_per_day = 0
    else:
        commits_per_day = 0

    return {
        'total_commits': len(commits),
        'avg_message_length': avg_length,
        'commits_per_day': commits_per_day,
        'message_lengths': message_lengths
    }

def check_conventional_commits(commits):
    """检查是否符合约定式提交规范"""
    conventional_types = [
        'feat', 'fix', 'docs', 'style', 'refactor',
        'test', 'chore', 'perf', 'ci', 'build'
    ]

    conventional_count = 0
    type_distribution = Counter()

    for commit in commits:
        message = commit['message'].strip()
        # 检查是否以类型开头
        match = re.match(r'^(\w+)(\(.+\))?\s*:', message)
        if match:
            commit_type = match.group(1).lower()
            if commit_type in conventional_types:
                conventional_count += 1
                type_distribution[commit_type] += 1

    compliance_rate = (conventional_count / len(commits)) * 100 if commits else 0

    return {
        'conventional_count': conventional_count,
        'total_count': len(commits),
        'compliance_rate': compliance_rate,
        'type_distribution': dict(type_distribution)
    }

def generate_heatmap_bar(data, max_value, width=50):
    """生成简单的条形图"""
    if max_value == 0:
        return [' ' * width]

    bars = []
    for key, value in data.items():
        bar_length = int((value / max_value) * width)
        bar = '█' * bar_length + ' ' * (width - bar_length)
        bars.append(f"{bar} {value}")
    return bars

def generate_report(commits):
    """生成分析报告"""
    if not commits:
        return "没有找到任何提交记录"

    now = datetime.now()
    contributors = analyze_contributors(commits)
    heatmap = analyze_activity_heatmap(commits)
    patterns = analyze_commit_patterns(commits)
    conventional = check_conventional_commits(commits)

    # 获取日期范围
    first_date = parse_date(commits[-1]['date'])
    last_date = parse_date(commits[0]['date'])

    report = []
    report.append("=" * 140)
    report.append("Git 提交历史分析报告")
    report.append(f"分析时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 140)
    report.append("")

    # 基础统计
    report.append("=" * 140)
    report.append("📊 基础统计")
    report.append("=" * 140)
    report.append(f"总提交数: {patterns['total_commits']}")
    report.append(f"贡献者数: {len(contributors)}")
    if first_date and last_date:
        report.append(f"时间范围: {first_date.strftime('%Y-%m-%d')} 至 {last_date.strftime('%Y-%m-%d')}")
        days_span = (last_date - first_date).days + 1
        report.append(f"跨度天数: {days_span} 天")
    report.append(f"平均提交频率: {patterns['commits_per_day']:.2f} 提交/天")
    report.append(f"平均信息长度: {patterns['avg_message_length']:.1f} 字符")
    report.append("")

    # 贡献者排行
    report.append("=" * 140)
    report.append("👥 贡献者排行榜")
    report.append("=" * 140)
    report.append(f"{'排名':<6} {'贡献者':<30} {'提交数':<10} {'占比'}")
    report.append("-" * 140)

    for i, contributor in enumerate(contributors, 1):
        bar_length = int(contributor['percentage'] / 2)
        bar = '█' * bar_length
        report.append(f"{i:<6} {contributor['author']:<30} {contributor['commits']:<10} {contributor['percentage']:>5.1f}% {bar}")

    report.append("")

    # 小时热图
    report.append("=" * 140)
    report.append("⏰ 提交时段热图（按小时）")
    report.append("=" * 140)

    hourly_max = max(heatmap['hourly'].values()) if heatmap['hourly'] else 0
    for hour in range(24):
        count = heatmap['hourly'].get(hour, 0)
        bar_length = int((count / hourly_max) * 40) if hourly_max > 0 else 0
        bar = '█' * bar_length
        marker = ' 👈' if hour == 12 or hour == 18 else ''
        report.append(f"{hour:02d}:00 {bar} {count:>4}{marker}")

    report.append("")
    report.append("说明: 👈 标记表示中午 12 点和下午 6 点（常见的高峰时段）")
    report.append("")

    # 星期热图
    report.append("=" * 140)
    report.append("📅 提交时段热图（按星期）")
    report.append("=" * 140)

    day_names_cn = {
        'Monday': '周一', 'Tuesday': '周二', 'Wednesday': '周三',
        'Thursday': '周四', 'Friday': '周五', 'Saturday': '周六', 'Sunday': '周日'
    }

    daily_max = max(heatmap['daily'].values()) if heatmap['daily'] else 0
    for day_en, day_cn in day_names_cn.items():
        count = heatmap['daily'].get(day_en, 0)
        bar_length = int((count / daily_max) * 40) if daily_max > 0 else 0
        bar = '█' * bar_length
        report.append(f"{day_cn} {bar} {count:>4}")

    report.append("")

    # 月度趋势
    if heatmap['monthly']:
        report.append("=" * 140)
        report.append("📈 月度提交趋势")
        report.append("=" * 140)

        monthly_items = list(heatmap['monthly'].items())[-12:]  # 最近12个月
        monthly_max = max(count for _, count in monthly_items) if monthly_items else 0

        for month, count in monthly_items:
            bar_length = int((count / monthly_max) * 30) if monthly_max > 0 else 0
            bar = '█' * bar_length
            report.append(f"{month} {bar} {count}")

        report.append("")

    # 提交信息质量分析
    report.append("=" * 140)
    report.append("✍️  提交信息质量分析")
    report.append("=" * 140)
    report.append(f"约定式提交规范符合率: {conventional['compliance_rate']:.1f}%")
    report.append(f"符合规范的提交数: {conventional['conventional_count']} / {conventional['total_count']}")

    if conventional['type_distribution']:
        report.append("")
        report.append("提交类型分布:")
        for commit_type, count in sorted(conventional['type_distribution'].items(),
                                        key=lambda x: x[1], reverse=True):
            percentage = (count / conventional['conventional_count']) * 100
            bar_length = int(percentage / 2)
            bar = '█' * bar_length
            report.append(f"  {commit_type:<12} {bar} {count:>4} ({percentage:>5.1f}%)")

    # 质量评估
    report.append("")
    report.append("质量评估:")
    if conventional['compliance_rate'] >= 80:
        report.append("  ✅ 优秀 - 提交信息规范，符合约定式提交标准")
    elif conventional['compliance_rate'] >= 50:
        report.append("  ⚠️  一般 - 部分提交符合规范，建议改进")
    else:
        report.append("  ❌ 需改进 - 提交信息不够规范，建议使用约定式提交格式")

    # 信息长度评估
    if patterns['avg_message_length'] >= 50:
        length_status = "✅ 良好 - 提交信息详细"
    elif patterns['avg_message_length'] >= 20:
        length_status = "⚠️  一般 - 建议提供更详细的提交说明"
    else:
        length_status = "❌ 简短 - 提交信息过于简短"
    report.append(f"  {length_status}")

    report.append("")

    # 活跃时段分析
    report.append("=" * 140)
    report.append("🎯 活跃时段分析")
    report.append("=" * 140)

    if heatmap['hourly']:
        peak_hour = max(heatmap['hourly'].items(), key=lambda x: x[1])
        report.append(f"最活跃小时: {peak_hour[0]:02d}:00 ({peak_hour[1]} 次提交)")

    if heatmap['daily']:
        peak_day = max(heatmap['daily'].items(), key=lambda x: x[1])
        day_cn = day_names_cn.get(peak_day[0], peak_day[0])
        report.append(f"最活跃日期: {day_cn} ({peak_day[1]} 次提交)")

    # 工作日 vs 周末
    workdays = sum(heatmap['daily'].get(day, 0) for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
    weekends = sum(heatmap['daily'].get(day, 0) for day in ['Saturday', 'Sunday'])
    total = workdays + weekends

    if total > 0:
        report.append("")
        report.append(f"工作日提交: {workdays} ({workdays/total*100:.1f}%)")
        report.append(f"周末提交: {weekends} ({weekends/total*100:.1f}%)")

    report.append("")

    # 建议
    report.append("=" * 140)
    report.append("💡 改进建议")
    report.append("=" * 140)

    suggestions = []

    if conventional['compliance_rate'] < 80:
        suggestions.append("• 采用约定式提交规范（Conventional Commits）")
        suggestions.append("• 使用 feat、fix、docs、style、refactor、test、chore 等类型前缀")
        suggestions.append("• 格式示例: feat: 添加用户登录功能")

    if patterns['avg_message_length'] < 30:
        suggestions.append("• 提交信息应该更详细，说明做了什么修改")

    if workdays > weekends * 3:
        suggestions.append("• 注意工作与生活的平衡，避免过度加班")

    if heatmap['hourly'].get(22, 0) > 0 or heatmap['hourly'].get(23, 0) > 0:
        suggestions.append("• 减少深夜提交，注意健康")

    if suggestions:
        for suggestion in suggestions:
            report.append(suggestion)
    else:
        report.append("✅ 提交模式良好，继续保持！")

    report.append("")
    report.append("=" * 140)

    return '\n'.join(report)

def save_report(report, output_file):
    """保存报告到文件"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    print("🔍 Git 提交历史分析器")
    print("=" * 60)

    # 检查是否在 Git 仓库中
    check_git_repo()

    # 获取提交数据
    print("📥 正在获取提交数据...")
    commits = fetch_commits()

    if not commits:
        print("⚠️  没有找到任何提交记录")
        sys.exit(0)

    print(f"✅ 成功获取 {len(commits)} 条提交记录")

    # 生成报告
    print("📊 正在分析提交数据...")
    report = generate_report(commits)

    # 保存报告
    output_file = 'commit_analysis_report.txt'
    print("📝 正在生成分析报告...")
    save_report(report, output_file)
    print(f"✅ 报告已保存到: {output_file}")

    # 显示摘要
    print("\n" + "=" * 60)
    print("📋 分析摘要")
    print("=" * 60)

    contributors = analyze_contributors(commits)
    patterns = analyze_commit_patterns(commits)

    print(f"  总提交数: {patterns['total_commits']}")
    print(f"  贡献者数: {len(contributors)}")
    print(f"  平均频率: {patterns['commits_per_day']:.2f} 提交/天")

    if contributors:
        print(f"  顶级贡献者: {contributors[0]['author']} ({contributors[0]['commits']} 提交)")

    conventional = check_conventional_commits(commits)
    print(f"  规范符合率: {conventional['compliance_rate']:.1f}%")

    print(f"\n  📄 完整报告: {output_file}")

if __name__ == '__main__':
    main()
