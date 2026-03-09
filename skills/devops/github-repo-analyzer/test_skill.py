#!/usr/bin/env python3
"""
测试脚本 - 验证 github-repo-analyzer Skill 是否正常工作
"""

import subprocess
import sys

def test_skill():
    """测试 Skill 功能"""
    print("🧪 正在测试 github-repo-analyzer Skill...")
    print()
    
    print("测试 1: 检查 Skill 文件是否存在")
    import os
    skill_path = 'skillsets/github-repo-analyzer/SKILL.md'
    impl_path = 'skillsets/github-repo-analyzer/impl.py'
    
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
    print("测试 2: 执行分析脚本")
    try:
        result = subprocess.run(
            ['python3', impl_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ 脚本执行成功")
            print(f"✅ 报告已生成: repos_analysis_report.txt")
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
    print("测试 3: 验证输出文件")
    output_file = 'repos_analysis_report.txt'
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ 输出文件存在，大小: {len(content)} 字符")
        print(f"✅ 包含 {content.count('个')} 个'字符")
    else:
        print(f"❌ 输出文件不存在: {output_file}")
        return False
    
    print()
    print("=" * 60)
    print("🎉 所有测试通过！")
    print("=" * 60)
    print()
    print("📋 下一步操作:")
    print("1. 查看 repos_analysis_report.txt 获取详细分析")
    print("2. 根据报告中的建议进行仓库清理")
    print("3. 定期重新运行此分析以跟踪仓库状态")
    
    return True

if __name__ == '__main__':
    success = test_skill()
    sys.exit(0 if success else 1)
