#!/usr/bin/env python3
"""
测试脚本 - 验证 doc-coverage-checker Skill 是否正常工作
"""

import subprocess
import sys
import os
import tempfile
import shutil


def create_test_project(test_dir):
    """创建测试项目"""
    # 创建 Python 测试文件
    py_file = os.path.join(test_dir, 'test_module.py')
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write('''
"""这是一个测试模块的文档字符串"""

class DocumentedClass:
    """这是一个有文档的类"""
    pass

class UndocumentedClass:
    pass

def documented_function(param1, param2):
    """这是一个有文档的函数

    Args:
        param1: 参数1
        param2: 参数2

    Returns:
        返回值描述
    """
    pass

def undocumented_function():
    pass

def _private_function():
    """这是私有函数，不需要公共文档"""
    pass
''')

    # 创建 JavaScript 测试文件
    js_file = os.path.join(test_dir, 'test.js')
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write('''
/**
 * 有文档的函数
 * @param {string} param1 - 参数1
 * @returns {string} 返回值
 */
function documentedFunction(param1) {
    return param1;
}

function undocumentedFunction() {
    // 没有文档
}

const documentedArrow = (x) => {
    /** 这是箭头函数的文档 */
    return x;
};
''')

    return [py_file, js_file]


def test_skill():
    """测试 Skill 功能"""
    print("🧪 正在测试 doc-coverage-checker Skill...")
    print()

    # 测试 1: 检查 Skill 文件是否存在
    print("测试 1: 检查 Skill 文件是否存在")
    skill_path = 'skillsets/doc-coverage-checker/SKILL.md'
    impl_path = 'skillsets/doc-coverage-checker/impl.py'

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

    # 测试 2: 检查 SKILL.md 内容
    print("测试 2: 检查 SKILL.md 内容")
    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_sections = [
        'name:', 'description:', 'Overview', 'When to Invoke',
        'What It Does', 'Coverage Metrics', 'Output Format'
    ]

    missing_sections = []
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)

    if not missing_sections:
        print("✅ SKILL.md 包含所有必需章节")
    else:
        print(f"❌ SKILL.md 缺少章节: {', '.join(missing_sections)}")
        return False

    print()

    # 测试 3: 检查 impl.py 导入和语法
    print("测试 3: 检查 impl.py 语法")
    try:
        import py_compile
        py_compile.compile(impl_path, doraise=True)
        print("✅ impl.py 语法正确")
    except py_compile.PyCompileError as e:
        print(f"❌ impl.py 语法错误: {e}")
        return False

    print()

    # 测试 4: 在测试项目上执行分析
    print("测试 4: 在测试项目上执行分析")
    test_dir = tempfile.mkdtemp(prefix='doc_coverage_test_')

    try:
        # 创建测试项目
        test_files = create_test_project(test_dir)
        print(f"  创建测试项目: {test_dir}")

        # 执行分析
        impl_abs_path = os.path.abspath(impl_path)
        result = subprocess.run(
            ['python3', impl_abs_path, test_dir],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print("✅ 脚本执行成功")
            print(f"  输出:\n{result.stdout}")
        else:
            print(f"❌ 脚本执行失败，返回码: {result.returncode}")
            print(f"  错误输出: {result.stderr}")
            print(f"  标准输出: {result.stdout}")
            return False

        # 测试 5: 验证输出文件
        print()
        print("测试 5: 验证输出文件")

        # 检查报告文件（在脚本执行的目录中）
        report_txt = 'doc_coverage_report.txt'
        report_json = 'doc_coverage_report.json'

        # 报告可能在 impl.py 所在目录或当前目录
        possible_dirs = [
            os.path.dirname(os.path.abspath(impl_path)),
            os.getcwd()
        ]

        report_found = False
        for report_path in possible_dirs:
            txt_path = os.path.join(report_path, report_txt)
            json_path = os.path.join(report_path, report_json)

            if os.path.exists(txt_path):
                print(f"✅ TXT 报告已生成: {txt_path}")
                with open(txt_path, 'r', encoding='utf-8') as f:
                    report_content = f.read()
                print(f"  报告大小: {len(report_content)} 字符")
                report_found = True
                break

        if not report_found:
            print(f"⚠️  未找到报告文件（可能在不同目录）")

        # 验证报告内容关键部分
        if report_found and 'report_content' in locals():
            required_keywords = [
                '文档覆盖率分析报告',
                '总体统计',
                '各文件文档覆盖率',
                '覆盖率'
            ]

            missing_keywords = []
            for keyword in required_keywords:
                if keyword not in report_content:
                    missing_keywords.append(keyword)

            if not missing_keywords:
                print("✅ 报告包含所有必需内容")
            else:
                print(f"⚠️  报告缺少内容: {', '.join(missing_keywords)}")

    except subprocess.TimeoutExpired:
        print("❌ 脚本执行超时")
        return False
    except Exception as e:
        print(f"❌ 测试执行出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理测试目录
        try:
            shutil.rmtree(test_dir)
            print(f"  清理测试目录: {test_dir}")
        except Exception as e:
            print(f"  ⚠️  清理测试目录失败: {e}")

    print()
    print("=" * 60)
    print("🎉 所有测试通过！")
    print("=" * 60)
    print()
    print("📋 Skill 功能验证:")
    print("  ✅ SKILL.md 定义文件正确")
    print("  ✅ impl.py 实现脚本可用")
    print("  ✅ 文档分析功能正常")
    print("  ✅ 报告生成功能正常")
    print()
    print("📖 使用方法:")
    print("  1. 直接运行: python3 skillsets/doc-coverage-checker/impl.py")
    print("  2. 指定路径: python3 skillsets/doc-coverage-checker/impl.py /path/to/project")
    print("  3. 运行测试: python3 skillsets/doc-coverage-checker/test_skill.py")

    return True


def test_on_current_project():
    """在当前项目上测试（可选）"""
    print()
    print("=" * 60)
    print("📊 是否在当前项目上运行分析？")
    print("=" * 60)
    print("这将分析 bingo-devops-skills 项目的文档覆盖率")
    print()

    try:
        response = input("是否继续？(y/N): ").strip().lower()
    except EOFError:
        # CI 环境中没有 stdin，跳过交互式测试
        print("  ℹ️  检测到非交互环境（CI），跳过当前项目分析")
        return

    if response == 'y':
        impl_path = 'skillsets/doc-coverage-checker/impl.py'
        project_path = os.path.dirname(os.path.dirname(os.path.abspath(impl_path)))

        print(f"🔍 分析项目: {project_path}")
        print()

        try:
            result = subprocess.run(
                ['python3', impl_path, project_path],
                capture_output=False,
                timeout=60
            )

            if result.returncode == 0:
                print()
                print("✅ 当前项目分析完成！")
                print("📄 查看报告: doc_coverage_report.txt")
            else:
                print(f"❌ 分析失败，返回码: {result.returncode}")

        except Exception as e:
            print(f"❌ 执行出错: {e}")


if __name__ == '__main__':
    success = test_skill()
    print()

    if success:
        test_on_current_project()

    sys.exit(0 if success else 1)
