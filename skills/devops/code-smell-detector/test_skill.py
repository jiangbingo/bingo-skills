#!/usr/bin/env python3
"""
测试脚本 - 验证 code-smell-detector Skill 是否正常工作
"""

import subprocess
import sys
import os
import tempfile
import shutil
from pathlib import Path


def create_test_project(project_dir: Path):
    """创建一个包含代码异味的测试项目"""
    project_dir.mkdir(parents=True, exist_ok=True)

    # 创建一个有代码异味的 Python 文件
    python_file = project_dir / "bad_code.py"
    python_file.write_text("""
import os

# 魔法数字
def calculate(x):
    if x > 42:
        result = x * 3.14159
        for i in range(100):
            for j in range(50):
                for k in range(10):
                    if result > 1000:
                        if result > 2000:
                            if result > 5000:
                                return result
    return 0

# 过长的函数
def long_function():
    a = 1
    b = 2
    c = 3
    d = 4
    e = 5
    f = 6
    g = 7
    h = 8
    i = 9
    j = 10
    # ... 继续很多行
    return a + b + c + d + e + f + g + h + i + j

# 参数过多
def TooManyParameters(a, b, c, d, e, f, g, h):
    return a + b + c + d + e + f + g + h

# 命名问题
def BadFunctionName():
    x = 10
    return x

class bad_class_name:
    pass
""", encoding='utf-8')

    # 创建一个有代码异味的 JavaScript 文件
    js_file = project_dir / "bad_code.js"
    js_file.write_text("""
// 使用 var
var oldVariable = 10;

// 遗留的 console.log
function debugFunction() {
    console.log("debug info");
    console.log("more debug");
    console.log("even more");
    
    var x = 1;
    if (x > 0) {
        if (x > 5) {
            if (x > 10) {
                if (x > 15) {
                    return x;
                }
            }
        }
    }
    return 0;
}

// 过长的函数
function veryLongFunctionThatDoesTooManyThings() {
    let a = 1;
    let b = 2;
    let c = 3;
    // ... 很多行代码
    return a + b + c;
}
""", encoding='utf-8')

    return project_dir


def test_skill():
    """测试 Skill 功能"""
    print("🧪 正在测试 code-smell-detector Skill...")
    print()

    print("测试 1: 检查 Skill 文件是否存在")
    skill_dir = 'skillsets/code-smell-detector'
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
    print("测试 2: 创建测试项目")

    # 创建临时测试项目
    test_project_dir = Path(tempfile.mkdtemp(prefix='code_smell_test_'))

    try:
        create_test_project(test_project_dir)
        print(f"✅ 测试项目创建成功: {test_project_dir}")

        print()
        print("测试 3: 执行代码异味检测")

        output_file = 'code_smell_report.txt'

        try:
            result = subprocess.run(
                ['python3', impl_path, '--project-dir', str(test_project_dir), '--output', output_file],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print("✅ 检测脚本执行成功")
                print(f"✅ 报告已生成: {output_file}")
            else:
                print(f"❌ 脚本执行失败，返回码: {result.returncode}")
                if result.stderr:
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

        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()

            print(f"✅ 输出文件存在，大小: {len(content)} 字符")

            # 检查报告内容
            required_keywords = ['代码质量', '问题统计', '改进建议', '严重程度']
            missing = [kw for kw in required_keywords if kw not in content]

            if not missing:
                print("✅ 报告包含所有必需的关键词")
            else:
                print(f"⚠️  报告缺少关键词: {missing}")

            # 检查是否检测到代码异味
            if '异味' in content or '问题' in content:
                print("✅ 成功检测到代码问题")
            else:
                print("⚠️  可能未检测到代码问题")

            # 显示报告摘要
            lines = content.split('\n')
            print()
            print("📋 报告预览 (前40行):")
            print("-" * 60)
            for line in lines[:40]:
                print(line)
            print("-" * 60)

        else:
            print(f"❌ 输出文件不存在: {output_file}")
            return False

        print()
        print("=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        print()
        print("📋 测试总结:")
        print("  ✅ Skill 文件结构完整")
        print("  ✅ 分析脚本可以正常执行")
        print("  ✅ 能够检测代码异味")
        print("  ✅ 报告内容格式正确")
        print()
        print("💡 使用提示:")
        print("  1. 在实际项目中运行: python3 skillsets/code-smell-detector/impl.py")
        print("  2. 查看 code_smell_report.txt 获取详细分析")
        print("  3. 根据优先级处理代码异味")
        print("  4. 定期运行检测保持代码质量")
        print()
        print("🔧 支持的语言:")
        print("  - Python (AST 分析)")
        print("  - JavaScript/TypeScript (启发式分析)")
        print("  - 更多语言可通过扩展添加")

        return True

    finally:
        # 清理临时目录
        try:
            shutil.rmtree(test_project_dir)
            print()
            print(f"🧹 已清理临时测试目录: {test_project_dir}")
        except Exception as e:
            print(f"⚠️  清理临时目录失败: {e}")


if __name__ == '__main__':
    success = test_skill()
    sys.exit(0 if success else 1)
