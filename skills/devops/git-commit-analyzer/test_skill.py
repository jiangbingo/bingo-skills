#!/usr/bin/env python3
"""
测试脚本 - 验证 git-commit-analyzer Skill 是否正常工作
"""

import subprocess
import sys
import os
import tempfile
import shutil

def setup_test_repo():
    """创建一个临时测试仓库"""
    temp_dir = tempfile.mkdtemp(prefix='git_commit_analyzer_test_')
    os.chdir(temp_dir)

    # 初始化 Git 仓库
    subprocess.run(['git', 'init'], capture_output=True)
    subprocess.run(['git', 'config', 'user.name', 'Test User'], capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], capture_output=True)

    # 创建一些测试提交
    test_commits = [
        ('feat: 添加新功能', 'feature file'),
        ('fix: 修复bug', 'bugfix file'),
        ('docs: 更新文档', 'docs file'),
        ('style: 代码格式化', 'style file'),
        ('refactor: 重构代码', 'refactor file'),
        ('test: 添加测试', 'test file'),
        ('chore: 维护任务', 'chore file'),
        ('feat: 添加用户登录', 'login feature'),
        ('fix: 修复登录bug', 'login fix'),
        ('docs: 更新README', 'readme update'),
    ]

    for i, (msg, content) in enumerate(test_commits):
        with open(f'file{i}.txt', 'w') as f:
            f.write(content)
        subprocess.run(['git', 'add', f'file{i}.txt'], capture_output=True)
        subprocess.run(['git', 'commit', '-m', msg], capture_output=True)

    return temp_dir

def test_skill():
    """测试 Skill 功能"""
    original_dir = os.getcwd()
    temp_dir = None

    try:
        print("🧪 正在测试 git-commit-analyzer Skill...")
        print()

        print("测试 1: 检查 Skill 文件是否存在")
        skill_path = 'skillsets/git-commit-analyzer/SKILL.md'
        impl_path = 'skillsets/git-commit-analyzer/impl.py'

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
        print("测试 2: 创建测试仓库")
        temp_dir = setup_test_repo()
        print(f"✅ 测试仓库已创建: {temp_dir}")

        print()
        print("测试 3: 执行分析脚本")
        result = subprocess.run(
            ['python3', os.path.join(original_dir, impl_path)],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print("✅ 脚本执行成功")
            print(result.stdout)
        else:
            print(f"❌ 脚本执行失败，返回码: {result.returncode}")
            print(f"标准输出: {result.stdout}")
            print(f"错误输出: {result.stderr}")
            return False

        print()
        print("测试 4: 验证输出文件")
        output_file = os.path.join(temp_dir, 'commit_analysis_report.txt')
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ 输出文件存在，大小: {len(content)} 字符")

            # 检查报告内容
            required_sections = [
                'Git 提交历史分析报告',
                '基础统计',
                '贡献者排行榜',
                '提交时段热图',
                '提交信息质量分析',
                '改进建议'
            ]

            for section in required_sections:
                if section in content:
                    print(f"  ✅ 包含章节: {section}")
                else:
                    print(f"  ❌ 缺少章节: {section}")
                    return False
        else:
            print(f"❌ 输出文件不存在: {output_file}")
            return False

        print()
        print("测试 5: 检查脚本可执行性")
        impl_full_path = os.path.join(original_dir, impl_path)
        if os.access(impl_full_path, os.R_OK):
            print("✅ 脚本可读")
        else:
            print("❌ 脚本不可读")
            return False

        print()
        print("=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        print()
        print("📋 测试摘要:")
        print("  ✅ 文件结构正确")
        print("  ✅ 脚本可以正常执行")
        print("  ✅ 报告生成成功")
        print("  ✅ 报告内容完整")
        print()
        print("📖 使用说明:")
        print("1. 在任何 Git 仓库目录中运行:")
        print(f"   python3 {impl_path}")
        print("2. 查看生成的 commit_analysis_report.txt 文件")
        print("3. 触发词: '分析提交历史'、'查看代码贡献统计'、'谁提交最多'")

        return True

    except subprocess.TimeoutExpired:
        print("❌ 脚本执行超时")
        return False
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理临时目录
        if temp_dir and os.path.exists(temp_dir):
            try:
                os.chdir(original_dir)
                shutil.rmtree(temp_dir)
                print(f"\n🧹 已清理测试仓库: {temp_dir}")
            except Exception as e:
                print(f"⚠️  清理测试仓库失败: {e}")

if __name__ == '__main__':
    success = test_skill()
    sys.exit(0 if success else 1)
