#!/usr/bin/env python3
"""
分支健康度检查器
检查 Git 仓库的分支健康度，识别僵尸分支、已合并分支和命名规范问题
"""

import subprocess
import sys
from datetime import datetime, timedelta
from collections import defaultdict


def run_command(cmd):
    """执行 shell 命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "命令执行超时"
    except Exception as e:
        return False, "", str(e)


def get_all_branches():
    """获取所有本地分支"""
    success, output, error = run_command('git branch -a')
    if not success:
        print(f"❌ 获取分支列表失败: {error}")
        sys.exit(1)

    branches = []
    for line in output.split('\n'):
        line = line.strip()
        if line and not line.startswith('remotes/origin/HEAD'):
            # 移除远程分支前缀
            if line.startswith('remotes/origin/'):
                line = line.replace('remotes/origin/', '', 1)
            # 移除当前分支标记
            if line.startswith('* '):
                line = line[2:]
            if line:
                branches.append(line)

    # 去重并排序
    branches = sorted(list(set(branches)))
    return branches


def get_branch_last_commit_date(branch):
    """获取分支最后提交日期"""
    success, output, error = run_command(f'git log -1 --format=%ci {branch}')
    if success and output:
        try:
            return datetime.strptime(output.split()[0], '%Y-%m-%d')
        except:
            return None
    return None


def get_branch_commits_count(branch):
    """获取分支提交数量"""
    success, output, error = run_command(f'git rev-list --count {branch}')
    if success and output:
        try:
            return int(output)
        except:
            return 0
    return 0


def is_branch_merged(branch):
    """检查分支是否已合并"""
    # 获取当前分支
    success, current, error = run_command('git rev-parse --abbrev-ref HEAD')
    if not success:
        return False

    main_branch = get_main_branch()
    if branch == current or branch == main_branch:
        return False

    success, output, error = run_command(f'git branch --merged {main_branch}')
    if success:
        merged_branches = [b.strip().replace('* ', '') for b in output.split('\n')]
        return branch in merged_branches
    return False


def get_main_branch():
    """获取主分支名称（main 或 master）"""
    # 检查 main 是否存在
    success, output, error = run_command('git rev-parse --verify main')
    if success:
        return 'main'

    # 检查 master 是否存在
    success, output, error = run_command('git rev-parse --verify master')
    if success:
        return 'master'

    # 获取默认分支
    success, output, error = run_command('git symbolic-ref refs/remotes/origin/HEAD')
    if success:
        return output.replace('refs/remotes/origin/', '')

    return 'main'


def check_branch_naming_convention(branch):
    """检查分支命名规范"""
    conventions = {
        'feature/': '功能分支',
        'bugfix/': 'Bug 修复分支',
        'hotfix/': '紧急修复分支',
        'release/': '发布分支',
        'develop': '开发环境分支',
        'main': '主分支',
        'master': '主分支'
    }

    for prefix, description in conventions.items():
        if branch == prefix or branch.startswith(prefix):
            return True, prefix, description

    return False, None, '未定义命名规范'


def get_branch_base(branch):
    """获取分支基于哪个分支"""
    main_branch = get_main_branch()
    success, output, error = run_command(f'git merge-base {branch} {main_branch}')
    if success and output:
        return output[:8]
    return None


def analyze_branches(branches):
    """分析所有分支"""
    main_branch = get_main_branch()
    now = datetime.now()
    zombie_threshold = now - timedelta(days=90)

    analysis = {
        'total': len(branches),
        'main_branch': main_branch,
        'zombie_branches': [],
        'merged_branches': [],
        'naming_issues': [],
        'active_branches': [],
        'branch_details': []
    }

    for branch in branches:
        if branch == main_branch:
            continue

        # 获取分支信息
        last_commit = get_branch_last_commit_date(branch)
        commits_count = get_branch_commits_count(branch)
        is_merged = is_branch_merged(branch)
        follows_convention, prefix, convention_desc = check_branch_naming_convention(branch)

        branch_info = {
            'name': branch,
            'last_commit': last_commit,
            'commits_count': commits_count,
            'is_merged': is_merged,
            'follows_convention': follows_convention,
            'prefix': prefix,
            'convention': convention_desc
        }

        analysis['branch_details'].append(branch_info)

        # 分类分支
        if last_commit and last_commit < zombie_threshold:
            analysis['zombie_branches'].append(branch_info)

        if is_merged:
            analysis['merged_branches'].append(branch_info)

        if not follows_convention:
            analysis['naming_issues'].append(branch_info)

        if last_commit and last_commit >= zombie_threshold:
            analysis['active_branches'].append(branch_info)

    return analysis


def generate_report(analysis):
    """生成分析报告"""
    report = []
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    report.append("=" * 140)
    report.append("分支健康度分析报告")
    report.append(f"分析时间: {now}")
    report.append("=" * 140)
    report.append(f"主分支: {analysis['main_branch']}")
    report.append(f"总分支数: {analysis['total']}")
    report.append("")

    # 僵尸分支统计
    report.append("=" * 140)
    report.append("🧟 僵尸分支检测（90天无活动）")
    report.append("=" * 140)
    report.append(f"僵尸分支数量: {len(analysis['zombie_branches'])}")
    report.append("")

    if analysis['zombie_branches']:
        report.append("僵尸分支列表:")
        report.append(f"{'分支名称':<40} {'最后提交日期':<15} {'提交数':<8} {'命名规范'}")
        report.append("-" * 140)

        for branch in sorted(analysis['zombie_branches'], key=lambda x: x['last_commit']):
            last_date = branch['last_commit'].strftime('%Y-%m-%d') if branch['last_commit'] else '未知'
            convention = '✅' if branch['follows_convention'] else '❌'
            report.append(f"{branch['name']:<40} {last_date:<15} {branch['commits_count']:<8} {convention}")

    # 已合并分支统计
    report.append("")
    report.append("=" * 140)
    report.append("✅ 已合并分支")
    report.append("=" * 140)
    report.append(f"已合并分支数量: {len(analysis['merged_branches'])}")
    report.append("")

    if analysis['merged_branches']:
        report.append("已合并分支列表（可安全删除）:")
        report.append(f"{'分支名称':<40} {'最后提交日期':<15} {'提交数':<8} {'命名规范'}")
        report.append("-" * 140)

        for branch in sorted(analysis['merged_branches'], key=lambda x: x['last_commit'], reverse=True):
            last_date = branch['last_commit'].strftime('%Y-%m-%d') if branch['last_commit'] else '未知'
            convention = '✅' if branch['follows_convention'] else '❌'
            report.append(f"{branch['name']:<40} {last_date:<15} {branch['commits_count']:<8} {convention}")

    # 命名规范统计
    report.append("")
    report.append("=" * 140)
    report.append("📝 命名规范分析")
    report.append("=" * 140)

    convention_counts = defaultdict(int)
    for branch in analysis['branch_details']:
        if branch['prefix']:
            convention_counts[branch['convention']] += 1

    report.append("命名规范分布:")
    for convention, count in sorted(convention_counts.items(), key=lambda x: x[1], reverse=True):
        report.append(f"  - {convention}: {count} 个")

    report.append("")
    report.append(f"不符合命名规范的分支: {len(analysis['naming_issues'])} 个")

    if analysis['naming_issues']:
        report.append("")
        report.append("不符合规范的分支:")
        for branch in sorted(analysis['naming_issues'], key=lambda x: x['name']):
            report.append(f"  - {branch['name']}")

    # 活跃分支统计
    report.append("")
    report.append("=" * 140)
    report.append("🟢 活跃分支（90天内有活动）")
    report.append("=" * 140)
    report.append(f"活跃分支数量: {len(analysis['active_branches'])}")
    report.append("")

    if analysis['active_branches']:
        report.append("活跃分支列表:")
        report.append(f"{'分支名称':<40} {'最后提交日期':<15} {'提交数':<8} {'命名规范'}")
        report.append("-" * 140)

        for branch in sorted(analysis['active_branches'], key=lambda x: x['last_commit'], reverse=True):
            last_date = branch['last_commit'].strftime('%Y-%m-%d') if branch['last_commit'] else '未知'
            convention = '✅' if branch['follows_convention'] else '❌'
            report.append(f"{branch['name']:<40} {last_date:<15} {branch['commits_count']:<8} {convention}")

    # 清理建议
    report.append("")
    report.append("=" * 140)
    report.append("🎯 清理建议")
    report.append("=" * 140)

    # 高优先级：已合并且无活动的分支
    high_priority = [b for b in analysis['merged_branches'] if b in analysis['zombie_branches']]
    report.append(f"🔴 高优先级清理（已合并且无活动）: {len(high_priority)} 个")

    if high_priority:
        report.append("")
        report.append("建议立即删除的分支:")
        for branch in sorted(high_priority, key=lambda x: x['name']):
            report.append(f"  - {branch['name']}")

    # 中优先级：已合并的分支
    medium_priority = [b for b in analysis['merged_branches'] if b not in high_priority]
    report.append("")
    report.append(f"🟡 中优先级清理（已合并）: {len(medium_priority)} 个")

    if medium_priority:
        report.append("")
        report.append("可以考虑删除的分支:")
        for branch in sorted(medium_priority, key=lambda x: x['name']):
            report.append(f"  - {branch['name']}")

    # 低优先级：僵尸分支但未合并
    low_priority = [b for b in analysis['zombie_branches'] if b not in analysis['merged_branches']]
    report.append("")
    report.append(f"🟢 低优先级清理（僵尸分支未合并）: {len(low_priority)} 个")

    if low_priority:
        report.append("")
        report.append("需要确认后删除的分支（可能包含未合并的更改）:")
        for branch in sorted(low_priority, key=lambda x: x['name']):
            report.append(f"  - {branch['name']}")

    # 清理命令
    report.append("")
    report.append("=" * 140)
    report.append("🔧 清理命令")
    report.append("=" * 140)

    if high_priority:
        report.append("")
        report.append("# 高优先级清理命令（已合并且无活动）:")
        report.append("git branch -D " + " ".join([b['name'] for b in sorted(high_priority, key=lambda x: x['name'])]))

    if medium_priority:
        report.append("")
        report.append("# 中优先级清理命令（已合并）:")
        report.append("git branch -d " + " ".join([b['name'] for b in sorted(medium_priority, key=lambda x: x['name'])]))

    # 分支依赖关系
    report.append("")
    report.append("=" * 140)
    report.append("📊 分支详细信息")
    report.append("=" * 140)
    report.append(f"{'分支名称':<40} {'最后提交':<15} {'提交数':<8} {'已合并':<8} {'命名规范':<15}")
    report.append("-" * 140)

    all_branches = sorted(analysis['branch_details'], key=lambda x: x['name'])
    for branch in all_branches:
        last_date = branch['last_commit'].strftime('%Y-%m-%d') if branch['last_commit'] else '未知'
        merged = '是' if branch['is_merged'] else '否'
        convention = branch['convention'] if branch['follows_convention'] else '❌ 不符合'
        report.append(f"{branch['name']:<40} {last_date:<15} {branch['commits_count']:<8} {merged:<8} {convention:<15}")

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
    print("🔍 正在检查分支健康度...")
    print()

    # 检查是否在 Git 仓库中
    success, output, error = run_command('git rev-parse --is-inside-work-tree')
    if not success or output != 'true':
        print("❌ 当前目录不是 Git 仓库")
        print("请在 Git 仓库目录中运行此脚本")
        sys.exit(1)

    # 获取所有分支
    print("📋 正在获取所有分支...")
    branches = get_all_branches()
    print(f"✅ 找到 {len(branches)} 个分支")
    print()

    # 分析分支
    print("🔬 正在分析分支数据...")
    analysis = analyze_branches(branches)
    print("✅ 分析完成")
    print()

    # 生成报告
    print("📝 正在生成分析报告...")
    report = generate_report(analysis)
    output_file = 'branch_hygiene_report.txt'

    if save_report(report, output_file):
        print(f"✅ 报告已保存到: {output_file}")
    else:
        print("❌ 保存报告失败")
        sys.exit(1)

    print()
    print("=" * 60)
    print("📋 分析摘要")
    print("=" * 60)
    print(f"  总分支数: {analysis['total']}")
    print(f"  主分支: {analysis['main_branch']}")
    print(f"  僵尸分支: {len(analysis['zombie_branches'])} 个")
    print(f"  已合并分支: {len(analysis['merged_branches'])} 个")
    print(f"  活跃分支: {len(analysis['active_branches'])} 个")
    print(f"  命名规范问题: {len(analysis['naming_issues'])} 个")
    print(f"  报告文件: {output_file}")


if __name__ == '__main__':
    main()
