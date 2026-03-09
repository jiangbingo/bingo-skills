#!/usr/bin/env python3
"""
代码复杂度分析工具
使用 radon (Python) 或 lizard (多语言) 分析代码复杂度
"""

import subprocess
import sys
import os
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def check_radon_installed():
    """检查 radon 是否已安装"""
    try:
        result = subprocess.run(
            ['radon', '--version'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def check_lizard_installed():
    """检查 lizard 是否已安装"""
    try:
        result = subprocess.run(
            ['lizard', '--version'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def analyze_with_radon():
    """使用 radon 分析 Python 代码复杂度"""
    if not check_radon_installed():
        print("⚠️  radon 未安装，尝试安装...")
        subprocess.run(['pip', 'install', 'radon'], capture_output=True)
        if not check_radon_installed():
            return None

    print("🔍 使用 radon 分析 Python 代码...")

    try:
        # 使用 radon 分析圈复杂度
        result = subprocess.run(
            ['radon', 'cc', '.', '-a', '-s', '-j'],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            return parse_radon_output(result.stdout)
        else:
            # 尝试不使用 JSON 格式
            result = subprocess.run(
                ['radon', 'cc', '.', '-a', '-s'],
                capture_output=True,
                text=True,
                timeout=60
            )
            return parse_radon_text_output(result.stdout)

    except subprocess.TimeoutExpired:
        print("⚠️  radon 分析超时")
        return None
    except Exception as e:
        print(f"⚠️  radon 分析失败: {e}")
        return None


def parse_radon_output(json_output):
    """解析 radon JSON 输出"""
    import json

    try:
        data = json.loads(json_output)
        files = {}

        for file_path, file_data in data.items():
            if isinstance(file_data, dict) and 'classes' in file_data:
                for class_name, class_data in file_data['classes'].items():
                    for method_name, method_data in class_data['methods'].items():
                        full_name = f"{file_path}:{class_name}.{method_name}"
                        files[full_name] = {
                            'type': 'method',
                            'complexity': method_data['complexity'],
                            'lineno': method_data['lineno'],
                            'endline': method_data['endline'],
                            'file': file_path,
                            'class': class_name,
                            'method': method_name,
                        }

        return organize_complexity_data(files, 'radon')

    except json.JSONDecodeError:
        return None


def parse_radon_text_output(text_output):
    """解析 radon 文本输出"""
    files = {}

    # radon 输出格式: FILE:lineno:lineno: CLASS.METHOD complexity -> CC
    pattern = r'^(.+?:(\d+):(\d+)):\s+(\S+)\s+(\S+)\s+->\s+(\d+)'

    for line in text_output.split('\n'):
        match = re.match(pattern, line)
        if match:
            location, lineno, endline, class_method, method_type, complexity = match.groups()

            # 解析 class.method
            if '.' in class_method:
                parts = class_method.split('.')
                if len(parts) >= 2:
                    class_name = parts[0]
                    method_name = '.'.join(parts[1:])
                else:
                    class_name = ''
                    method_name = class_method
            else:
                class_name = ''
                method_name = class_method

            files[location] = {
                'type': 'method',
                'complexity': int(complexity),
                'lineno': int(lineno),
                'endline': int(endline),
                'file': location.split(':')[0] if ':' in location else '',
                'class': class_name,
                'method': method_name,
            }

    return organize_complexity_data(files, 'radon')


def analyze_with_lizard():
    """使用 lizard 分析多语言代码复杂度"""
    if not check_lizard_installed():
        print("⚠️  lizard 未安装，尝试安装...")
        subprocess.run(['pip', 'install', 'lizard'], capture_output=True)
        if not check_lizard_installed():
            return None

    print("🔍 使用 lizard 分析代码复杂度...")

    try:
        result = subprocess.run(
            ['lizard', '.', '--CCN', '15'],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            return parse_lizard_output(result.stdout)
        else:
            return None

    except subprocess.TimeoutExpired:
        print("⚠️  lizard 分析超时")
        return None
    except Exception as e:
        print(f"⚠️  lizard 分析失败: {e}")
        return None


def parse_lizard_output(text_output):
    """解析 lizard 输出"""
    files = {}
    functions = []

    lines = text_output.split('\n')
    for line in lines:
        # lizard 格式: N lines N tokens N CC N params N loc file:class:function
        parts = line.split()
        if len(parts) >= 8:
            try:
                tokens = int(parts[1])
                if tokens == 0:  # 跳过摘要行
                    continue

                cc = int(parts[2])
                file_path = parts[-1]
                
                # 解析 file:class:function
                if ':' in file_path:
                    file_parts = file_path.split(':')
                    if len(file_parts) >= 3:
                        file_name = ':'.join(file_parts[:-2])
                        class_name = file_parts[-2]
                        function_name = file_parts[-1]
                    else:
                        file_name = file_parts[0]
                        class_name = ''
                        function_name = file_parts[-1] if len(file_parts) > 1 else ''
                else:
                    file_name = file_path
                    class_name = ''
                    function_name = ''

                key = f"{file_name}:{class_name}.{function_name}" if class_name else f"{file_name}:{function_name}"

                files[key] = {
                    'type': 'function',
                    'complexity': cc,
                    'file': file_name,
                    'class': class_name,
                    'method': function_name,
                    'tokens': tokens,
                }
            except (ValueError, IndexError):
                continue

    return organize_complexity_data(files, 'lizard')


def organize_complexity_data(files, tool):
    """组织复杂度数据"""
    if not files:
        return None

    # 按复杂度排序
    sorted_files = sorted(files.items(), key=lambda x: x[1]['complexity'], reverse=True)

    # 计算统计
    complexities = [f['complexity'] for f in files.values()]
    total_functions = len(files)
    avg_complexity = sum(complexities) / total_functions if total_functions > 0 else 0
    max_complexity = max(complexities) if complexities else 0

    # 按风险等级分类
    risk_levels = {
        'low': [],      # CC < 15
        'medium': [],   # CC 15-25
        'high': [],     # CC 25-50
        'critical': [], # CC > 50
    }

    for key, data in files.items():
        cc = data['complexity']
        if cc < 15:
            risk_levels['low'].append((key, cc))
        elif cc < 25:
            risk_levels['medium'].append((key, cc))
        elif cc < 50:
            risk_levels['high'].append((key, cc))
        else:
            risk_levels['critical'].append((key, cc))

    # 按文件分组
    file_complexity = defaultdict(list)
    for key, data in files.items():
        file_path = data.get('file', key.split(':')[0])
        file_complexity[file_path].append(data['complexity'])

    file_avg_complexity = {}
    for file_path, ccs in file_complexity.items():
        file_avg_complexity[file_path] = sum(ccs) / len(ccs)

    return {
        'tool': tool,
        'total_functions': total_functions,
        'avg_complexity': avg_complexity,
        'max_complexity': max_complexity,
        'sorted_files': sorted_files,
        'risk_levels': risk_levels,
        'file_complexity': dict(sorted(
            file_avg_complexity.items(),
            key=lambda x: x[1],
            reverse=True
        )),
    }


def get_complexity_level(cc):
    """获取复杂度等级"""
    if cc < 15:
        return 'Low', '🟢'
    elif cc < 25:
        return 'Medium', '🟡'
    elif cc < 50:
        return 'High', '🟠'
    else:
        return 'Critical', '🔴'


def generate_complexity_bar(cc, width=20):
    """生成复杂度可视化条"""
    if cc >= 50:
        filled = width
    else:
        filled = min(int(cc / 50 * width), width)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {cc}"


def generate_report(data):
    """生成复杂度报告"""
    if not data:
        return generate_no_analysis_report()

    lines = []
    lines.append("=" * 80)
    lines.append("📊 代码复杂度分析报告 (Code Complexity Analysis)")
    lines.append(f"⏰ 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"🔧 分析工具: {data['tool'].upper()}")
    lines.append("=" * 80)
    lines.append("")

    # 摘要统计
    lines.append("📈 总体统计")
    lines.append("-" * 80)
    lines.append(f"分析函数总数: {data['total_functions']:,}")
    lines.append(f"平均复杂度: {data['avg_complexity']:.2f}")
    lines.append(f"最高复杂度: {data['max_complexity']}")
    lines.append("")

    # 风险分布
    lines.append("🎯 风险等级分布")
    lines.append("-" * 80)
    risk_map = {
        'low': ('🟢', '低风险 (CC < 15)'),
        'medium': ('🟡', '中风险 (CC 15-25)'),
        'high': ('🟠', '高风险 (CC 25-50)'),
        'critical': ('🔴', '紧急风险 (CC > 50)'),
    }

    for level, (emoji, desc) in risk_map.items():
        count = len(data['risk_levels'][level])
        if count > 0:
            lines.append(f"{emoji} {desc}: {count} 个函数")

    lines.append("")

    # 紧急风险函数
    if data['risk_levels']['critical']:
        lines.append("🔴 紧急风险函数 (CC > 50)")
        lines.append("-" * 80)
        for key, cc in data['risk_levels']['critical'][:10]:
            lines.append(f"  {generate_complexity_bar(cc, 20)} {key}")
        if len(data['risk_levels']['critical']) > 10:
            lines.append(f"  ... 还有 {len(data['risk_levels']['critical']) - 10} 个")
        lines.append("")

    # 高风险函数
    if data['risk_levels']['high']:
        lines.append("🟠 高风险函数 (CC 25-50)")
        lines.append("-" * 80)
        for key, cc in data['risk_levels']['high'][:15]:
            lines.append(f"  {generate_complexity_bar(cc, 15)} {key}")
        if len(data['risk_levels']['high']) > 15:
            lines.append(f"  ... 还有 {len(data['risk_levels']['high']) - 15} 个")
        lines.append("")

    # Top 20 最复杂函数
    lines.append("🔝 Top 20 最复杂函数")
    lines.append("-" * 80)
    lines.append(f"{'复杂度':<30} {'函数'}")
    lines.append("-" * 80)

    for i, (key, func_data) in enumerate(data['sorted_files'][:20], 1):
        cc = func_data['complexity']
        level, emoji = get_complexity_level(cc)
        bar = generate_complexity_bar(cc, 20)

        # 构建显示名称
        if func_data.get('class'):
            display_name = f"{func_data['file']}:{func_data['class']}.{func_data['method']}"
        elif func_data.get('method'):
            display_name = f"{func_data['file']}:{func_data['method']}"
        else:
            display_name = key

        lines.append(f"{i:2}. {bar} {emoji}")
        lines.append(f"     {display_name}")

    lines.append("")

    # 文件复杂度排名
    lines.append("📁 文件复杂度排名")
    lines.append("-" * 80)
    lines.append(f"{'平均复杂度':<30} {'文件'}")
    lines.append("-" * 80)

    for i, (file_path, avg_cc) in enumerate(list(data['file_complexity'].items())[:20], 1):
        level, emoji = get_complexity_level(avg_cc)
        bar = generate_complexity_bar(avg_cc, 15)
        lines.append(f"{i:2}. {bar} {emoji} {file_path}")

    lines.append("")

    # 改进建议
    lines.append("💡 改进建议")
    lines.append("-" * 80)

    critical_count = len(data['risk_levels']['critical'])
    high_count = len(data['risk_levels']['high'])
    medium_count = len(data['risk_levels']['medium'])

    if critical_count > 0:
        lines.append(f"🔴 紧急: {critical_count} 个函数复杂度超过 50，必须重构")

    if high_count > 0:
        lines.append(f"🟠 重要: {high_count} 个函数复杂度在 25-50 之间")

    if medium_count > 0:
        lines.append(f"🟡 建议: {medium_count} 个函数复杂度在 15-25 之间")

    if data['avg_complexity'] > 20:
        lines.append("")
        lines.append("⚠️  警告: 项目平均复杂度偏高，建议整体重构")

    # 重构优先级
    lines.append("")
    lines.append("🎯 重构优先级:")

    priority_list = []
    priority_list.extend(data['risk_levels']['critical'])
    priority_list.extend(data['risk_levels']['high'])

    if priority_list:
        for i, (key, cc) in enumerate(priority_list[:5], 1):
            lines.append(f"  {i}. {key}")
            lines.append(f"     当前复杂度: {cc}, 目标: < 15")
    else:
        lines.append("  ✅ 当前代码复杂度在可接受范围内")

    lines.append("")
    lines.append("=" * 80)
    lines.append("✅ 报告生成完成")
    lines.append("=" * 80)

    return '\n'.join(lines)


def generate_no_analysis_report():
    """生成无分析数据时的报告"""
    lines = []
    lines.append("=" * 80)
    lines.append("📊 代码复杂度分析报告 (Code Complexity Analysis)")
    lines.append(f"⏰ 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)
    lines.append("")
    lines.append("⚠️  未找到可分析的代码或分析工具未安装")
    lines.append("")
    lines.append("请安装分析工具：")
    lines.append("")
    lines.append("Python 项目 (推荐 radon):")
    lines.append("  pip install radon")
    lines.append("")
    lines.append("多语言项目 (推荐 lizard):")
    lines.append("  pip install lizard")
    lines.append("")
    lines.append("然后重新运行分析")
    lines.append("")
    lines.append("=" * 80)

    return '\n'.join(lines)


def save_report(report, output_file='complexity_map_report.txt'):
    """保存报告到文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✅ 报告已保存到: {output_file}")


def main():
    print("🔍 代码复杂度分析工具")
    print()

    # 尝试使用不同的工具进行分析
    data = None

    # 优先使用 radon (Python)
    if os.path.exists('setup.py') or os.path.exists('pyproject.toml') or os.path.exists('pytest.ini'):
        print("🐍 检测到 Python 项目")
        data = analyze_with_radon()

    # 如果 radon 失败，尝试 lizard
    if not data:
        data = analyze_with_lizard()

    print()
    print("📝 正在生成报告...")

    report = generate_report(data)

    print()
    print(report)

    save_report(report)


if __name__ == '__main__':
    main()
