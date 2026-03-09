#!/usr/bin/env python3
"""
编码时间分析器 - 分析 Git 提交时间模式，识别高效时段和编码习惯
"""

import subprocess
import sys
from datetime import datetime
from collections import Counter, defaultdict
from pathlib import Path

def check_git_repo():
    """检查是否在 Git 仓库中"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False

def fetch_commits():
    """获取 Git 提交记录，包含时间戳"""
    try:
        result = subprocess.run(
            'git log --all --date=format:"%Y-%m-%d %H:%M" --pretty=format:"%H|%ad|%an"',
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            raise Exception(f"Git log 失败: {result.stderr}")

        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('|')
                if len(parts) >= 2:
                    commits.append({
                        'hash': parts[0],
                        'date': parts[1],
                        'author': parts[2] if len(parts) > 2 else 'Unknown'
                    })

        return commits

    except subprocess.TimeoutExpired:
        raise Exception("Git log 执行超时，仓库可能太大")
    except Exception as e:
        raise Exception(f"获取提交记录失败: {str(e)}")

def parse_commits(commits):
    """解析提交时间，按小时和星期分组"""
    hourly_data = Counter()
    daily_data = Counter()
    hourly_by_day = defaultdict(lambda: Counter())

    weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

    for commit in commits:
        try:
            dt = datetime.strptime(commit['date'], '%Y-%m-%d %H:%M')
            hour = dt.hour
            weekday = dt.weekday()  # 0=Monday, 6=Sunday

            hourly_data[hour] += 1
            daily_data[weekday] += 1
            hourly_by_day[weekday][hour] += 1

        except ValueError as e:
            print(f"警告: 无法解析提交时间 {commit['date']}: {e}")
            continue

    return hourly_data, daily_data, hourly_by_day, weekday_names

def generate_hourly_chart(hourly_data, max_commits):
    """生成每小时提交分布的 ASCII 图表"""
    chart = []
    chart.append("每小时提交分布 (24小时):")
    chart.append("")

    for hour in range(24):
        count = hourly_data.get(hour, 0)
        bar_length = int((count / max_commits) * 50) if max_commits > 0 else 0
        bar = '█' * bar_length

        time_label = f"{hour:02d}:00"
        chart.append(f"  {time_label} │ {bar} {count}")

    return '\n'.join(chart)

def generate_heatmap(hourly_by_day, weekday_names):
    """生成星期 x 小时的热力图"""
    heatmap = []
    heatmap.append("提交热力图 (星期 x 小时):")
    heatmap.append("")
    heatmap.append("        00  01  02  03  04  05  06  07  08  09  10  11  12  13  14  15  16  17  18  19  20  21  22  23")
    heatmap.append("        " + "─" * 96)

    intensity_chars = [' ', '░', '▒', '▓', '█']

    for day in range(7):
        row = [weekday_names[day].ljust(8) + '│']

        for hour in range(24):
            count = hourly_by_day[day].get(hour, 0)
            if count == 0:
                row.append('  ')
            else:
                max_count = max(hourly_by_day[day].values()) if hourly_by_day[day] else 1
                intensity = int((count / max_count) * 4)
                intensity = min(intensity, 4)
                row.append(f'{intensity_chars[intensity]} ')

        heatmap.append(''.join(row))

    return '\n'.join(heatmap)

def generate_report(commits, hourly_data, daily_data, hourly_by_day, weekday_names):
    """生成完整的分析报告"""
    report = []
    report.append("=" * 100)
    report.append("编码时间分析报告")
    report.append("=" * 100)
    report.append("")

    if not commits:
        report.append("❌ 未找到任何提交记录")
        report.append("")
        report.append("提示: 请确保当前目录是一个 Git 仓库，并且包含提交历史")
        return '\n'.join(report)

    total_commits = len(commits)
    first_commit = commits[-1]['date']
    last_commit = commits[0]['date']

    report.append(f"📊 统计概览")
    report.append(f"  总提交数: {total_commits}")
    report.append(f"  时间范围: {first_commit} ~ {last_commit}")
    report.append("")

    report.append("=" * 100)
    report.append("📈 每日提交分布 (星期)")
    report.append("=" * 100)
    report.append("")

    weekday_total = sum(daily_data.values())
    for day in range(7):
        count = daily_data.get(day, 0)
        percentage = (count / weekday_total * 100) if weekday_total > 0 else 0
        bar = '█' * int(percentage / 2)
        report.append(f"  {weekday_names[day]} │ {bar:<50} {count:4d} 次 ({percentage:5.1f}%)")

    report.append("")

    workday_commits = sum(daily_data.get(i, 0) for i in range(5))
    weekend_commits = sum(daily_data.get(i, 0) for i in range(5, 7))

    report.append("工作日 vs 周末:")
    report.append(f"  工作日 (周一至周五): {workday_commits} 次 ({workday_commits/weekday_total*100:.1f}%)")
    report.append(f"  周末 (周六、周日):     {weekend_commits} 次 ({weekend_commits/weekday_total*100:.1f}%)")
    report.append("")

    report.append("=" * 100)
    report.append("⏰ 每小时提交分布")
    report.append("=" * 100)
    report.append("")

    max_hourly = max(hourly_data.values()) if hourly_data else 0
    report.append(generate_hourly_chart(hourly_data, max_hourly))
    report.append("")

    peak_hours = sorted(hourly_data.items(), key=lambda x: x[1], reverse=True)[:3]
    report.append("🔥 最活跃时段 (Top 3):")
    for hour, count in peak_hours:
        report.append(f"  {hour:02d}:00 - {hour:02d}:59 │ {count} 次提交")
    report.append("")

    morning = sum(hourly_data.get(h, 0) for h in range(6, 12))
    afternoon = sum(hourly_data.get(h, 0) for h in range(12, 18))
    evening = sum(hourly_data.get(h, 0) for h in range(18, 24))
    night = sum(hourly_data.get(h, 0) for h in range(0, 6))

    report.append("时段分布:")
    report.append(f"  早晨 (06:00-11:59): {morning} 次 ({morning/total_commits*100:.1f}%)")
    report.append(f"  下午 (12:00-17:59): {afternoon} 次 ({afternoon/total_commits*100:.1f}%)")
    report.append(f"  晚上 (18:00-23:59): {evening} 次 ({evening/total_commits*100:.1f}%)")
    report.append(f"  深夜 (00:00-05:59): {night} 次 ({night/total_commits*100:.1f}%)")
    report.append("")

    report.append("=" * 100)
    report.append("🗺️ 提交热力图")
    report.append("=" * 100)
    report.append("")
    report.append(generate_heatmap(hourly_by_day, weekday_names))
    report.append("")

    report.append("=" * 100)
    report.append("💡 编码习惯洞察")
    report.append("=" * 100)
    report.append("")

    most_active_day = daily_data.most_common(1)[0] if daily_data else (0, 0)
    most_active_hour = hourly_data.most_common(1)[0] if hourly_data else (0, 0)

    report.append(f"最活跃的星期: {weekday_names[most_active_day[0]]} ({most_active_day[1]} 次提交)")
    report.append(f"最活跃的时段: {most_active_hour[0]:02d}:00-{most_active_hour[0]:02d}:59 ({most_active_hour[1]} 次提交)")
    report.append("")

    if workday_commits > weekend_commits:
        ratio = workday_commits / weekend_commits if weekend_commits > 0 else float('inf')
        report.append(f"工作日编码: 是工作日提交者，工作日/周末提交比约为 {ratio:.1f}:1")
    else:
        ratio = weekend_commits / workday_commits if workday_commits > 0 else float('inf')
        report.append(f"周末编码: 是周末提交者，周末/工作日提交比约为 {ratio:.1f}:1")
    report.append("")

    if morning + afternoon > evening + night:
        day_ratio = (morning + afternoon) / (evening + night) if (evening + night) > 0 else float('inf')
        report.append(f"白天编码: 倾向于白天编码，白天/晚上提交比约为 {day_ratio:.1f}:1")
    else:
        night_ratio = (evening + night) / (morning + afternoon) if (morning + afternoon) > 0 else float('inf')
        report.append(f"夜间编码: 倾向于夜间编码，晚上/白天提交比约为 {night_ratio:.1f}:1")
    report.append("")

    avg_per_day = total_commits / 7 if weekday_total > 0 else 0
    report.append(f"平均每天: {avg_per_day:.1f} 次提交")
    report.append("")

    report.append("=" * 100)
    report.append("📝 建议")
    report.append("=" * 100)
    report.append("")

    if morning > afternoon and morning > evening and morning > night:
        report.append("✨ 早晨型开发者: 你在早晨最有生产力，建议安排重要任务在早上")
    elif afternoon > morning and afternoon > evening and afternoon > night:
        report.append("✨ 下午型开发者: 你在下午最有生产力，建议安排重要任务在下午")
    elif evening > morning and evening > afternoon and evening > night:
        report.append("✨ 晚间型开发者: 你在晚上最有生产力，建议安排重要任务在晚上")
    elif night > 0:
        report.append("✨ 夜猫型开发者: 你经常在深夜编码，注意劳逸结合")

    if workday_commits > weekend_commits * 2:
        report.append("💼 工作日专注: 你的工作日投入度很高，周末可以适当休息")
    elif weekend_commits > workday_commits:
        report.append("🎨 周末程序员: 你在周末也很活跃，可能是开源爱好者或学习者")

    report.append("")
    report.append("=" * 100)
    report.append("报告生成完成")
    report.append("=" * 100)

    return '\n'.join(report)

def save_report(report, output_file):
    """保存报告到文件"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        return True
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")
        return False

def main():
    """主函数"""
    print("🔍 正在检查 Git 仓库...")

    if not check_git_repo():
        print("❌ 错误: 当前目录不是一个 Git 仓库")
        print("💡 提示: 请在 Git 仓库目录中运行此脚本")
        sys.exit(1)

    print("✅ Git 仓库检查通过")
    print("📊 正在获取提交记录...")

    try:
        commits = fetch_commits()

        if not commits:
            print("❌ 未找到任何提交记录")
            print("💡 提示: 仓库可能没有提交历史")
            sys.exit(1)

        print(f"✅ 成功获取 {len(commits)} 条提交记录")
        print("🔬 正在分析编码时间模式...")

        hourly_data, daily_data, hourly_by_day, weekday_names = parse_commits(commits)

        print("📝 正在生成分析报告...")
        report = generate_report(commits, hourly_data, daily_data, hourly_by_day, weekday_names)

        output_file = 'time_tracker_report.txt'
        if save_report(report, output_file):
            print(f"✅ 报告已保存到: {output_file}")
        else:
            print("❌ 报告保存失败")
            sys.exit(1)

        print("\n" + "=" * 60)
        print("📋 分析摘要")
        print("=" * 60)

        total_commits = len(commits)
        workday_commits = sum(daily_data.get(i, 0) for i in range(5))
        weekend_commits = sum(daily_data.get(i, 0) for i in range(5, 7))

        print(f"  总提交数: {total_commits}")
        print(f"  工作日: {workday_commits} 次 ({workday_commits/total_commits*100:.1f}%)")
        print(f"  周  末: {weekend_commits} 次 ({weekend_commits/total_commits*100:.1f}%)")

        if hourly_data:
            peak_hour = hourly_data.most_common(1)[0]
            print(f"  最活跃时段: {peak_hour[0]:02d}:00-{peak_hour[0]:02d}:59 ({peak_hour[1]} 次)")

        most_active_day = daily_data.most_common(1)[0]
        print(f"  最活跃星期: {weekday_names[most_active_day[0]]} ({most_active_day[1]} 次)")
        print(f"  报告文件: {output_file}")

    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
