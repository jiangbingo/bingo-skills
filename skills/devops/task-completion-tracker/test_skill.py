#!/usr/bin/env python3
"""
测试脚本 - 验证 task-completion-tracker Skill 是否正常工作
"""

import subprocess
import sys
import os

def test_skill():
    """测试 Skill 功能"""
    print("🧪 正在测试 task-completion-tracker Skill...")
    print()

    print("测试 1: 检查 Skill 文件是否存在")
    skill_path = 'skillsets/task-completion-tracker/SKILL.md'
    impl_path = 'skillsets/task-completion-tracker/impl.py'

    if os.path.exists(skill_path):
        print(f"✅ Skill 定义文件存在: {skill_path}")
    else:
        print(f"❌ Skill 定义文件不存在: {skill_path}")
        return False

    if os.path.exists(impl_path):
        print(f"✅ 实现脚本存在: {impl_path}")
    else:
        print(f"❌ 实现脚本不存在: {impl_path}")
        return False

    print()
    print("测试 2: 检查是否在 Git 仓库中")
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.stdout.strip() == 'true':
            print("✅ 当前目录是 Git 仓库")
        else:
            print("⚠️  当前目录不是 Git 仓库")
            print("   此 skill 需要在 Git 仓库中运行")
            return False
    except FileNotFoundError:
        print("❌ 未找到 git 命令，请确保已安装 Git")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Git 命令执行超时")
        return False
    except Exception as e:
        print(f"❌ Git 检查出错: {e}")
        return False

    print()
    print("测试 3: 执行任务完成分析")
    try:
        result = subprocess.run(
            ['python3', impl_path],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print("✅ 脚本执行成功")
            print(f"✅ 报告已生成: task_completion_report.txt")

            # 显示部分输出
            output_lines = result.stdout.strip().split('\n')
            print("\n脚本输出:")
            for line in output_lines[-15:]:  # 显示最后15行
                print(f"  {line}")
        else:
            print(f"❌ 脚本执行失败，返回码: {result.returncode}")
            print(f"错误输出: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ 脚本执行超时")
        return False
    except Exception as e:
        print(f"❌ 脚本执行出错: {e}")
        return False

    print()
    print("测试 4: 验证输出文件")
    output_file = 'task_completion_report.txt'
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ 报告文件存在")
        print(f"✅ 报告大小: {len(content)} 字符")

        # 检查报告内容的关键部分
        checks = [
            ('标题', '任务完成追踪分析报告' in content),
            ('任务类型分布', '任务类型分布' in content),
            ('项目速度分析', '项目速度分析' in content),
            ('活跃时段分析', '活跃时段分析' in content),
            ('洞察与建议', '洞察与建议' in content),
        ]

        print("\n报告内容检查:")
        all_passed = True
        for name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {name}")
            if not passed:
                all_passed = False

        if not all_passed:
            return False
    else:
        print(f"❌ 报告文件不存在: {output_file}")
        return False

    print()
    print("=" * 60)
    print("🎉 所有测试通过！")
    print("=" * 60)
    print()
    print("📋 下一步操作:")
    print("1. 查看 task_completion_report.txt 获取详细分析")
    print("2. 关注 Bug/Feature 比例，评估代码质量")
    print("3. 定期运行此分析以跟踪项目速度")
    print("4. 根据任务类型分布调整团队资源分配")

    return True

if __name__ == '__main__':
    success = test_skill()
    sys.exit(0 if success else 1)
