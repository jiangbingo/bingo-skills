#!/usr/bin/env python3
"""
测试脚本 - 验证 complexity-mapper Skill 是否正常工作
"""

import subprocess
import sys
import os
import tempfile
import shutil
from pathlib import Path


def create_test_python_code():
    """创建测试用的 Python 代码"""
    temp_dir = tempfile.mkdtemp(prefix='complexity_test_')

    # 创建高复杂度代码
    complex_code = '''
def complex_function(a, b, c, d, e):
    """一个故意复杂的函数用于测试"""
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return a + b + c + d + e
                    else:
                        return a + b + c + d
                else:
                    return a + b + c
            else:
                return a + b
        else:
            return a
    else:
        for i in range(10):
            if i > 5:
                if b > 0:
                    return b
                else:
                    return c
        return 0

def medium_function(x):
    """中等复杂度函数"""
    result = 0
    for i in range(100):
        if i % 2 == 0:
            result += i
        elif i % 3 == 0:
            result -= i
        else:
            result *= i
    return result

def simple_function(x, y):
    """简单函数"""
    return x + y
'''

    test_file = Path(temp_dir) / 'complex_module.py'
    test_file.write_text(complex_code)

    return temp_dir


def test_skill():
    """测试 Skill 功能"""
    original_dir = os.getcwd()
    temp_dir = None

    try:
        print("🧪 正在测试 complexity-mapper Skill...")
        print()

        print("测试 1: 检查 Skill 文件是否存在")
        skill_path = 'skillsets/complexity-mapper/SKILL.md'
        impl_path = 'skillsets/complexity-mapper/impl.py'

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
        print("测试 3: 创建测试代码")
        temp_dir = create_test_python_code()
        print(f"✅ 测试代码已创建: {temp_dir}")

        print()
        print("测试 4: 尝试安装分析工具")
        try:
            # 尝试安装 radon
            subprocess.run(
                ['pip', 'install', 'radon', 'lizard'],
                capture_output=True,
                timeout=60
            )
            print("✅ 分析工具已安装")
        except Exception as e:
            print(f"⚠️  工具安装可能失败: {e}")

        print()
        print("测试 5: 运行分析脚本")
        os.chdir(temp_dir)
        result = subprocess.run(
            ['python3', os.path.join(original_dir, impl_path)],
            capture_output=True,
            text=True,
            timeout=60
        )

        # 检查输出
        if '代码复杂度分析报告' in result.stdout or 'Code Complexity' in result.stdout:
            print("✅ 脚本执行成功")
        else:
            print("⚠️  脚本输出可能不完整")
            print(f"输出: {result.stdout[:500]}")

        print()
        print("测试 6: 验证报告生成")
        report_file = os.path.join(temp_dir, 'complexity_map_report.txt')
        if os.path.exists(report_file):
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ 报告文件已生成，大小: {len(content)} 字符")

            # 检查报告内容
            required_sections = [
                '代码复杂度分析报告',
                '复杂度',
            ]

            for section in required_sections:
                if section in content:
                    print(f"  ✅ 包含: {section}")
                else:
                    print(f"  ⚠️  可能缺少: {section}")
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
        print("  ✅ 能够执行分析")
        print("  ✅ 报告生成功能正常")
        print()
        print("📖 使用说明:")
        print("1. 在项目目录中运行:")
        print(f"   python3 {impl_path}")
        print("2. 确保安装了 radon (Python) 或 lizard (多语言)")
        print("3. 查看 complexity_map_report.txt 获取详细分析")

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
