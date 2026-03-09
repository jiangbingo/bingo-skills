#!/usr/bin/env python3
"""
测试覆盖率分析工具
支持 Python (coverage.py) 和 JavaScript/TypeScript (jest/vitest)
"""

import subprocess
import sys
import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def detect_coverage_tool():
    """检测项目中使用的覆盖率工具"""
    tools = []

    # 检查 Python coverage.py
    if os.path.exists('.coverage') or os.path.exists('coverage.json'):
        tools.append(('python', 'coverage.py'))

    # 检查 jest/vitest 覆盖率报告
    coverage_json_paths = [
        'coverage/coverage-final.json',
        'coverage/coverage.json',
        'coverage.json',
    ]
    for path in coverage_json_paths:
        if os.path.exists(path):
            tools.append(('javascript', 'jest/vitest'))
            break

    return tools


def run_python_coverage():
    """运行 Python coverage 并生成 JSON 报告"""
    print("📊 检测到 Python 项目，运行 coverage...")

    # 尝试生成 JSON 报告
    try:
        result = subprocess.run(
            ['coverage', 'json'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("✅ coverage.json 已生成")
            return parse_python_coverage()
        else:
            print(f"⚠️  coverage json 失败: {result.stderr}")
            return None
    except FileNotFoundError:
        print("⚠️  未找到 coverage 命令，尝试读取现有数据...")
        return parse_python_coverage()
    except subprocess.TimeoutExpired:
        print("⚠️  coverage 超时")
        return None


def parse_python_coverage():
    """解析 Python coverage.json 数据"""
    coverage_file = 'coverage.json'
    if not os.path.exists(coverage_file):
        print(f"⚠️  未找到 {coverage_file}")
        return None

    with open(coverage_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    files = {}
    total_lines = 0
    covered_lines = 0
    total_branches = 0
    covered_branches = 0

    for file_path, file_data in data.get('files', {}).items():
        summary = file_data.get('summary', {})
        num_statements = summary.get('num_statements', 0)
        covered = summary.get('covered_lines', 0)
        missing = summary.get('missing_lines', 0)

        # 计算行覆盖率
        if num_statements > 0:
            coverage_pct = (covered / num_statements) * 100
        else:
            coverage_pct = 0

        files[file_path] = {
            'statements': num_statements,
            'covered': covered,
            'missing': summary.get('missing_lines', 0),
            'coverage': coverage_pct,
            'branches': summary.get('num_branches', 0),
            'covered_branches': summary.get('covered_branches', 0),
        }

        total_lines += num_statements
        covered_lines += covered
        total_branches += files[file_path]['branches']
        covered_branches += files[file_path]['covered_branches']

    overall_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
    branch_coverage = (covered_branches / total_branches * 100) if total_branches > 0 else None

    return {
        'format': 'python',
        'files': files,
        'total_lines': total_lines,
        'covered_lines': covered_lines,
        'overall_coverage': overall_coverage,
        'branch_coverage': branch_coverage,
        'total_branches': total_branches,
        'covered_branches': covered_branches,
    }


def parse_js_coverage():
    """解析 JavaScript/TypeScript jest/vitest 覆盖率数据"""
    coverage_paths = [
        'coverage/coverage-final.json',
        'coverage/coverage.json',
        'coverage.json',
    ]

    for path in coverage_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return parse_coverage_data(data, path)

    return None


def parse_coverage_data(data, source):
    """解析通用覆盖率数据"""
    files = {}
    total_lines = 0
    covered_lines = 0
    total_branches = 0
    covered_branches = 0

    for file_path, file_data in data.items():
        # 跳过总结信息
        if not isinstance(file_data, dict):
            continue

        stmts = file_data.get('s', {})
        branches = file_data.get('b', {})
        functions = file_data.get('f', {})

        # 计算语句覆盖
        total_stmts = sum(v for k, v in stmts.items() if k != '0')
        covered_stmts = sum(v for k, v in stmts.items() if k != '0' and v > 0)

        # 计算分支覆盖
        total_br = 0
        covered_br = 0
        for branch_set in branches.values():
            if isinstance(branch_set, list):
                total_br += len(branch_set)
                covered_br += sum(1 for v in branch_set if v > 0)

        if total_stmts > 0:
            coverage_pct = (covered_stmts / total_stmts) * 100
        else:
            coverage_pct = 0

        branch_pct = (covered_br / total_br * 100) if total_br > 0 else None

        files[file_path] = {
            'statements': total_stmts,
            'covered': covered_stmts,
            'missing': total_stmts - covered_stmts,
            'coverage': coverage_pct,
            'branches': total_br,
            'covered_branches': covered_br,
            'branch_coverage': branch_pct,
            'functions': len(functions),
        }

        total_lines += total_stmts
        covered_lines += covered_stmts
        total_branches += total_br
        covered_branches += covered_br

    overall_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
    branch_coverage = (covered_branches / total_branches * 100) if total_branches > 0 else None

    return {
        'format': 'javascript',
        'files': files,
        'total_lines': total_lines,
        'covered_lines': covered_lines,
        'overall_coverage': overall_coverage,
        'branch_coverage': branch_coverage,
        'total_branches': total_branches,
        'covered_branches': covered_branches,
    }


def get_coverage_level(coverage):
    """根据覆盖率返回等级"""
    if coverage >= 90:
        return 'Excellent', '🟢'
    elif coverage >= 75:
        return 'Good', '🟢'
    elif coverage >= 50:
        return 'Fair', '🟡'
    elif coverage >= 25:
        return 'Poor', '🟠'
    else:
        return 'Critical', '🔴'


def generate_coverage_bar(coverage, width=20):
    """生成覆盖率可视化条"""
    filled = int(coverage / 100 * width)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {coverage:.1f}%"


def generate_report(coverage_data):
    """生成覆盖率报告"""
    if not coverage_data:
        return generate_no_coverage_report()

    lines = []
    lines.append("=" * 80)
    lines.append("📊 测试覆盖率分析报告 (Test Coverage Analysis)")
    lines.append(f"⏰ 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)
    lines.append("")

    # 摘要统计
    lines.append("📈 总体统计")
    lines.append("-" * 80)
    overall = coverage_data['overall_coverage']
    level, emoji = get_coverage_level(overall)
    lines.append(f"总体覆盖率: {generate_coverage_bar(overall)} {level} {emoji}")

    if coverage_data.get('branch_coverage'):
        branch = coverage_data['branch_coverage']
        lines.append(f"分支覆盖率: {generate_coverage_bar(branch)}")

    lines.append(f"总代码行数: {coverage_data['total_lines']:,}")
    lines.append(f"已覆盖行数: {coverage_data['covered_lines']:,}")
    lines.append(f"未覆盖行数: {coverage_data['total_lines'] - coverage_data['covered_lines']:,}")
    lines.append("")

    # 覆盖率分布
    lines.append("📊 覆盖率分布")
    lines.append("-" * 80)
    distribution = defaultdict(list)
    for file_path, data in coverage_data['files'].items():
        coverage = data['coverage']
        if coverage >= 90:
            distribution['Excellent'].append((file_path, coverage))
        elif coverage >= 75:
            distribution['Good'].append((file_path, coverage))
        elif coverage >= 50:
            distribution['Fair'].append((file_path, coverage))
        elif coverage >= 25:
            distribution['Poor'].append((file_path, coverage))
        else:
            distribution['Critical'].append((file_path, coverage))

    for level in ['Excellent', 'Good', 'Fair', 'Poor', 'Critical']:
        emoji_map = {'Excellent': '🟢', 'Good': '🟢', 'Fair': '🟡', 'Poor': '🟠', 'Critical': '🔴'}
        count = len(distribution[level])
        if count > 0:
            lines.append(f"{emoji_map[level]} {level}: {count} 个文件")

    lines.append("")

    # 零覆盖率文件
    zero_coverage = [fp for fp, data in coverage_data['files'].items() if data['coverage'] == 0]
    if zero_coverage:
        lines.append("🔴 零覆盖率文件")
        lines.append("-" * 80)
        for fp in zero_coverage[:20]:
            lines.append(f"  • {fp}")
        if len(zero_coverage) > 20:
            lines.append(f"  ... 还有 {len(zero_coverage) - 20} 个文件")
        lines.append("")

    # 低覆盖率文件
    low_coverage = [(fp, data) for fp, data in coverage_data['files'].items() if 0 < data['coverage'] < 50]
    if low_coverage:
        lines.append("🟠 低覆盖率文件 (< 50%)")
        lines.append("-" * 80)
        sorted_files = sorted(low_coverage, key=lambda x: x[1]['coverage'])
        for fp, data in sorted_files[:20]:
            lines.append(f"  {generate_coverage_bar(data['coverage'], 15)} {fp}")
        if len(sorted_files) > 20:
            lines.append(f"  ... 还有 {len(sorted_files) - 20} 个文件")
        lines.append("")

    # 文件详细列表
    lines.append("📁 文件覆盖率详情")
    lines.append("-" * 80)
    lines.append(f"{'覆盖率':<50} {'文件'}")
    lines.append("-" * 80)

    sorted_files = sorted(coverage_data['files'].items(), key=lambda x: x[1]['coverage'], reverse=True)
    for file_path, data in sorted_files:
        coverage = data['coverage']
        level, emoji = get_coverage_level(coverage)
        bar = generate_coverage_bar(coverage, 30)
        lines.append(f"{bar} {emoji} {file_path}")

    lines.append("")

    # 改进建议
    lines.append("💡 改进建议")
    lines.append("-" * 80)

    critical_count = len(distribution['Critical'])
    poor_count = len(distribution['Poor'])
    fair_count = len(distribution['Fair'])

    if critical_count > 0:
        lines.append(f"🔴 紧急: {critical_count} 个文件覆盖率低于 25%，需要立即添加测试")

    if poor_count > 0:
        lines.append(f"🟠 重要: {poor_count} 个文件覆盖率在 25-50% 之间")

    if fair_count > 0:
        lines.append(f"🟡 建议: {fair_count} 个文件覆盖率在 50-75% 之间，可以进一步改进")

    if zero_coverage:
        lines.append(f"⚠️  警告: {len(zero_coverage)} 个文件完全没有测试覆盖")

    # 优先级建议
    if low_coverage:
        lines.append("")
        lines.append("🎯 测试优先级建议:")

        # 按文件大小排序，优先测试大文件
        sorted_by_size = sorted(
            [(fp, data) for fp, data in low_coverage],
            key=lambda x: x[1]['statements'],
            reverse=True
        )

        for i, (fp, data) in enumerate(sorted_by_size[:5], 1):
            lines.append(f"  {i}. {fp}")
            lines.append(f"     当前: {data['coverage']:.1f}%, 目标: 75%+")
            lines.append(f"     需要覆盖: {data['missing']} 行")

    lines.append("")
    lines.append("=" * 80)
    lines.append("✅ 报告生成完成")
    lines.append("=" * 80)

    return '\n'.join(lines)


def generate_no_coverage_report():
    """生成无覆盖率数据时的报告"""
    lines = []
    lines.append("=" * 80)
    lines.append("📊 测试覆盖率分析报告 (Test Coverage Analysis)")
    lines.append(f"⏰ 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)
    lines.append("")
    lines.append("⚠️  未找到覆盖率数据")
    lines.append("")
    lines.append("请先运行测试并生成覆盖率报告：")
    lines.append("")
    lines.append("Python 项目:")
    lines.append("  pip install coverage")
    lines.append("  coverage run -m pytest")
    lines.append("  coverage json")
    lines.append("")
    lines.append("JavaScript/TypeScript 项目 (jest):")
    lines.append("  npm test -- --coverage --coverageReporters=json")
    lines.append("")
    lines.append("JavaScript/TypeScript 项目 (vitest):")
    lines.append("  npx vitest run --coverage")
    lines.append("")
    lines.append("=" * 80)

    return '\n'.join(lines)


def save_report(report, output_file='test_coverage_report.txt'):
    """保存报告到文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✅ 报告已保存到: {output_file}")


def main():
    print("🔍 测试覆盖率分析工具")
    print()

    # 检测覆盖率工具
    tools = detect_coverage_tool()

    if not tools:
        print("⚠️  未检测到覆盖率数据")
        print()
        print("尝试自动运行覆盖率工具...")

        # 尝试运行 Python coverage
        if os.path.exists('pytest.ini') or os.path.exists('setup.py') or os.path.exists('pyproject.toml'):
            data = run_python_coverage()
        else:
            data = None
    else:
        print(f"✅ 检测到覆盖率工具: {', '.join([t[1] for t in tools])}")
        print()

        data = None
        for lang, tool in tools:
            if lang == 'python':
                data = parse_python_coverage()
            elif lang == 'javascript':
                data = parse_js_coverage()

            if data:
                break

    print()
    print("📝 正在生成报告...")

    report = generate_report(data)

    print()
    print(report)

    save_report(report)


if __name__ == '__main__':
    main()
