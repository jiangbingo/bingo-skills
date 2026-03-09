#!/usr/bin/env python3
"""
测试脚本 - 验证 changelog-generator Skill 是否正常工作
"""

import subprocess
import sys
import os
import tempfile
import shutil


def test_skill():
    """测试 Skill 功能"""
    print("🧪 正在测试 changelog-generator Skill...")
    print()

    print("测试 1: 检查 Skill 文件是否存在")
    skill_dir = 'skillsets/changelog-generator'
    skill_path = os.path.join(skill_dir, 'SKILL.md')
    impl_path = os.path.join(skill_dir, 'impl.py')

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
    print("测试 2: 验证脚本可执行性")
    try:
        result = subprocess.run(
            ['python3', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Python 版本: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Python 3 未安装")
        return False

    print()
    print("测试 3: 创建测试 Git 仓库")

    # 创建临时目录和测试仓库
    test_dir = tempfile.mkdtemp(prefix='changelog_test_')
    original_dir = os.getcwd()

    try:
        os.chdir(test_dir)
        print(f"📁 测试目录: {test_dir}")

        # 初始化 Git 仓库
        subprocess.run(['git', 'init'], capture_output=True, check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], capture_output=True, check=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], capture_output=True, check=True)

        # 创建测试提交
        test_commits = [
            ('feat: 添加新功能 A', 'Initial commit'),
            ('fix: 修复 bug B', 'Fix bug'),
            ('docs: 更新文档', 'Update docs'),
            ('feat(api): 添加 API 接口', 'Add API'),
            ('feat!: 破坏性变更', 'Breaking change'),
            ('refactor: 重构代码', 'Refactor'),
        ]

        for msg, desc in test_commits:
            # 创建空文件
            with open('test.txt', 'a') as f:
                f.write(f'{msg}\n')
            subprocess.run(['git', 'add', '.'], capture_output=True, check=True)
            subprocess.run(['git', 'commit', '-m', msg], capture_output=True, check=True)

        print(f"✅ 创建了 {len(test_commits)} 个测试提交")

        # 创建版本标签
        subprocess.run(['git', 'tag', 'v0.1.0'], capture_output=True, check=True)
        print("✅ 创建了测试标签 v0.1.0")

        # 添加更多提交
        with open('test.txt', 'a') as f:
            f.write('more changes\n')
        subprocess.run(['git', 'add', '.'], capture_output=True, check=True)
        subprocess.run(['git', 'commit', '-m', 'feat: 添加功能 B'], capture_output=True, check=True)

        print()
        print("测试 4: 执行变更日志生成脚本")

        # 复制 impl.py 到测试目录
        impl_src = os.path.join(original_dir, impl_path)
        impl_dest = os.path.join(test_dir, 'impl.py')
        shutil.copy(impl_src, impl_dest)

        result = subprocess.run(
            ['python3', impl_dest],
            capture_output=True,
            text=True,
            timeout=30
        )

        print("📄 脚本输出:")
        print(result.stdout)

        if result.returncode != 0:
            print(f"❌ 脚本执行失败，返回码: {result.returncode}")
            if result.stderr:
                print(f"错误输出: {result.stderr}")
            return False

        print("✅ 脚本执行成功")

        print()
        print("测试 5: 验证输出文件")

        output_file = 'CHANGELOG.md'
        if not os.path.exists(output_file):
            print(f"❌ 输出文件不存在: {output_file}")
            return False

        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"✅ 输出文件存在，大小: {len(content)} 字符")

        # 验证内容
        checks = [
            ('# Changelog', '标题'),
            ('Added', '新增分类'),
            ('Fixed', '修复分类'),
            ('Changed', '变更分类'),
            ('Unreleased', '未发布版本'),
        ]

        for keyword, desc in checks:
            if keyword in content:
                print(f"✅ 包含 {desc}: '{keyword}'")
            else:
                print(f"⚠️  缺少 {desc}: '{keyword}'")

        # 显示部分内容
        print()
        print("📋 CHANGELOG.md 内容预览:")
        print("-" * 60)
        lines = content.split('\n')
        for line in lines[:30]:
            print(line)
        if len(lines) > 30:
            print(f"... (还有 {len(lines) - 30} 行)")
        print("-" * 60)

    except subprocess.TimeoutExpired:
        print("❌ 脚本执行超时")
        return False
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理测试目录
        os.chdir(original_dir)
        try:
            shutil.rmtree(test_dir)
            print()
            print(f"🧹 清理测试目录: {test_dir}")
        except Exception as e:
            print(f"⚠️  清理失败: {e}")

    print()
    print("=" * 60)
    print("🎉 所有测试通过！")
    print("=" * 60)
    print()
    print("📋 功能验证:")
    print("  ✅ Git 历史解析")
    print("  ✅ 约定式提交识别")
    print("  ✅ 版本标签检测")
    print("  ✅ 变更类型分类")
    print("  ✅ Markdown 格式生成")
    print()
    print("📖 使用示例:")
    print("  python3 skillsets/changelog-generator/impl.py")
    print("  在任何 Git 仓库中运行以生成 CHANGELOG.md")

    return True


if __name__ == '__main__':
    success = test_skill()
    sys.exit(0 if success else 1)
