#!/usr/bin/env python3
"""
Task Completion Tracker - 任务完成追踪分析
"""

import subprocess
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter


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

# 约定式提交类型
COMMIT_TYPES = {
    'feat': '新功能',
    'fix': 'Bug 修复',
    'refactor': '重构',
    'docs': '文档',
    'test': '测试',
    'chore': '杂项',
    'style': '代码风格',
    'perf': '性能优化',
    'ci': 'CI/CD',
    'build': '构建',
    'revert': '回滚',
}

def get_git_commits(days=90):
    """获取指定天数内的 Git 提交历史"""
    since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    result = subprocess.run([
        'git', 'log',
        f'--since={since_date}',
        '--pretty=format:%H|%ai|%s',
        '--no-merges',
    ], capture_output=True, text=True)

    if result.returncode != 0:
        return []

    lines = result.stdout.strip().split('\n')
    commits = []

    for line in lines:
        if not line or '|' not in line:
            continue

        parts = line.split('|', 2)
        if len(parts) == 3:
            commit_hash, commit_date, commit_msg = parts
            commits.append({
                'hash': commit_hash,
                'date': parse_git_date(commit_date),
                'message': commit_msg.strip(),
            })

    return commits

def parse_commit_type(message):
    """解析提交消息中的约定式提交类型"""
    # 匹配 type: 或 type(scope): 格式
    match = re.match(r'^(\w+)(\([^)]*\))?:', message)
    if match:
        commit_type = match.group(1).lower()
        return commit_type if commit_type in COMMIT_TYPES else 'other'
    return 'other'

def analyze_commits(commits):
    """分析提交历史，统计任务完成情况"""
    if not commits:
        return {
            'total': 0,
            'by_type': Counter(),
            'by_week': defaultdict(lambda: defaultdict(int)),
            'by_month': defaultdict(lambda: defaultdict(int)),
            'by_day': defaultdict(int),
            'date_range': None,
        }

    by_type = Counter()
    by_week = defaultdict(lambda: defaultdict(int))
    by_month = defaultdict(lambda: defaultdict(int))
    by_day = defaultdict(int)

    start_date = commits[-1]['date']
    end_date = commits[0]['date']

    for commit in commits:
        commit_type = parse_commit_type(commit['message'])
        commit_date = commit['date']

        by_type[commit_type] += 1

        # 按周统计（使用 ISO 周数）
        week_key = commit_date.strftime('%Y-W%W')
        by_week[week_key][commit_type] += 1

        # 按月统计
        month_key = commit_date.strftime('%Y-%m')
        by_month[month_key][commit_type] += 1

        # 按星期几统计
        day_key = commit_date.strftime('%A')  # Monday, Tuesday, etc.
        by_day[day_key] += 1

    return {
        'total': len(commits),
        'by_type': by_type,
        'by_week': by_week,
        'by_month': by_month,
        'by_day': by_day,
        'date_range': (start_date, end_date),
    }

def calculate_velocity(by_week, by_month):
    """计算项目速度"""
    weekly_velocity = []
    monthly_velocity = []

    for week, types in sorted(by_week.items()):
        weekly_velocity.append((week, sum(types.values())))

    for month, types in sorted(by_month.items()):
        monthly_velocity.append((month, sum(types.values())))

    return weekly_velocity, monthly_velocity

def generate_report(stats, days=90):
    """生成任务完成分析报告"""
    now = datetime.now()
    since_date = (now - timedelta(days=days)).strftime('%Y-%m-%d')

    report = []
    report.append("=" * 140)
    report.append("任务完成追踪分析报告 (Task Completion Analysis)")
    report.append(f"分析时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"分析周期: {since_date} 至今 ({days} 天)")
    report.append("=" * 140)
    report.append("")

    if stats['total'] == 0:
        report.append("⚠️  在指定时间范围内没有找到提交记录")
        report.append("")
        report.append("可能原因:")
        report.append("  - 仓库是新建的，还没有提交")
        report.append("  - 指定的时间范围内没有活动")
        report.append("  - 不是 Git 仓库")
        return '\n'.join(report)

    report.append(f"总任务数: {stats['total']}")
    report.append("")

    # 任务类型分布
    report.append("=" * 140)
    report.append("📊 任务类型分布")
    report.append("=" * 140)

    by_type = stats['by_type']
    total_tasks = stats['total']

    # 按数量排序
    sorted_types = sorted(by_type.items(), key=lambda x: x[1], reverse=True)

    for commit_type, count in sorted_types:
        type_name = COMMIT_TYPES.get(commit_type, commit_type.capitalize())
        percentage = (count / total_tasks * 100) if total_tasks > 0 else 0
        bar_length = int(percentage / 2)
        bar = '█' * bar_length
        report.append(f"  {type_name:<15} {count:>4} ({percentage:>5.1f}%) {bar}")

    report.append("")

    # 新功能 vs Bug 修复
    feat_count = by_type.get('feat', 0)
    fix_count = by_type.get('fix', 0)
    refactor_count = by_type.get('refactor', 0)

    report.append("关键指标:")
    report.append(f"  🎯 新功能 (feat):       {feat_count} ({feat_count/total_tasks*100:.1f}%)")
    report.append(f"  🐛 Bug 修复 (fix):       {fix_count} ({fix_count/total_tasks*100:.1f}%)")
    report.append(f"  🔧 重构 (refactor):     {refactor_count} ({refactor_count/total_tasks*100:.1f}%)")

    feat_fix_ratio = fix_count / feat_count if feat_count > 0 else 0
    report.append(f"  📈 Bug/Feature 比例:    {feat_fix_ratio:.2f} (每个功能对应的 bug 数)")

    report.append("")

    # 项目速度分析
    report.append("=" * 140)
    report.append("🚀 项目速度分析")
    report.append("=" * 140)

    weekly_velocity, monthly_velocity = calculate_velocity(stats['by_week'], stats['by_month'])

    if weekly_velocity:
        avg_weekly = sum(v for _, v in weekly_velocity) / len(weekly_velocity)
        report.append(f"每周平均完成: {avg_weekly:.1f} 个任务")
        report.append("")

        report.append("最近 8 周任务完成情况:")
        for week, count in weekly_velocity[-8:]:
            report.append(f"  {week}:  {count:>3} 个任务")

        # 速度趋势
        if len(weekly_velocity) >= 4:
            recent_avg = sum(v for _, v in weekly_velocity[-4:]) / 4
            earlier_avg = sum(v for _, v in weekly_velocity[-8:-4]) / 4 if len(weekly_velocity) >= 8 else recent_avg

            if recent_avg > earlier_avg * 1.1:
                trend = "📈 上升趋势"
            elif recent_avg < earlier_avg * 0.9:
                trend = "📉 下降趋势"
            else:
                trend = "➡️ 稳定"

            report.append(f"\n趋势: {trend} (最近4周平均 {recent_avg:.1f} vs 前4周平均 {earlier_avg:.1f})")

    report.append("")

    if monthly_velocity:
        report.append("月度任务完成情况:")
        for month, count in monthly_velocity:
            report.append(f"  {month}:  {count:>3} 个任务")

    report.append("")

    # 活跃时段分析
    report.append("=" * 140)
    report.append("📅 活跃时段分析")
    report.append("=" * 140)

    by_day = stats['by_day']
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    max_day_count = max(by_day.values()) if by_day else 1

    for day in day_order:
        count = by_day.get(day, 0)
        if count > 0:
            bar_length = int(count / max_day_count * 30) if max_day_count > 0 else 0
            bar = '█' * bar_length
            report.append(f"  {day:<10} {count:>3} {bar}")

    report.append("")

    # 任务类型趋势（按月）
    report.append("=" * 140)
    report.append("📈 任务类型趋势（按月）")
    report.append("=" * 140)

    by_month = stats['by_month']
    for month in sorted(by_month.keys())[-6:]:  # 最近6个月
        types = by_month[month]
        total = sum(types.values())
        report.append(f"\n{month} (总计 {total} 个任务):")

        for commit_type in ['feat', 'fix', 'refactor', 'docs', 'test', 'chore']:
            count = types.get(commit_type, 0)
            if count > 0:
                type_name = COMMIT_TYPES.get(commit_type, commit_type)
                report.append(f"  {type_name:<10} {count:>3}")

    report.append("")

    # 洞察和建议
    report.append("=" * 140)
    report.append("💡 洞察与建议")
    report.append("=" * 140)

    insights = []

    # Bug/Feature 比例分析
    if feat_count > 0 and fix_count > 0:
        if feat_fix_ratio > 0.5:
            insights.append(f"⚠️  Bug/Feature 比例较高 ({feat_fix_ratio:.2f})，建议关注代码质量")
        elif feat_fix_ratio < 0.2:
            insights.append(f"✅ Bug/Feature 比例健康 ({feat_fix_ratio:.2f})")

    # 重构比例
    refactor_ratio = refactor_count / total_tasks if total_tasks > 0 else 0
    if refactor_ratio > 0.15:
        insights.append(f"🔧 重构占比 {refactor_ratio*100:.1f}%，说明团队在积极维护代码质量")
    elif refactor_ratio < 0.05:
        insights.append(f"💡 重构占比较低 ({refactor_ratio*100:.1f}%)，考虑定期重构以避免技术债务")

    # 测试覆盖
    test_count = by_type.get('test', 0)
    test_ratio = test_count / total_tasks if total_tasks > 0 else 0
    if test_ratio > 0.1:
        insights.append(f"✅ 测试相关提交占 {test_ratio*100:.1f}%，团队重视测试")
    else:
        insights.append(f"💡 测试相关提交仅占 {test_ratio*100:.1f}%，建议增加测试投入")

    # 文档
    docs_count = by_type.get('docs', 0)
    if docs_count > 0:
        insights.append(f"📚 有 {docs_count} 个文档相关提交，保持文档更新很重要")

    # 速度趋势
    if weekly_velocity and len(weekly_velocity) >= 4:
        recent_avg = sum(v for _, v in weekly_velocity[-4:]) / 4
        if recent_avg < 5:
            insights.append(f"📊 最近每周平均完成 {recent_avg:.1f} 个任务，可能需要关注团队容量")
        elif recent_avg > 20:
            insights.append(f"📊 最近每周平均完成 {recent_avg:.1f} 个任务，团队效率很高")

    # 输出洞察
    for insight in insights:
        report.append(insight)

    report.append("")
    report.append("通用建议:")
    report.append("  - 保持稳定的提交频率，避免过度劳累")
    report.append("  - 平衡新功能开发和 Bug 修复")
    report.append("  - 定期进行代码重构，避免技术债务积累")
    report.append("  - 保持测试和文档的更新")
    report.append("  - 关注项目速度趋势，及时调整计划")

    return '\n'.join(report)

def save_report(report, output_file):
    """保存报告到文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

def main():
    print("🔍 正在分析任务完成情况...")

    commits = get_git_commits(days=90)
    print(f"✅ 获取到 {len(commits)} 个提交记录")

    if not commits:
        print("⚠️  在过去 90 天内没有找到提交记录")
        print("📊 正在生成空报告...")
        stats = {
            'total': 0,
            'by_type': Counter(),
            'by_week': defaultdict(lambda: defaultdict(int)),
            'by_month': defaultdict(lambda: defaultdict(int)),
            'by_day': defaultdict(int),
            'date_range': None,
        }
    else:
        print("📊 正在分析任务模式...")
        stats = analyze_commits(commits)
        print(f"✅ 分析了 {stats['total']} 个任务")

    print("📝 正在生成分析报告...")
    report = generate_report(stats, days=90)

    output_file = 'task_completion_report.txt'
    save_report(report, output_file)
    print(f"✅ 报告已保存到: {output_file}")

    print("\n" + "=" * 60)
    print("📋 分析摘要")
    print("=" * 60)
    print(f"  分析周期: 最近 90 天")
    print(f"  总任务数: {stats['total']}")

    if stats['total'] > 0:
        by_type = stats['by_type']
        feat_count = by_type.get('feat', 0)
        fix_count = by_type.get('fix', 0)
        print(f"  新功能: {feat_count}")
        print(f"  Bug 修复: {fix_count}")

        weekly_velocity, _ = calculate_velocity(stats['by_week'], stats['by_month'])
        if weekly_velocity:
            avg_weekly = sum(v for _, v in weekly_velocity) / len(weekly_velocity)
            print(f"  周平均: {avg_weekly:.1f} 个任务")

    print(f"  报告文件: {output_file}")

if __name__ == '__main__':
    main()
