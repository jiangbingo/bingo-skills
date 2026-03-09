#!/usr/bin/env python3
"""
代码异味检测器
支持 Python、JavaScript/TypeScript、Go 等语言的代码质量分析
"""

import os
import re
import ast
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class CodeSmell:
    """代码异味数据结构"""

    def __init__(self, severity: str, category: str, message: str,
                 file_path: str, line_no: int, suggestion: str = ""):
        self.severity = severity  # critical, high, medium, low
        self.category = category  # complexity, duplication, naming, design, dead_code
        self.message = message
        self.file_path = file_path
        self.line_no = line_no
        self.suggestion = suggestion

    def __repr__(self):
        return f"[{self.severity.upper()}] {self.file_path}:{self.line_no} - {self.message}"


class PythonAnalyzer:
    """Python 代码分析器"""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.smells: List[CodeSmell] = []

    # 分析 Python 文件
    def analyze_file(self, file_path: Path) -> List[CodeSmell]:
        """分析单个 Python 文件"""
        smells = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content, filename=str(file_path))

            # 分析函数复杂度
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    smells.extend(self._analyze_function(node, file_path))

            # 检测命名问题
            smells.extend(self._check_naming(tree, file_path))

            # 检测魔法数字
            smells.extend(self._check_magic_numbers(content, file_path))

        except Exception as e:
            pass  # 跳过无法解析的文件

        return smells

    def _analyze_function(self, node, file_path: Path) -> List[CodeSmell]:
        """分析函数的代码异味"""
        smells = []

        # 计算圈复杂度
        complexity = self._calculate_complexity(node)

        # 检查函数长度
        func_length = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0

        # 检查参数数量
        param_count = len(node.args.args)

        # 检查嵌套深度
        max_depth = self._calculate_nesting_depth(node)

        # 生成报告
        if complexity > 15:
            smells.append(CodeSmell(
                severity="high",
                category="complexity",
                message=f"函数 '{node.name}' 圈复杂度过高 ({complexity})",
                file_path=str(file_path.relative_to(self.project_dir)),
                line_no=node.lineno,
                suggestion=f"考虑将函数 '{node.name}' 拆分为更小的函数"
            ))

        if func_length > 50:
            smells.append(CodeSmell(
                severity="medium",
                category="complexity",
                message=f"函数 '{node.name}' 过长 ({func_length} 行)",
                file_path=str(file_path.relative_to(self.project_dir)),
                line_no=node.lineno,
                suggestion=f"建议将函数 '{node.name}' 拆分为更小的函数"
            ))

        if param_count > 5:
            smells.append(CodeSmell(
                severity="medium",
                category="design",
                message=f"函数 '{node.name}' 参数过多 ({param_count} 个)",
                file_path=str(file_path.relative_to(self.project_dir)),
                line_no=node.lineno,
                suggestion="考虑使用配置对象或数据类来封装参数"
            ))

        if max_depth > 4:
            smells.append(CodeSmell(
                severity="medium",
                category="complexity",
                message=f"函数 '{node.name}' 嵌套过深 ({max_depth} 层)",
                file_path=str(file_path.relative_to(self.project_dir)),
                line_no=node.lineno,
                suggestion="考虑使用早返回(early return)或提取函数来减少嵌套"
            ))

        return smells

    def _calculate_complexity(self, node) -> int:
        """计算圈复杂度"""
        complexity = 1  # 基础复杂度

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1

        return complexity

    def _calculate_nesting_depth(self, node) -> int:
        """计算最大嵌套深度"""
        max_depth = 0

        def _depth(n, current=0):
            nonlocal max_depth
            max_depth = max(max_depth, current)

            if isinstance(n, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                current += 1

            for child in ast.iter_child_nodes(n):
                _depth(child, current)

        _depth(node)
        return max_depth

    def _check_naming(self, tree, file_path: Path) -> List[CodeSmell]:
        """检查命名规范"""
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查函数名是否小写加下划线
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    smells.append(CodeSmell(
                        severity="low",
                        category="naming",
                        message=f"函数名 '{node.name}' 不符合 PEP8 规范",
                        file_path=str(file_path.relative_to(self.project_dir)),
                        line_no=node.lineno,
                        suggestion="函数名应使用小写字母和下划线"
                    ))

            elif isinstance(node, ast.ClassDef):
                # 检查类名是否驼峰命名
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    smells.append(CodeSmell(
                        severity="low",
                        category="naming",
                        message=f"类名 '{node.name}' 不符合 PEP8 规范",
                        file_path=str(file_path.relative_to(self.project_dir)),
                        line_no=node.lineno,
                        suggestion="类名应使用驼峰命名法(CapWords)"
                    ))

        return smells

    def _check_magic_numbers(self, content: str, file_path: Path) -> List[CodeSmell]:
        """检查魔法数字"""
        smells = []
        lines = content.split('\n')

        for line_no, line in enumerate(lines, 1):
            # 跳过注释
            if line.strip().startswith('#'):
                continue

            # 查找数字（排除 0, 1, 2 等常见值）
            matches = re.finditer(r'\b([3-9]|[1-9]\d+)\b', line)
            for match in matches:
                # 排除一些合法场景
                if any(x in line.lower() for x in ['range', 'sleep', 'timeout', 'port', 'size', 'length']):
                    continue

                smells.append(CodeSmell(
                    severity="low",
                    category="naming",
                    message=f"发现魔法数字: {match.group(1)}",
                    file_path=str(file_path.relative_to(self.project_dir)),
                    line_no=line_no,
                    suggestion="考虑使用命名常量代替魔法数字"
                ))

        return smells[:20]  # 限制数量


class JavaScriptAnalyzer:
    """JavaScript/TypeScript 代码分析器"""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.smells: List[CodeSmell] = []

    def analyze_file(self, file_path: Path) -> List[CodeSmell]:
        """分析单个 JavaScript/TypeScript 文件"""
        smells = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            # 检查函数长度
            smells.extend(self._check_long_functions(content, file_path))

            # 检查嵌套深度
            smells.extend(self._check_nesting(content, file_path))

            # 检查 console.log
            smells.extend(self._check_console_logs(content, file_path))

            # 检查 var 使用
            smells.extend(self._check_var_usage(content, file_path))

        except Exception:
            pass

        return smells

    def _check_long_functions(self, content: str, file_path: Path) -> List[CodeSmell]:
        """检查过长的函数"""
        smells = []

        # 简单的函数检测
        func_pattern = r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)'

        matches = list(re.finditer(func_pattern, content))
        lines = content.split('\n')

        for i, match in enumerate(matches):
            func_name = match.group(1) or match.group(2)
            start_line = content[:match.start()].count('\n') + 1

            # 查找函数结束（简单启发式）
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            func_content = content[match.start():end_pos]
            func_lines = func_content.count('\n')

            if func_lines > 50:
                smells.append(CodeSmell(
                    severity="medium",
                    category="complexity",
                    message=f"函数 '{func_name}' 过长 ({func_lines} 行)",
                    file_path=str(file_path.relative_to(self.project_dir)),
                    line_no=start_line,
                    suggestion=f"考虑将函数 '{func_name}' 拆分为更小的函数"
                ))

        return smells

    def _check_nesting(self, content: str, file_path: Path) -> List[CodeSmell]:
        """检查嵌套深度"""
        smells = []
        lines = content.split('\n')

        for line_no, line in enumerate(lines, 1):
            # 计算缩进层级（2空格或4空格）
            stripped = line.lstrip()
            indent = len(line) - len(stripped)

            if indent > 0:
                spaces_per_level = 2 if line_no > 1 and len(lines[line_no - 2]) - len(lines[line_no - 2].lstrip()) < 4 else 4
                depth = indent // spaces_per_level

                if depth > 4:
                    smells.append(CodeSmell(
                        severity="medium",
                        category="complexity",
                        message=f"代码嵌套过深 ({depth} 层)",
                        file_path=str(file_path.relative_to(self.project_dir)),
                        line_no=line_no,
                        suggestion="考虑提取函数或使用早返回来减少嵌套"
                    ))

        return smells[:10]

    def _check_console_logs(self, content: str, file_path: Path) -> List[CodeSmell]:
        """检查遗留的 console.log"""
        smells = []
        lines = content.split('\n')

        for line_no, line in enumerate(lines, 1):
            if 'console.log' in line and not line.strip().startswith('//'):
                smells.append(CodeSmell(
                    severity="low",
                    category="dead_code",
                    message="发现遗留的 console.log",
                    file_path=str(file_path.relative_to(self.project_dir)),
                    line_no=line_no,
                    suggestion="移除或替换为适当的日志框架"
                ))

        return smells[:15]

    def _check_var_usage(self, content: str, file_path: Path) -> List[CodeSmell]:
        """检查 var 使用（建议使用 const/let）"""
        smells = []
        lines = content.split('\n')

        for line_no, line in enumerate(lines, 1):
            # 匹配 var 关键字（排除注释）
            if re.search(r'\bvar\s+\w+', line) and not line.strip().startswith('//'):
                smells.append(CodeSmell(
                    severity="low",
                    category="naming",
                    message="使用了 var 关键字",
                    file_path=str(file_path.relative_to(self.project_dir)),
                    line_no=line_no,
                    suggestion="考虑使用 const 或 let 代替 var"
                ))

        return smells[:20]


class CodeSmellDetector:
    """代码异味检测器主类"""

    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir).resolve()
        self.smells: List[CodeSmell] = []
        self.files_analyzed = 0

    def detect(self) -> bool:
        """执行代码异味检测"""
        print(f"🔍 扫描项目: {self.project_dir}")

        # 检测项目类型
        py_files = list(self.project_dir.rglob("*.py"))
        js_files = list(self.project_dir.rglob("*.js")) + list(self.project_dir.rglob("*.ts"))
        go_files = list(self.project_dir.rglob("*.go"))

        total_files = len(py_files) + len(js_files) + len(go_files)

        if total_files == 0:
            print("❌ 未找到支持的源代码文件")
            return False

        print(f"📁 发现 {total_files} 个源文件")

        # 分析 Python 文件
        if py_files:
            print(f"🐍 分析 {len(py_files)} 个 Python 文件...")
            py_analyzer = PythonAnalyzer(self.project_dir)
            for py_file in py_files:
                # 排除虚拟环境和测试文件
                if 'venv' not in str(py_file) and '.venv' not in str(py_file):
                    self.smells.extend(py_analyzer.analyze_file(py_file))
                    self.files_analyzed += 1

        # 分析 JavaScript/TypeScript 文件
        if js_files:
            print(f"📜 分析 {len(js_files)} 个 JavaScript/TypeScript 文件...")
            js_analyzer = JavaScriptAnalyzer(self.project_dir)
            for js_file in js_files:
                # 排除 node_modules
                if 'node_modules' not in str(js_file):
                    self.smells.extend(js_analyzer.analyze_file(js_file))
                    self.files_analyzed += 1

        print(f"✅ 分析完成: 发现 {len(self.smells)} 个代码异味")
        return True

    def calculate_quality_score(self) -> int:
        """计算代码质量评分"""
        if not self.smells:
            return 100

        score = 100
        for smell in self.smells:
            if smell.severity == "critical":
                score -= 10
            elif smell.severity == "high":
                score -= 5
            elif smell.severity == "medium":
                score -= 2
            elif smell.severity == "low":
                score -= 1

        return max(0, score)

    def generate_report(self) -> str:
        """生成检测报告"""
        report = []
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 计算评分
        score = self.calculate_quality_score()
        if score >= 90:
            rating = "🟢 优秀"
        elif score >= 75:
            rating = "🟡 良好"
        elif score >= 60:
            rating = "🟠 一般"
        else:
            rating = "🔴 较差"

        # 统计严重程度
        severity_counts = defaultdict(int)
        category_counts = defaultdict(int)

        for smell in self.smells:
            severity_counts[smell.severity] += 1
            category_counts[smell.category] += 1

        # 报告头部
        report.append("=" * 140)
        report.append("🔍 代码异味检测报告")
        report.append(f"分析时间: {now}")
        report.append(f"项目路径: {self.project_dir}")
        report.append("=" * 140)
        report.append("")

        # 质量评分
        report.append("📊 代码质量评分")
        report.append("-" * 140)
        report.append(f"  总评分: {score}/100 {rating}")
        report.append(f"  分析文件: {self.files_analyzed} 个")
        report.append(f"  发现问题: {len(self.smells)} 个")
        report.append("")

        # 问题统计
        report.append("=" * 140)
        report.append("📈 问题统计")
        report.append("=" * 140)
        report.append("")

        report.append("按严重程度:")
        for sev in ["critical", "high", "medium", "low"]:
            icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[sev]
            count = severity_counts.get(sev, 0)
            label = {"critical": "严重", "high": "高", "medium": "中等", "low": "轻微"}[sev]
            report.append(f"  {icon} {label}问题: {count} 个")

        report.append("")
        report.append("按类别:")

        category_labels = {
            "complexity": "复杂度",
            "duplication": "重复代码",
            "naming": "命名规范",
            "design": "设计问题",
            "dead_code": "死代码"
        }

        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            label = category_labels.get(cat, cat)
            report.append(f"  - {label}: {count} 个")

        # 问题排行
        if self.smells:
            report.append("")
            report.append("=" * 140)
            report.append("🔍 问题详情（按严重程度排序）")
            report.append("=" * 140)
            report.append("")

            # 按严重程度排序
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            sorted_smells = sorted(self.smells, key=lambda s: severity_order[s.severity])

            for smell in sorted_smells[:100]:  # 限制显示数量
                icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[smell.severity]
                report.append(f"{icon} [{smell.severity.upper()}] {smell.file_path}:{smell.line_no}")
                report.append(f"   {smell.message}")
                if smell.suggestion:
                    report.append(f"   💡 {smell.suggestion}")
                report.append("")

            if len(self.smells) > 100:
                report.append(f"... 还有 {len(self.smells) - 100} 个问题未显示")

        # 改进建议
        report.append("")
        report.append("=" * 140)
        report.append("💡 改进建议")
        report.append("=" * 140)
        report.append("")

        recommendations = self._generate_recommendations(score, severity_counts)
        for i, rec in enumerate(recommendations, 1):
            report.append(f"{i}. {rec}")

        return '\n'.join(report)

    def _generate_recommendations(self, score: int, severity_counts: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []

        if score < 60:
            recommendations.append(
                "🔴 **紧急**: 代码质量较差，建议立即处理严重和高优先级问题，重点关注函数复杂度和代码重复"
            )
        elif score < 75:
            recommendations.append(
                "🟠 **重要**: 代码质量有提升空间，建议优先处理中高优先级的问题"
            )
        elif score < 90:
            recommendations.append(
                "🟡 **改进**: 代码质量良好，建议持续改进剩余的代码异味"
            )
        else:
            recommendations.append(
                "🟢 **优秀**: 代码质量很高，继续保持良好的编码习惯"
            )

        if severity_counts.get("critical", 0) > 0:
            recommendations.append(
                f"🚨 立即修复 {severity_counts['critical']} 个严重问题，这些可能导致 bug 或安全风险"
            )

        if severity_counts.get("high", 0) > 0:
            recommendations.append(
                f"⚠️ 尽快处理 {severity_counts['high']} 个高优先级问题，改善代码可维护性"
            )

        if severity_counts.get("complexity", 0) > 5:
            recommendations.append(
                "📉 复杂度问题较多，建议使用重构技巧拆分复杂函数，提高代码可读性"
            )

        recommendations.append("🧪 在 CI/CD 流程中集成代码质量检查，防止引入新的代码异味")
        recommendations.append("📖 定期进行代码审查，团队共同识别和解决代码质量问题")
        recommendations.append("🔄 考虑使用自动化重构工具辅助代码改进")

        return recommendations


def save_report(report: str, output_file: str):
    """保存报告到文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='代码异味检测器')
    parser.add_argument('--project-dir', '-p', default='.', help='项目目录路径')
    parser.add_argument('--output', '-o', default='code_smell_report.txt', help='输出报告文件名')

    args = parser.parse_args()

    print("🔍 代码异味检测器")
    print("=" * 60)
    print(f"项目目录: {args.project_dir}")
    print()

    detector = CodeSmellDetector(args.project_dir)

    if not detector.detect():
        print("❌ 检测失败")
        return 1

    print()
    print("📝 正在生成检测报告...")
    report = detector.generate_report()
    save_report(report, args.output)

    print(f"✅ 报告已保存到: {args.output}")
    print()

    # 显示摘要
    score = detector.calculate_quality_score()
    severity_counts = defaultdict(int)
    for smell in detector.smells:
        severity_counts[smell.severity] += 1

    print("=" * 60)
    print("📋 检测摘要")
    print("=" * 60)
    print(f"  质量评分: {score}/100")
    print(f"  分析文件: {detector.files_analyzed} 个")
    print(f"  发现问题: {len(detector.smells)} 个")
    print(f"  - 严重: {severity_counts.get('critical', 0)} 个")
    print(f"  - 高: {severity_counts.get('high', 0)} 个")
    print(f"  - 中: {severity_counts.get('medium', 0)} 个")
    print(f"  - 低: {severity_counts.get('low', 0)} 个")
    print()

    return 0


if __name__ == '__main__':
    exit(main())
