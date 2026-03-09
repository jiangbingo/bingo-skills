#!/usr/bin/env python3
"""
上下文切换监控分析脚本
通过 Git 提交历史分析工作模式，识别上下文切换频率和工作区分散度
"""

import subprocess
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import os
import sys


def run_git_command(cmd):
    """执行 Git 命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"错误: Git 命令执行失败: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("错误: 未找到 Git 命令，请确保已安装 Git")
        sys.exit(1)


def get_git_commits(days=30):
    """获取指定天数内的 Git 提交记录"""
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    cmd = (
        f'git log --since="{since_date}" --pretty=format:"%H|%ai|%s" '
        f'--name-only'
    )

    output = run_git_command(cmd)
    return parse_commits(output)


def parse_commits(output):
    """解析 Git 日志输出"""
    commits = []
    lines = output.strip().split('\n')

    current_commit = None
    for line in lines:
        if '|' in line:  # 提交信息行
            if current_commit:
                commits.append(current_commit)

            parts = line.split('|')
            current_commit = {
                'hash': parts[0],
                'date': parts[1],
                'message': parts[2] if len(parts) > 2 else '',
                'files': []
            }
        elif current_commit and line.strip():  # 文件路径行
            current_commit['files'].append(line.strip())

    if current_commit:
        commits.append(current_commit)

    return commits


def extract_module(file_path):
    """从文件路径提取模块名称（目录名）"""
    # 移除常见的根目录
    path = file_path.replace('src/', '').replace('lib/', '').replace('app/', '')

    # 获取第一层目录作为模块
    parts = path.split('/')
    if len(parts) > 1:
        return parts[0]

    # 如果没有目录，根据文件类型分类
    ext = os.path.splitext(file_path)[1]
    if ext in ['.py', '.js', '.ts', '.java', '.go', '.rs']:
        return 'code'
    elif ext in ['.md', '.txt', '.rst']:
        return 'docs'
    elif ext in ['.yml', '.yaml', '.json', '.toml', '.ini']:
        return 'config'
    elif ext in ['.css', '.scss', '.less', '.html', '.jsx', '.tsx']:
        return 'frontend'
    else:
        return 'other'


def detect_context_switches(commits, time_threshold_minutes=30):
    """检测上下文切换"""
    if len(commits) < 2:
        return []

    switches = []
    time_threshold = timedelta(minutes=time_threshold_minutes)

    for i in range(1, len(commits)):
        prev = commits[i - 1]
        curr = commits[i]

        prev_date = datetime.fromisoformat(prev['date'].replace('+00:00', ''))
        curr_date = datetime.fromisoformat(curr['date'].replace('+00:00', ''))

        # 获取主要模块
        prev_modules = Counter(extract_module(f) for f in prev['files'])
        curr_modules = Counter(extract_module(f) for f in curr['files'])

        prev_main = prev_modules.most_common(1)[0][0] if prev_modules else 'unknown'
        curr_main = curr_modules.most_common(1)[0][0] if curr_modules else 'unknown'

        # 检测切换条件
        is_module_switch = prev_main != curr_main
        is_time_gap = (curr_date - prev_date) > time_threshold

        switch_type = []
        if is_module_switch:
            switch_type.append('module')
        if is_time_gap:
            switch_type.append('time_gap')

        if switch_type:
            switches.append({
                'from_commit': prev['hash'][:8],
                'to_commit': curr['hash'][:8],
                'from_module': prev_main,
                'to_module': curr_main,
                'from_date': prev['date'],
                'to_date': curr['date'],
                'time_gap': str(curr_date - prev_date),
                'switch_type': switch_type,
                'message': curr['message']
            })

    return switches


def calculate_fragmentation_index(commits, switches):
    """计算工作区分散度指数 (0-100)"""
    if len(commits) < 2:
        return 0

    # 基于切换频率的分散度
    switch_ratio = len(switches) / len(commits) * 100

    # 基于模块数量的分散度
    all_modules = set()
    for commit in commits:
        for f in commit['files']:
            all_modules.add(extract_module(f))

    module_diversity = len(all_modules) * 5

    # 组合指数
    fragmentation = min(100, (switch_ratio * 0.7 + module_diversity * 0.3))

    return round(fragmentation, 1)


def identify_focus_periods(commits, switches, min_duration_minutes=45):
    """识别专注时段"""
    if len(commits) < 3:
        return []

    focus_periods = []
    min_duration = timedelta(minutes=min_duration_minutes)

    # 找出没有切换或切换很少的连续提交
    period_start = 0
    switch_count_in_period = 0

    for i, commit in enumerate(commits[1:], 1):
        # 检查这个提交是否是切换点
        is_switch_point = any(
            s['to_commit'] == commit['hash'][:8]
            for s in switches
        )

        if is_switch_point:
            switch_count_in_period += 1

        # 计算当前时段长度
        period_commits = commits[period_start:i + 1]
        if len(period_commits) >= 2:
            start_time = datetime.fromisoformat(period_commits[0]['date'].replace('+00:00', ''))
            end_time = datetime.fromisoformat(period_commits[-1]['date'].replace('+00:00', ''))
            duration = end_time - start_time

            # 如果持续时间足够且切换次数少
            if duration >= min_duration and switch_count_in_period <= 2:
                # 获取主要模块
                module_counter = Counter()
                for c in period_commits:
                    for f in c['files']:
                        module_counter[extract_module(f)] += 1

                main_module = module_counter.most_common(1)[0][0] if module_counter else 'unknown'

                focus_periods.append({
                    'start': period_commits[0]['date'],
                    'end': period_commits[-1]['date'],
                    'duration': str(duration),
                    'commits': len(period_commits),
                    'main_module': main_module,
                    'switches': switch_count_in_period
                })

            # 重置时段
            period_start = i
            switch_count_in_period = 0

    # 按时长排序
    focus_periods.sort(key=lambda x: x['duration'], reverse=True)

    return focus_periods[:10]  # 返回前10个专注时段


def generate_report(commits, switches, focus_periods):
    """生成分析报告"""
    if not commits:
        return "错误: 没有找到 Git 提交记录，请确保仓库有提交历史"

    report = []
    report.append("=" * 140)
    report.append("上下文切换分析报告")
    report.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 140)
    report.append("")

    # 基本统计
    time_span = datetime.fromisoformat(commits[-1]['date'].replace('+00:00', '')) - \
                datetime.fromisoformat(commits[0]['date'].replace('+00:00', ''))

    report.append("=" * 140)
    report.append("📊 基本统计")
    report.append("=" * 140)
    report.append(f"分析提交数: {len(commits)} 次")
    report.append(f"时间跨度: {time_span.days} 天")
    if time_span.days > 0:
        report.append(f"平均每日提交: {len(commits) / time_span.days:.1f} 次")
    report.append("")

    # 上下文切换分析
    report.append("=" * 140)
    report.append("🔄 上下文切换分析")
    report.append("=" * 140)
    report.append(f"总切换次数: {len(switches)} 次")

    if time_span.days > 0:
        daily_switches = len(switches) / time_span.days
        report.append(f"平均每日切换: {daily_switches:.1f} 次")

    module_switches = [s for s in switches if 'module' in s['switch_type']]
    time_gaps = [s for s in switches if 'time_gap' in s['switch_type']]

    report.append(f"  - 模块切换: {len(module_switches)} 次")
    report.append(f"  - 时间间隔切换: {len(time_gaps)} 次")
    report.append("")

    # 模块分布
    report.append("=" * 140)
    report.append("📁 工作模块分布")
    report.append("=" * 140)

    module_commits = Counter()
    for commit in commits:
        for f in commit['files']:
            module_commits[extract_module(f)] += 1

    report.append(f"涉及模块数: {len(module_commits)} 个")
    report.append("")
    report.append("模块活跃度 (Top 10):")
    for module, count in module_commits.most_common(10):
        percentage = count / sum(module_commits.values()) * 100
        report.append(f"  - {module:<20} {count:>4} 次提交 ({percentage:>5.1f}%)")
    report.append("")

    # 模块切换矩阵 (只显示主要的切换)
    report.append("=" * 140)
    report.append("🔀 主要模块切换路径")
    report.append("=" * 140)

    transitions = Counter()
    for s in switches:
        if 'module' in s['switch_type']:
            transitions[(s['from_module'], s['to_module'])] += 1

    if transitions:
        report.append("最常见的切换 (Top 10):")
        for (from_mod, to_mod), count in transitions.most_common(10):
            report.append(f"  - {from_mod:<15} → {to_mod:<15} ({count} 次)")
    else:
        report.append("  无显著的模块切换")
    report.append("")

    # 专注时段
    report.append("=" * 140)
    report.append("🎯 专注时段识别")
    report.append("=" * 140)
    report.append(f"识别到 {len(focus_periods)} 个专注时段 (最少45分钟连续工作)")
    report.append("")

    if focus_periods:
        report.append("最专注的时段 (Top 10):")
        report.append(f"{'开始时间':<20} {'持续时间':<12} {'提交数':<6} {'主要模块':<15} {'切换数'}")
        report.append("-" * 140)

        for period in focus_periods:
            start = period['start'][:16].replace('T', ' ')
            duration = period['duration']
            commits_count = period['commits']
            module = period['main_module']
            switches_count = period['switches']

            # 简化持续时间显示
            if 'day' in duration:
                duration = duration.split(',')[0]
            else:
                duration = duration.split('.')[0]

            report.append(f"{start:<20} {duration:<12} {commits_count:<6} {module:<15} {switches_count}")
    else:
        report.append("  未检测到明显的专注时段")
        report.append("  建议: 尝试减少中断，延长单次工作时长")
    report.append("")

    # 工作区分散度评估
    report.append("=" * 140)
    report.append("📈 工作区分散度评估")
    report.append("=" * 140)

    fragmentation = calculate_fragmentation_index(commits, switches)
    report.append(f"分散度指数: {fragmentation}/100")
    report.append("")

    # 分散度评级
    if fragmentation <= 25:
        grade = "优秀"
        description = "高度专注，工作模式非常好"
        emoji = "✅"
    elif fragmentation <= 50:
        grade = "良好"
        description = "适度专注，有一定上下文切换"
        emoji = "👍"
    elif fragmentation <= 75:
        grade = "需改进"
        description = "工作较分散，上下文切换较频繁"
        emoji = "⚠️"
    else:
        grade = "急需改进"
        description = "工作高度分散，注意力严重分散"
        emoji = "❌"

    report.append(f"{emoji} 专注度评级: {grade}")
    report.append(f"评估说明: {description}")
    report.append("")

    # 切换成本估算
    if switches:
        # 研究表明每次上下文切换需要约23分钟恢复专注
        recovery_time_minutes = 23
        total_recovery_hours = len(switches) * recovery_time_minutes / 60

        report.append("=" * 140)
        report.append("⏱️ 切换成本估算")
        report.append("=" * 140)
        report.append(f"总切换次数: {len(switches)} 次")
        report.append(f"估算恢复时间: {total_recovery_hours:.1f} 小时")
        report.append(f"  (基于研究: 每次切换平均需要 {recovery_time_minutes} 分钟恢复专注)")
        report.append("")

    # 优化建议
    report.append("=" * 140)
    report.append("💡 专注优化建议")
    report.append("=" * 140)

    recommendations = []

    if fragmentation > 50:
        recommendations.append("📌 批量处理相似任务，减少模块间切换")
        recommendations.append("📌 设置固定的时间块处理特定模块的工作")

    if len(focus_periods) < 3:
        recommendations.append("📌 每天至少安排一个45分钟以上的深度工作时段")
        recommendations.append("📌 在深度工作期间关闭通知和干扰")

    if len(module_switches) > len(commits) * 0.5:
        recommendations.append("📌 考虑使用原子提交，每次只完成一个相关任务")
        recommendations.append("📌 记录当前任务，被打断后能快速恢复上下文")

    if len(time_gaps) > len(commits) * 0.3:
        recommendations.append("📌 尝试减少工作时间碎片化，集中连续时间工作")

    # 通用建议
    general_tips = [
        "📌 使用番茄工作法 (25分钟专注 + 5分钟休息)",
        "📌 为每个任务创建独立分支，隔离工作上下文",
        "📌 定期回顾此报告，跟踪工作模式改善情况",
        "📌 在低精力时段处理琐事，高精力时段处理核心任务"
    ]

    if recommendations:
        report.append("针对性建议:")
        for rec in recommendations:
            report.append(f"  {rec}")
        report.append("")

    report.append("通用优化技巧:")
    for tip in general_tips:
        report.append(f"  {tip}")
    report.append("")

    # 详细的切换记录 (最近20次)
    if switches:
        report.append("=" * 140)
        report.append("📋 最近上下文切换记录 (最近20次)")
        report.append("=" * 140)
        report.append(f"{'时间':<20} {'切换类型':<15} {'从模块':<15} {'到模块':<15} {'间隔':<12} {'提交信息'}")
        report.append("-" * 140)

        for s in switches[-20:]:
            time = s['to_date'][:16].replace('T', ' ')
            switch_type = ','.join(s['switch_type'])
            from_mod = s['from_module']
            to_mod = s['to_module']
            gap = s['time_gap'].split('.')[0]
            msg = s['message'][:30]

            report.append(f"{time:<20} {switch_type:<15} {from_mod:<15} {to_mod:<15} {gap:<12} {msg}")

        report.append("")

    report.append("=" * 140)
    report.append("分析完成")
    report.append("=" * 140)

    return '\n'.join(report)


def save_report(report, output_file):
    """保存报告到文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)


def main():
    """主函数"""
    print("🔍 正在分析 Git 提交历史...")

    # 检查是否在 Git 仓库中
    try:
        run_git_command('git rev-parse --git-dir')
    except:
        print("错误: 当前目录不是 Git 仓库")
        sys.exit(1)

    # 获取提交记录 (默认最近30天)
    days = 30
    commits = get_git_commits(days)

    if not commits:
        print(f"警告: 最近 {days} 天内没有找到提交记录")
        print("尝试扩大时间范围...")
        commits = get_git_commits(days * 3)

        if not commits:
            print("错误: 仓库中没有足够的提交记录")
            sys.exit(1)

    print(f"✅ 成功获取 {len(commits)} 次提交记录")

    # 检测上下文切换
    print("🔄 正在检测上下文切换...")
    switches = detect_context_switches(commits)
    print(f"✅ 检测到 {len(switches)} 次上下文切换")

    # 识别专注时段
    print("🎯 正在识别专注时段...")
    focus_periods = identify_focus_periods(commits, switches)
    print(f"✅ 识别到 {len(focus_periods)} 个专注时段")

    # 生成报告
    print("📊 正在生成分析报告...")
    report = generate_report(commits, switches, focus_periods)

    # 保存报告
    output_file = 'context_switch_report.txt'
    save_report(report, output_file)
    print(f"✅ 报告已保存到: {output_file}")

    # 打印摘要
    print("\n" + "=" * 60)
    print("📋 分析摘要")
    print("=" * 60)

    fragmentation = calculate_fragmentation_index(commits, switches)
    if fragmentation <= 25:
        grade = "✅ 优秀"
    elif fragmentation <= 50:
        grade = "👍 良好"
    elif fragmentation <= 75:
        grade = "⚠️ 需改进"
    else:
        grade = "❌ 急需改进"

    print(f"  提交总数: {len(commits)}")
    print(f"  上下文切换: {len(switches)} 次")
    print(f"  专注时段: {len(focus_periods)} 个")
    print(f"  分散度指数: {fragmentation}/100")
    print(f"  专注度评级: {grade}")
    print(f"  报告文件: {output_file}")
    print("")


if __name__ == '__main__':
    main()
