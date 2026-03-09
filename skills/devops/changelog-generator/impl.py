#!/usr/bin/env python3
"""
变更日志生成器 - 自动解析 Git 提交历史生成 CHANGELOG.md

功能：
- 解析约定式提交（Conventional Commits）
- 按版本标签分组
- 分类变更类型（Added/Changed/Fixed/Removed）
- 生成 Keep a Changelog 格式的 Markdown
"""

import subprocess
import re
from datetime import datetime
from collections import defaultdict


class CommitParser:
    """解析 Git 提交信息"""

    def __init__(self):
        # 约定式提交类型映射
        self.commit_types = {
            'feat': 'Added',
            'fix': 'Fixed',
            'perf': 'Changed',
            'refactor': 'Changed',
            'docs': 'Changed',
            'style': 'Changed',
            'test': 'Changed',
            'chore': 'Changed',
            'revert': 'Fixed',
            'build': 'Changed',
            'ci': 'Changed',
        }

        # 中文类型名称
        self.type_names_cn = {
            'Added': '新增',
            'Changed': '变更',
            'Fixed': '修复',
            'Removed': '移除',
            'Security': '安全'
        }

    def parse_commit(self, commit_line):
        """
        解析单条提交信息

        格式: hash|author|date|message
        返回: dict with type, scope, description, breaking
        """
        parts = commit_line.split('|', 3)
        if len(parts) < 4:
            return None

        hash_val, author, date, message = parts[:4]

        # 解析约定式提交格式
        # type(scope)!: subject
        conventional_pattern = r'^(\w+)(?:\(([^)]+)\))?(!)?:\s*(.+)$'
        match = re.match(conventional_pattern, message)

        if not match:
            # 非约定式提交，归类为 Changed
            return {
                'hash': hash_val,
                'author': author,
                'date': date,
                'type': 'Changed',
                'scope': None,
                'description': message,
                'breaking': False
            }

        commit_type, scope, breaking, description = match.groups()

        # 映射到标准类型
        category = self.commit_types.get(commit_type, 'Changed')
        is_breaking = breaking is not None or '!' in description

        # 清理破坏性变更标记
        clean_desc = description.replace('!', '').strip()

        return {
            'hash': hash_val,
            'author': author,
            'date': date,
            'type': category,
            'commit_type': commit_type,
            'scope': scope,
            'description': clean_desc,
            'breaking': is_breaking
        }


class ChangelogGenerator:
    """生成变更日志"""

    def __init__(self):
        self.parser = CommitParser()

    def get_tags(self):
        """获取所有版本标签，按版本号排序"""
        try:
            result = subprocess.run(
                ['git', 'tag', '-l', '--sort=-v:refname'],
                capture_output=True,
                text=True,
                check=True
            )

            tags = result.stdout.strip().split('\n')
            # 过滤空标签并反转（最新的在前）
            tags = [t for t in tags if t.strip()]
            return tags[::-1]  # 反转，最新的版本在前

        except subprocess.CalledProcessError as e:
            print(f"⚠️  获取标签失败: {e}")
            return []

    def get_commits_between(self, start_tag=None, end_tag=None):
        """
        获取两个标签之间的提交

        参数:
            start_tag: 起始标签（不包含），None 表示从最开始
            end_tag: 结束标签（包含），None 表示到最新提交
        """
        try:
            if start_tag and end_tag:
                range_spec = f"{start_tag}..{end_tag}"
            elif end_tag:
                range_spec = end_tag
            elif start_tag:
                range_spec = f"{start_tag}..HEAD"
            else:
                range_spec = "HEAD"

            # 使用 git log 获取提交信息
            # 格式: %H|%an|%ad|%s
            cmd = [
                'git', 'log',
                range_spec,
                '--format=%H|%an|%ad|%s',
                '--date=short'
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            commits = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parsed = self.parser.parse_commit(line)
                    if parsed:
                        commits.append(parsed)

            return commits

        except subprocess.CalledProcessError as e:
            print(f"⚠️  获取提交失败: {e}")
            return []

    def get_tag_date(self, tag):
        """获取标签的日期"""
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%ad', '--date=short', tag],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return datetime.now().strftime('%Y-%m-%d')

    def format_version_section(self, version, commits, tag_date=None):
        """格式化单个版本的变更日志"""
        if not commits:
            return None

        lines = []
        lines.append(f"## [{version}] - {tag_date or 'Unreleased'}")
        lines.append("")

        # 按类型分组
        grouped = defaultdict(list)
        for commit in commits:
            grouped[commit['type']].append(commit)

        # 定义类型顺序
        type_order = ['Added', 'Changed', 'Fixed', 'Removed', 'Security']

        for commit_type in type_order:
            if commit_type not in grouped:
                continue

            type_commits = grouped[commit_type]
            lines.append(f"### {self.parser.type_names_cn[commit_type]} ({commit_type})")
            lines.append("")

            for commit in type_commits:
                # 添加破坏性变更标记
                prefix = "**BREAKING CHANGE:** " if commit['breaking'] else ""
                scope = f"**{commit['scope']}**: " if commit['scope'] else ""

                # 格式: description (commit_hash)
                desc = f"{prefix}{scope}{commit['description']}"
                lines.append(f"- {desc} ({commit['hash'][:8]})")

            lines.append("")

        return '\n'.join(lines)

    def generate(self, output_file='CHANGELOG.md'):
        """生成完整的 CHANGELOG.md"""
        print("🔍 正在分析 Git 历史和标签...")

        tags = self.get_tags()

        if not tags:
            print("⚠️  未找到版本标签，生成无版本日志...")
            return self.generate_without_tags(output_file)

        print(f"✅ 找到 {len(tags)} 个版本标签")

        # 生成日志内容
        lines = []
        lines.append("# Changelog")
        lines.append("")
        lines.append("所有重要变更都将记录在此文件中。")
        lines.append("")
        lines.append("格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),")
        lines.append("并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。")
        lines.append("")
        lines.append("---")
        lines.append("")

        # 获取每个版本的提交
        prev_tag = None
        version_sections = []

        for i, tag in enumerate(tags):
            # 获取标签日期
            tag_date = self.get_tag_date(tag)

            # 获取当前标签到上一个标签之间的提交
            commits = self.get_commits_between(prev_tag, tag)

            if commits:
                section = self.format_version_section(tag, commits, tag_date)
                if section:
                    version_sections.append(section)

            prev_tag = tag

        # 添加未发布的提交
        unreleased_commits = self.get_commits_between(prev_tag, None)
        if unreleased_commits:
            section = self.format_version_section("Unreleased", unreleased_commits)
            if section:
                version_sections.append(section)

        # 合并所有版本
        lines.extend(version_sections)

        # 写入文件
        content = '\n'.join(lines)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ 变更日志已生成: {output_file}")
        self.print_summary(tags, unreleased_commits)

    def generate_without_tags(self, output_file='CHANGELOG.md'):
        """生成没有版本标签的日志"""
        print("📊 正在生成无版本日志...")

        commits = self.get_commits_between(None, None)

        lines = []
        lines.append("# Changelog")
        lines.append("")
        lines.append("所有重要变更都将记录在此文件中。")
        lines.append("")
        lines.append("⚠️  未找到版本标签，建议使用语义化版本标签（如 v1.0.0）")
        lines.append("")
        lines.append("---")
        lines.append("")

        section = self.format_version_section("All Commits", commits)
        if section:
            lines.append(section)

        content = '\n'.join(lines)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ 变更日志已生成: {output_file}")
        print(f"📊 共包含 {len(commits)} 个提交")

    def print_summary(self, tags, unreleased):
        """打印生成摘要"""
        print()
        print("=" * 60)
        print("📋 生成摘要")
        print("=" * 60)

        type_counts = defaultdict(int)
        for commit in unreleased:
            type_counts[commit['type']] += 1

        print(f"  版本数量: {len(tags)}")
        print(f"  未发布提交: {len(unreleased)}")

        if type_counts:
            print()
            print("  未发布提交分类:")
            for commit_type, count in sorted(type_counts.items()):
                cn_name = self.parser.type_names_cn.get(commit_type, commit_type)
                print(f"    - {cn_name} ({commit_type}): {count}")


def main():
    """主函数"""
    print("🚀 变更日志生成器")
    print("=" * 60)

    # 检查是否在 Git 仓库中
    try:
        subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 错误: 当前目录不是 Git 仓库")
        print("💡 提示: 请在 Git 仓库根目录运行此脚本")
        return 1

    generator = ChangelogGenerator()
    generator.generate()

    print()
    print("📝 下一步操作:")
    print("  1. 查看 CHANGELOG.md 文件")
    print("  2. 根据需要调整内容")
    print("  3. 提交 CHANGELOG.md 到仓库")
    print("  4. 为新版本打标签（如 v1.0.0）")

    return 0


if __name__ == '__main__':
    exit(main())
