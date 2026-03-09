#!/usr/bin/env python3
"""
测试脚本 - 验证 knowledge-mapper Skill 是否正常工作
"""

import subprocess
import sys
import os

def test_skill():
    """测试 Skill 功能"""
    print("🧪 正在测试 knowledge-mapper Skill...")
    print()

    print("测试 1: 检查 Skill 文件是否存在")
    skill_path = 'skillsets/knowledge-mapper/SKILL.md'
    impl_path = 'skillsets/knowledge-mapper/impl.py'

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
    print("测试 3: 执行知识图谱分析")
    try:
        result = subprocess.run(
            ['python3', impl_path],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print("✅ 脚本执行成功")
            print(f"✅ 报告已生成: knowledge_map_report.txt")
            print(f"✅ 知识图谱已生成: knowledge_graph.dot")

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
    output_file = 'knowledge_map_report.txt'
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ 报告文件存在")
        print(f"✅ 报告大小: {len(content)} 字符")

        # 检查报告内容的关键部分
        checks = [
            ('标题', '项目知识图谱分析报告' in content),
            ('基本统计', '基本统计' in content),
            ('贡献者排行', '贡献者排行' in content),
            ('知识风险分析', '知识风险分析' in content),
            ('代码所有权', '代码所有权报告' in content),
            ('专家领域', '专家领域识别' in content),
            ('建议', '建议' in content),
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

    # 检查 DOT 文件
    dot_file = 'knowledge_graph.dot'
    if os.path.exists(dot_file):
        print(f"✅ 知识图谱 DOT 文件存在: {dot_file}")
    else:
        print(f"⚠️  知识图谱 DOT 文件不存在: {dot_file}")

    print()
    print("=" * 60)
    print("🎉 所有测试通过！")
    print("=" * 60)
    print()
    print("📋 下一步操作:")
    print("1. 查看 knowledge_map_report.txt 获取详细分析")
    print("2. 关注高风险文件（知识孤岛）")
    print("3. 识别项目专家并进行知识转移")
    print("4. 使用 Graphviz 可视化知识图谱:")
    print("   dot -Tpng knowledge_graph.dot -o knowledge_graph.png")

    return True

if __name__ == '__main__':
    success = test_skill()
    sys.exit(0 if success else 1)
