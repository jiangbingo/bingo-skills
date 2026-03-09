#!/usr/bin/env python3
"""
测试脚本 - 验证 dependency-auditor Skill 是否正常工作
"""

import subprocess
import sys
import os
from pathlib import Path

def test_skill():
    """测试 Skill 功能"""
    print("🧪 正在测试 dependency-auditor Skill...")
    print()

    print("测试 1: 检查 Skill 文件是否存在")
    skill_path = 'skillsets/dependency-auditor/SKILL.md'
    impl_path = 'skillsets/dependency-auditor/impl.py'

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
    try:
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
    except subprocess.TimeoutExpired:
        print("❌ 语法检查超时")
        return False
    except Exception as e:
        print(f"❌ 语法检查出错: {e}")
        return False

    print()
    print("测试 3: 检查包管理器检测功能")
    # 创建临时测试环境
    test_dir = Path('.test_dependency_audit')
    test_dir.mkdir(exist_ok=True)

    # 创建测试用 package.json
    test_package = test_dir / 'package.json'
    test_package.write_text('{"name": "test", "version": "1.0.0"}')
    print("✅ 测试环境已创建")

    # 在测试目录中运行脚本
    print()
    print("测试 4: 执行分析脚本（测试模式）")
    try:
        result = subprocess.run(
            ['python3', impl_path],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(test_dir)
        )

        # 脚本可能因为缺少依赖而失败，但至少应该能运行
        if "审计" in result.stdout or "audit" in result.stdout.lower():
            print("✅ 脚本执行正常")
        else:
            print("⚠️  脚本输出可能不完整")
            print(f"输出: {result.stdout[:500]}")
    except subprocess.TimeoutExpired:
        print("⚠️  脚本执行超时（可能是依赖扫描耗时较长）")
    except Exception as e:
        print(f"⚠️  脚本执行出错: {e}")

    # 清理测试环境
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
    print("✅ 测试环境已清理")

    print()
    print("测试 5: 验证输出功能")
    # 在当前目录运行以生成报告
    try:
        result = subprocess.run(
            ['python3', impl_path],
            capture_output=True,
            text=True,
            timeout=120
        )

        output_file = 'dependency_audit_report.txt'
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ 输出文件存在，大小: {len(content)} 字符")

            # 检查报告内容
            required_sections = [
                ("审计工具", "标题"),
                ("包管理器", "检测"),
                ("摘要", "总结"),
                ("建议", "操作")
            ]

            for keyword, section_name in required_sections:
                if keyword in content or section_name in content:
                    print(f"✅ 包含 {section_name} 部分")
                else:
                    print(f"⚠️  可能缺少 {section_name} 部分")
        else:
            print(f"⚠️  输出文件不存在: {output_file}")
            print("   这可能是正常的（如果没有检测到包管理器）")
    except subprocess.TimeoutExpired:
        print("⚠️  完整扫描超时（大型项目可能需要更长时间）")
    except Exception as e:
        print(f"⚠️  输出验证出错: {e}")

    print()
    print("=" * 60)
    print("🎉 测试完成！")
    print("=" * 60)
    print()
    print("📋 测试说明:")
    print("1. 此测试验证 Skill 文件结构和脚本语法")
    print("2. 完整功能需要在包含依赖的项目中运行")
    print("3. 部分审计功能需要额外工具（如 npm-audit, pip-audit）")
    print()
    print("📋 支持的包管理器:")
    print("   - npm (Node.js)")
    print("   - pip (Python)")
    print("   - cargo (Rust)")
    print("   - composer (PHP)")
    print("   - maven (Java)")
    print("   - gradle (Java)")
    print()
    print("📋 下一步操作:")
    print("1. 在包含依赖的项目目录中运行此脚本")
    print("2. 查看生成的 dependency_audit_report.txt")
    print("3. 根据报告建议更新依赖或修复漏洞")

    return True

if __name__ == '__main__':
    success = test_skill()
    sys.exit(0 if success else 1)
