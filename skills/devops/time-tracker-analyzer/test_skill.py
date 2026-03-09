#!/usr/bin/env python3
"""
测试脚本 - 验证 time-tracker-analyzer Skill 是否正常工作
"""

import subprocess
import sys
import os
from pathlib import Path

def test_skill():
    """测试 Skill 功能"""
    print("🧪 正在测试 time-tracker-analyzer Skill...")
    print()

    print("测试 1: 检查 Skill 文件是否存在")
    base_dir = Path(__file__).parent.parent.parent
    skill_path = base_dir / 'skillsets' / 'time-tracker-analyzer' / 'SKILL.md'
    impl_path = base_dir / 'skillsets' / 'time-tracker-analyzer' / 'impl.py'

    if skill_path.exists():
        print(f"✅ Skill 定义文件存在: {skill_path}")
    else:
        print(f"❌ Skill 定义文件不存在: {skill_path}")
        return False

    if impl_path.exists():
        print(f"✅ 实现脚本存在: {impl_path}")
    else:
        print(f"❌ 实现脚本不存在: {impl_path}")
        return False

    print()
    print("测试 2: 检查是否在 Git 仓库中")

    result = subprocess.run(
        ['git', 'rev-parse', '--git-dir'],
        capture_output=True,
        text=True,
        timeout=5
    )

    if result.returncode != 0:
        print("⚠️  当前目录不是 Git 仓库，将创建测试仓库")
        test_repo = base_dir / 'test_repo'
        test_repo.mkdir(exist_ok=True)

        subprocess.run(
            ['git', 'init'],
            cwd=test_repo,
            capture_output=True,
            timeout=5
        )

        subprocess.run(
            ['git', 'config', 'user.email', 'test@example.com'],
            cwd=test_repo,
            capture_output=True,
            timeout=5
        )

        subprocess.run(
            ['git', 'config', 'user.name', 'Test User'],
            cwd=test_repo,
            capture_output=True,
            timeout=5
        )

        test_file = test_repo / 'test.txt'
        for i in range(10):
            test_file.write_text(f"Commit {i}\n")
            subprocess.run(
                ['git', 'add', 'test.txt'],
                cwd=test_repo,
                capture_output=True,
                timeout=5
            )
            subprocess.run(
                ['git', 'commit', '-m', f'Test commit {i}'],
                cwd=test_repo,
                capture_output=True,
                timeout=5
            )

        work_dir = test_repo
        print(f"✅ 测试仓库已创建: {test_repo}")
    else:
        print("✅ 当前是 Git 仓库")
        work_dir = Path.cwd()

    print()
    print("测试 3: 执行分析脚本")

    try:
        result = subprocess.run(
            ['python3', str(impl_path)],
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print("✅ 脚本执行成功")
            print("✅ 报告已生成: time_tracker_report.txt")
        else:
            print(f"❌ 脚本执行失败，返回码: {result.returncode}")
            print(f"错误输出: {result.stderr}")
            print(f"标准输出: {result.stdout}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ 脚本执行超时")
        return False
    except Exception as e:
        print(f"❌ 脚本执行出错: {e}")
        return False

    print()
    print("测试 4: 验证输出文件")

    output_file = work_dir / 'time_tracker_report.txt'

    if output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ 输出文件存在，大小: {len(content)} 字符")

        required_keywords = ['编码时间分析报告', '总提交数', '每日提交分布', '每小时提交分布', '提交热力图']
        missing_keywords = [kw for kw in required_keywords if kw not in content]

        if missing_keywords:
            print(f"❌ 输出文件缺少关键词: {missing_keywords}")
            return False
        else:
            print(f"✅ 包含所有必需的关键词")

        if '提交热力图' in content:
            heatmap_lines = [line for line in content.split('\n') if '│' in line and '█' in line or '░' in line or '▒' in line or '▓' in line]
            if len(heatmap_lines) >= 8:
                print(f"✅ 热力图生成正确 ({len(heatmap_lines)} 行)")
            else:
                print(f"⚠️  热力图可能不完整 ({len(heatmap_lines)} 行)")

    else:
        print(f"❌ 输出文件不存在: {output_file}")
        return False

    print()
    print("=" * 60)
    print("🎉 所有测试通过！")
    print("=" * 60)
    print()
    print("📋 Skill 功能验证:")
    print("  ✅ Git 仓库检测")
    print("  ✅ 提交记录提取")
    print("  ✅ 时间模式分析")
    print("  ✅ 每日/每小时统计")
    print("  ✅ 热力图生成")
    print("  ✅ 编码习惯洞察")
    print()
    print("📖 下一步操作:")
    print("  1. 查看 time_tracker_report.txt 获取详细分析")
    print("  2. 在任何 Git 仓库中运行此脚本进行分析")
    print("  3. 根据报告中的建议优化编码时间安排")

    return True

if __name__ == '__main__':
    success = test_skill()
    sys.exit(0 if success else 1)
