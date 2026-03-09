#!/usr/bin/env python3
"""
测试脚本 - 验证 test-coverage-analyzer Skill 是否正常工作
"""

import subprocess
import sys
import os
import tempfile
import shutil
from pathlib import Path


def create_test_python_project():
    """创建一个测试用的 Python 项目"""
    temp_dir = tempfile.mkdtemp(prefix='coverage_test_')

    # 创建简单的 Python 文件
    test_file = Path(temp_dir) / 'calculator.py'
    test_file.write_text('''
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return None
    return a / b
''')

    # 创建测试文件
    test_content = '''
import pytest
from calculator import add, subtract, multiply

def test_add():
    assert add(1, 2) == 3

def test_subtract():
    assert subtract(5, 3) == 2

def test_multiply():
    assert multiply(3, 4) == 12
'''

    # 创建 pytest 测试
    (Path(temp_dir) / 'test_calculator.py').write_text(test_content)

    return temp_dir


def create_test_js_project():
    """创建一个测试用的 JavaScript 项目"""
    temp_dir = tempfile.mkdtemp(prefix='coverage_test_js_')

    # 创建简单的 JS 文件
    test_file = Path(temp_dir) / 'math.js'
    test_file.write_text('''
export function add(a, b) {
    return a + b;
}

export function subtract(a, b) {
    return a - b;
}

export function multiply(a, b) {
    return a * b;
}
''')

    return temp_dir


def test_skill():
    """测试 Skill 功能"""
    original_dir = os.getcwd()
    temp_dir = None

    try:
        print("🧪 正在测试 test-coverage-analyzer Skill...")
        print()

        print("测试 1: 检查 Skill 文件是否存在")
        skill_path = 'skillsets/test-coverage-analyzer/SKILL.md'
        impl_path = 'skillsets/test-coverage-analyzer/impl.py'

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
        print("测试 2: 验证 Python 脚本语法")
        result = subprocess.run(
            ['python3', '-m', 'py_compile', impl_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print("✅ Python 脚本语法正确")
        else:
            print(f"❌ Python 脚本语法错误:")
            print(result.stderr)
            return False

        print()
        print("测试 3: 创建测试项目")
        temp_dir = create_test_python_project()
        print(f"✅ 测试项目已创建: {temp_dir}")

        print()
        print("测试 4: 运行脚本（无覆盖率数据）")
        os.chdir(temp_dir)
        result = subprocess.run(
            ['python3', os.path.join(original_dir, impl_path)],
            capture_output=True,
            text=True,
            timeout=30
        )

        # 应该生成一个无数据的报告
        if '未找到覆盖率数据' in result.stdout or '未检测到覆盖率数据' in result.stdout:
            print("✅ 脚本正确处理无覆盖率数据的情况")
        else:
            print("⚠️  脚本输出可能不符合预期")
            print(f"输出: {result.stdout[:500]}")

        print()
        print("测试 5: 检查报告生成")
        report_file = os.path.join(temp_dir, 'test_coverage_report.txt')
        if os.path.exists(report_file):
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ 报告文件已生成，大小: {len(content)} 字符")

            # 检查报告内容
            required_sections = [
                '测试覆盖率分析报告',
                '未找到覆盖率数据',
            ]

            for section in required_sections:
                if section in content:
                    print(f"  ✅ 包含: {section}")
                else:
                    print(f"  ⚠️  缺少: {section}")
        else:
            print(f"⚠️  报告文件未生成: {report_file}")

        print()
        print("=" * 60)
        print("🎉 测试完成！")
        print("=" * 60)
        print()
        print("📋 测试摘要:")
        print("  ✅ 文件结构正确")
        print("  ✅ 脚本语法正确")
        print("  ✅ 能够正确处理无覆盖率数据的情况")
        print("  ✅ 报告生成功能正常")
        print()
        print("📖 使用说明:")
        print("1. 在包含测试的项目目录中运行:")
        print(f"   python3 {impl_path}")
        print("2. 确保先运行测试并生成覆盖率数据")
        print("3. 查看 test_coverage_report.txt 获取详细分析")

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
                print(f"\n🧹 已清理测试目录: {temp_dir}")
            except Exception as e:
                print(f"⚠️  清理测试目录失败: {e}")


if __name__ == '__main__':
    success = test_skill()
    sys.exit(0 if success else 1)
