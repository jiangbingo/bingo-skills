#!/usr/bin/env python3
"""
Knowledge Mapper - 项目知识图谱映射
"""

import subprocess
import re
from collections import defaultdict
from pathlib import Path

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
    r'\.md$',  # 排除文档文件
    r'\.txt$',
    r'\.json$',
    r'\.yaml$',
    r'\.yml$',
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

def get_author_file_mapping():
    """获取作者与文件的映射关系"""
    result = subprocess.run([
        'git', 'log',
        '--pretty=format:%an',
        '--name-only',
        '-m',
    ], capture_output=True, text=True)

    if result.returncode != 0:
        return {}, {}

    lines = result.stdout.strip().split('\n')
    author_file_data = defaultdict(lambda: defaultdict(int))
    file_author_data = defaultdict(lambda: defaultdict(int))

    current_author = None
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if not should_exclude(line) and '/' in line:
            # 这是文件路径
            if current_author:
                author_file_data[current_author][line] += 1
                file_author_data[line][current_author] += 1
        else:
            # 这是作者名
            current_author = line

    return dict(author_file_data), dict(file_author_data)

def analyze_code_ownership(file_author_data):
    """分析代码所有权"""
    file_ownership = {}

    for file_path, authors in file_author_data.items():
        if should_exclude(file_path):
            continue

        total_commits = sum(authors.values())
        sorted_authors = sorted(authors.items(), key=lambda x: x[1], reverse=True)

        primary_owner = sorted_authors[0][0] if sorted_authors else "Unknown"
        contributor_count = len(authors)

        # 计算所有权集中度 (主贡献者占比)
        primary_ratio = sorted_authors[0][1] / total_commits if total_commits > 0 else 0

        file_ownership[file_path] = {
            'primary_owner': primary_owner,
            'contributors': list(authors.keys()),
            'contributor_count': contributor_count,
            'total_commits': total_commits,
            'ownership_concentration': primary_ratio,
        }

    return file_ownership

def calculate_knowledge_risk(file_ownership):
    """计算知识风险等级"""
    risk_analysis = {}

    for file_path, data in file_ownership.items():
        contributor_count = data['contributor_count']

        if contributor_count == 1:
            risk_level = "Critical"
            risk_emoji = "🔴"
        elif contributor_count == 2:
            risk_level = "High"
            risk_emoji = "🟠"
        elif contributor_count <= 5:
            risk_level = "Medium"
            risk_emoji = "🟡"
        else:
            risk_level = "Low"
            risk_emoji = "🟢"

        risk_analysis[file_path] = {
            'level': risk_level,
            'emoji': risk_emoji,
            'contributor_count': contributor_count,
        }

    return risk_analysis

def find_file_relationships(author_file_data):
    """找出文件间的关系（基于共同修改者）"""
    file_cooccurrence = defaultdict(lambda: defaultdict(int))

    for author, files in author_file_data.items():
        file_list = list(files.keys())
        # 计算文件共现
        for i, file1 in enumerate(file_list):
            for file2 in file_list[i+1:]:
                if not should_exclude(file1) and not should_exclude(file2):
                    file_cooccurrence[file1][file2] += 1
                    file_cooccurrence[file2][file1] += 1

    # 找出强关联（共同修改次数 >= 2）
    strong_relationships = []
    for file1, related in file_cooccurrence.items():
        for file2, count in related.items():
            if count >= 2:
                strong_relationships.append((file1, file2, count))

    strong_relationships.sort(key=lambda x: x[2], reverse=True)
    return strong_relationships

def generate_dot_graph(file_ownership, strong_relationships, output_file):
    """生成 Graphviz DOT 格式的知识图谱"""
    dot_content = []
    dot_content.append('digraph KnowledgeGraph {')
    dot_content.append('  rankdir=LR;')
    dot_content.append('  node [shape=box, style=rounded];')
    dot_content.append('')

    # 按模块分组文件
    modules = defaultdict(list)
    for file_path in file_ownership.keys():
        if '/' in file_path:
            module = file_path.split('/')[0]
        else:
            module = 'root'
        modules[module].append(file_path)

    # 创建子图
    for module, files in modules.items():
        if len(files) > 1:
            dot_content.append(f'  subgraph cluster_{module} {{')
            dot_content.append(f'    label="{module}";')
            dot_content.append(f'    style=filled;')
            dot_content.append(f'    color=lightgrey;')
            for file_path in files[:10]:  # 限制每个模块最多10个文件
                safe_name = file_path.replace('/', '_').replace('.', '_').replace('-', '_')
                risk = file_ownership[file_path]['contributor_count']
                color = "red" if risk <= 2 else "yellow" if risk <= 5 else "green"
                dot_content.append(f'    "{safe_name}" [label="{file_path}", fillcolor={color}, style="rounded,filled"];')
            dot_content.append('  }')
            dot_content.append('')

    # 添加边（文件关系）
    for file1, file2, count in strong_relationships[:50]:  # 限制边数量
        safe_name1 = file1.replace('/', '_').replace('.', '_').replace('-', '_')
        safe_name2 = file2.replace('/', '_').replace('.', '_').replace('-', '_')
        dot_content.append(f'  "{safe_name1}" -> "{safe_name2}" [label="{count}", penwidth={min(count, 3)}];')

    dot_content.append('}')
    dot_content.append('')

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(dot_content))

def generate_report(author_file_data, file_author_data, file_ownership, risk_analysis, strong_relationships):
    """生成知识图谱分析报告"""
    report = []
    report.append("=" * 140)
    report.append("项目知识图谱分析报告 (Knowledge Map Analysis)")
    report.append("=" * 140)
    report.append("")

    # 基本统计
    total_authors = len(author_file_data)
    total_files = len(file_ownership)
    total_relationships = len(strong_relationships)

    report.append("📊 基本统计")
    report.append("=" * 140)
    report.append(f"总贡献者数: {total_authors}")
    report.append(f"分析文件数: {total_files}")
    report.append(f"文件关联数: {total_relationships}")
    report.append("")

    # 贡献者排行
    report.append("=" * 140)
    report.append("👥 贡献者排行 (按文件修改数)")
    report.append("=" * 140)

    author_file_counts = [(author, sum(files.values())) for author, files in author_file_data.items()]
    author_file_counts.sort(key=lambda x: x[1], reverse=True)

    for i, (author, count) in enumerate(author_file_counts[:20], 1):
        percentage = (count / sum(c for _, c in author_file_counts) * 100) if author_file_counts else 0
        report.append(f"  {i:2}. {author:<30} 修改文件: {count:<4} ({percentage:.1f}%)")

    report.append("")

    # 知识风险分析
    report.append("=" * 140)
    report.append("⚠️  知识风险分析 (Bus Factor)")
    report.append("=" * 140)

    risk_counts = defaultdict(int)
    for risk in risk_analysis.values():
        risk_counts[risk['level']] += 1

    report.append(f"🔴 Critical 风险 (1人): {risk_counts['Critical']} 个文件")
    report.append(f"🟠 High 风险 (2人):    {risk_counts['High']} 个文件")
    report.append(f"🟡 Medium 风险 (3-5人): {risk_counts['Medium']} 个文件")
    report.append(f"🟢 Low 风险 (6+人):   {risk_counts['Low']} 个文件")
    report.append("")

    # 列出高风险文件
    high_risk_files = [(fp, d) for fp, d in file_ownership.items() if risk_analysis[fp]['level'] in ['Critical', 'High']]
    high_risk_files.sort(key=lambda x: x[1]['contributor_count'])

    if high_risk_files:
        report.append("高风险文件列表:")
        report.append("")
        for file_path, data in high_risk_files[:30]:
            risk = risk_analysis[file_path]
            report.append(f"  {risk['emoji']} {file_path}")
            report.append(f"     主要贡献者: {data['primary_owner']}")
            report.append(f"     贡献者数: {data['contributor_count']} | 总提交: {data['total_commits']}")
            report.append("")

    # 代码所有权报告
    report.append("=" * 140)
    report.append("📁 代码所有权报告 (Top 30 文件)")
    report.append("=" * 140)
    report.append(f"{'文件路径':<50} {'主要贡献者':<20} {'贡献者数':<8} {'集中度':<10} {'风险等级'}")
    report.append("-" * 140)

    sorted_files = sorted(file_ownership.items(), key=lambda x: x[1]['total_commits'], reverse=True)

    for file_path, data in sorted_files[:30]:
        primary = data['primary_owner']
        contributors = data['contributor_count']
        concentration = f"{data['ownership_concentration']*100:.0f}%"
        risk = risk_analysis[file_path]['emoji'] + " " + risk_analysis[file_path]['level']

        display_path = file_path if len(file_path) <= 48 else '...' + file_path[-45:]
        report.append(f"{display_path:<50} {primary:<20} {contributors:<8} {concentration:<10} {risk}")

    report.append("")

    # 专家领域识别
    report.append("=" * 140)
    report.append("🎯 专家领域识别")
    report.append("=" * 140)

    # 找出每个作者的专长领域
    author_expertise = defaultdict(lambda: defaultdict(int))
    for author, files in author_file_data.items():
        for file_path, count in files.items():
            if '/' in file_path:
                module = '/'.join(file_path.split('/')[:2])  # 取前两级目录作为模块
            else:
                module = file_path
            author_expertise[author][module] += count

    for author in author_file_counts[:10]:
        author_name = author[0]
        modules = sorted(author_expertise[author_name].items(), key=lambda x: x[1], reverse=True)[:5]
        if modules:
            report.append(f"\n  {author_name}:")
            for module, count in modules:
                report.append(f"    - {module} ({count} 次修改)")

    report.append("")

    # 文件关联分析
    if strong_relationships:
        report.append("=" * 140)
        report.append("🔗 文件关联分析 (强关联文件对)")
        report.append("=" * 140)
        report.append("以下文件经常被一起修改，可能存在逻辑依赖关系:")
        report.append("")

        for file1, file2, count in strong_relationships[:20]:
            report.append(f"  {count:3} 次: {file1}")
            report.append(f"         {file2}")
            report.append("")

    # 建议
    report.append("=" * 140)
    report.append("💡 建议")
    report.append("=" * 140)

    critical_count = risk_counts['Critical']
    high_count = risk_counts['High']

    if critical_count > 0:
        report.append("")
        report.append(f"🚨 发现 {critical_count} 个 Critical 风险文件（单人负责）:")
        report.append("  - 立即为这些文件指定备份责任人")
        report.append("  - 通过代码审查让其他团队成员熟悉代码")
        report.append("  - 考虑重写或简化这些文件")

    if high_count > 0:
        report.append("")
        report.append(f"⚠️  发现 {high_count} 个 High 风险文件（双人负责）:")
        report.append("  - 扩展这些文件的熟悉人数")
        report.append("  - 在团队中进行知识分享")

    report.append("")
    report.append("通用建议:")
    report.append("  - 定期运行此分析监控知识分布")
    report.append("  - 对高风险文件实施结对编程")
    report.append("  - 建立代码审查轮换制度")
    report.append("  - 维护代码文档以降低知识孤岛风险")

    return '\n'.join(report)

def save_report(report, output_file):
    """保存报告到文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

def main():
    print("🔍 正在分析项目知识图谱...")

    git_root = get_git_root()
    if not git_root:
        print("❌ 错误: 当前目录不是 Git 仓库")
        return

    print(f"✅ Git 仓库根目录: {git_root}")

    print("📊 正在获取作者-文件映射...")
    author_file_data, file_author_data = get_author_file_mapping()
    print(f"✅ 获取到 {len(author_file_data)} 个贡献者")

    print("📊 正在分析代码所有权...")
    file_ownership = analyze_code_ownership(file_author_data)
    print(f"✅ 分析了 {len(file_ownership)} 个文件")

    print("📊 正在计算知识风险...")
    risk_analysis = calculate_knowledge_risk(file_ownership)

    print("🔗 正在分析文件关联...")
    strong_relationships = find_file_relationships(author_file_data)
    print(f"✅ 发现 {len(strong_relationships)} 个文件关联")

    print("📝 正在生成分析报告...")
    report = generate_report(author_file_data, file_author_data, file_ownership, risk_analysis, strong_relationships)

    output_file = 'knowledge_map_report.txt'
    save_report(report, output_file)
    print(f"✅ 报告已保存到: {output_file}")

    # 生成 DOT 图
    dot_file = 'knowledge_graph.dot'
    print(f"📊 正在生成知识图谱...")
    generate_dot_graph(file_ownership, strong_relationships, dot_file)
    print(f"✅ 知识图谱已保存到: {dot_file}")
    print(f"   使用以下命令可视化: dot -Tpng {dot_file} -o knowledge_graph.png")

    print("\n" + "=" * 60)
    print("📋 分析摘要")
    print("=" * 60)
    print(f"  贡献者数: {len(author_file_data)}")
    print(f"  分析文件: {len(file_ownership)}")

    risk_counts = defaultdict(int)
    for risk in risk_analysis.values():
        risk_counts[risk['level']] += 1
    print(f"  🔴 Critical: {risk_counts['Critical']}")
    print(f"  🟠 High:     {risk_counts['High']}")
    print(f"  🟡 Medium:   {risk_counts['Medium']}")
    print(f"  🟢 Low:      {risk_counts['Low']}")
    print(f"  报告文件: {output_file}")

if __name__ == '__main__':
    main()
