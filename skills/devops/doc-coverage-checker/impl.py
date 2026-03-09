#!/usr/bin/env python3
"""
文档覆盖率检查工具
检查代码中的函数、类、模块的文档完整性
支持 Python、JavaScript/TypeScript 等多种语言
"""

import ast
import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any


class DocCoverageAnalyzer:
    """文档覆盖率分析器"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.results = {
            'summary': {},
            'files': [],
            'undocumented': [],
            'quality_score': 0
        }

    def analyze(self) -> Dict[str, Any]:
        """执行完整的文档覆盖率分析"""
        print("🔍 开始分析文档覆盖率...")

        # 查找所有需要分析的文件
        files = self._find_source_files()
        print(f"📁 找到 {len(files)} 个源文件")

        # 分析每个文件
        for file_path in files:
            file_result = self._analyze_file(file_path)
            if file_result:
                self.results['files'].append(file_result)

        # 计算总体统计
        self._calculate_summary()

        # 计算质量评分
        self._calculate_quality_score()

        return self.results

    def _find_source_files(self) -> List[Path]:
        """查找所有源代码文件"""
        file_patterns = [
            '**/*.py',
            '**/*.js',
            '**/*.ts',
            '**/*.jsx',
            '**/*.tsx',
        ]

        exclude_dirs = {
            'node_modules', 'venv', '.venv', 'env',
            '__pycache__', '.git', 'dist', 'build',
            'tests', 'test', '.tox', '.pytest_cache',
            'vendor', 'third_party', '.next', '.nuxt'
        }

        files = []
        for pattern in file_patterns:
            for file_path in self.project_path.rglob(pattern):
                # 检查是否在排除目录中
                if any(exclude_dir in file_path.parts for exclude_dir in exclude_dirs):
                    continue
                files.append(file_path)

        return files

    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """分析单个文件的文档覆盖率"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if file_path.suffix == '.py':
                return self._analyze_python_file(file_path, content)
            elif file_path.suffix in ['.js', '.ts', '.jsx', '.tsx']:
                return self._analyze_javascript_file(file_path, content)
            else:
                return None

        except Exception as e:
            print(f"⚠️  分析文件 {file_path} 时出错: {e}")
            return None

    def _analyze_python_file(self, file_path: Path, content: str) -> Dict[str, Any]:
        """分析 Python 文件的文档覆盖率"""
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError:
            return None

        file_result = {
            'path': str(file_path.relative_to(self.project_path)),
            'type': 'python',
            'module_doc': self._get_module_docstring(tree),
            'classes': [],
            'functions': [],
            'total_elements': 0,
            'documented_elements': 0,
            'coverage': 0.0
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = self._analyze_class(node)
                file_result['classes'].append(class_info)
                file_result['total_elements'] += 1
                if class_info['has_doc']:
                    file_result['documented_elements'] += 1

            elif isinstance(node, ast.FunctionDef):
                # 只分析模块级别的函数（不在类中的函数）
                is_method = False
                for parent in ast.walk(tree):
                    if isinstance(parent, ast.ClassDef) and hasattr(parent, 'body'):
                        # 安全地检查 node 是否在 parent.body 中
                        try:
                            if node in parent.body:
                                is_method = True
                                break
                        except (TypeError, AttributeError):
                            # parent.body 可能不是可迭代的，跳过
                            continue

                if not is_method:
                    func_info = self._analyze_function(node)
                    file_result['functions'].append(func_info)
                    file_result['total_elements'] += 1
                    if func_info['has_doc']:
                        file_result['documented_elements'] += 1

        # 计算覆盖率
        if file_result['total_elements'] > 0:
            file_result['coverage'] = (
                file_result['documented_elements'] / file_result['total_elements'] * 100
            )

        # 记录未文档化的元素
        self._record_undocumented(file_result)

        return file_result

    def _analyze_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """分析类的文档"""
        class_info = {
            'name': node.name,
            'line': node.lineno,
            'is_public': not node.name.startswith('_'),
            'has_doc': ast.get_docstring(node) is not None,
            'docstring': ast.get_docstring(node),
            'methods': []
        }

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._analyze_function(item, is_method=True)
                class_info['methods'].append(method_info)

        return class_info

    def _analyze_function(self, node: ast.FunctionDef, is_method: bool = False) -> Dict[str, Any]:
        """分析函数的文档"""
        docstring = ast.get_docstring(node)

        func_info = {
            'name': node.name,
            'line': node.lineno,
            'is_public': not node.name.startswith('_'),
            'is_method': is_method,
            'has_doc': docstring is not None,
            'docstring': docstring,
            'doc_quality': self._assess_doc_quality(docstring) if docstring else 'missing'
        }

        return func_info

    def _get_module_docstring(self, tree: ast.AST) -> Dict[str, Any]:
        """获取模块文档字符串"""
        docstring = ast.get_docstring(tree)
        return {
            'has_doc': docstring is not None,
            'docstring': docstring,
            'quality': self._assess_doc_quality(docstring) if docstring else 'missing'
        }

    def _assess_doc_quality(self, docstring: str) -> str:
        """评估文档质量"""
        if not docstring:
            return 'missing'

        # 移除空白字符
        clean_doc = re.sub(r'\s+', ' ', docstring.strip())

        # 检查是否为空或只是占位符
        if len(clean_doc) < 10:
            return 'poor'
        if clean_doc.lower() in ['todo', 'fix me', 'tbd', 'placeholder']:
            return 'poor'

        # 检查文档完整性
        has_description = len(clean_doc) > 20
        has_args = 'arg' in clean_doc.lower() or 'param' in clean_doc.lower()
        has_return = 'return' in clean_doc.lower() or 'returns' in clean_doc.lower()
        has_raises = 'raise' in clean_doc.lower() or 'exception' in clean_doc.lower()

        if has_description and has_args and has_return:
            return 'complete'
        elif has_description:
            return 'good'
        else:
            return 'basic'

    def _analyze_javascript_file(self, file_path: Path, content: str) -> Dict[str, Any]:
        """分析 JavaScript/TypeScript 文件的文档覆盖率"""
        file_result = {
            'path': str(file_path.relative_to(self.project_path)),
            'type': 'javascript',
            'functions': [],
            'total_elements': 0,
            'documented_elements': 0,
            'coverage': 0.0
        }

        # 查找所有函数定义
        # 匹配 function name() 和 const name = () => 等形式
        function_patterns = [
            r'function\s+(\w+)\s*\(',
            r'const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>',
            r'(\w+)\s*:\s*(?:async\s*)?function',
            r'(\w+)\s*\([^)]*\)\s*{',  # 方法定义
            r'export\s+(?:const|function)\s+(\w+)',
        ]

        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # 跳过注释行
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('*'):
                continue

            for pattern in function_patterns:
                match = re.search(pattern, line)
                if match:
                    func_name = match.group(1)
                    is_public = not func_name.startswith('_')

                    # 检查前一行是否有 JSDoc 注释
                    has_jsdoc = False
                    if line_num > 1:
                        prev_line = lines[line_num - 2].strip()
                        has_jsdoc = prev_line.startswith('*') or prev_line.startswith('/**')

                    func_info = {
                        'name': func_name,
                        'line': line_num,
                        'is_public': is_public,
                        'has_doc': has_jsdoc,
                        'doc_quality': 'good' if has_jsdoc else 'missing'
                    }

                    file_result['functions'].append(func_info)
                    file_result['total_elements'] += 1
                    if has_jsdoc:
                        file_result['documented_elements'] += 1
                    break

        # 计算覆盖率
        if file_result['total_elements'] > 0:
            file_result['coverage'] = (
                file_result['documented_elements'] / file_result['total_elements'] * 100
            )

        # 记录未文档化的元素
        self._record_undocumented(file_result)

        return file_result

    def _record_undocumented(self, file_result: Dict[str, Any]):
        """记录未文档化的公共 API"""
        file_path = file_result['path']

        # 检查模块文档
        if file_result.get('type') == 'python':
            if not file_result.get('module_doc', {}).get('has_doc', False):
                self.results['undocumented'].append({
                    'type': 'module',
                    'path': file_path,
                    'name': file_path
                })

        # 检查类文档
        for cls in file_result.get('classes', []):
            if cls['is_public'] and not cls['has_doc']:
                self.results['undocumented'].append({
                    'type': 'class',
                    'path': file_path,
                    'name': cls['name'],
                    'line': cls['line']
                })

        # 检查函数/方法文档
        for func in file_result.get('functions', []):
            if func['is_public'] and not func['has_doc']:
                self.results['undocumented'].append({
                    'type': 'function',
                    'path': file_path,
                    'name': func['name'],
                    'line': func['line']
                })

    def _calculate_summary(self):
        """计算总体统计"""
        total_files = len(self.results['files'])
        total_elements = sum(f.get('total_elements', 0) for f in self.results['files'])
        total_documented = sum(f.get('documented_elements', 0) for f in self.results['files'])

        overall_coverage = (total_documented / total_elements * 100) if total_elements > 0 else 0

        # 按类型统计
        python_files = [f for f in self.results['files'] if f.get('type') == 'python']
        js_files = [f for f in self.results['files'] if f.get('type') == 'javascript']

        self.results['summary'] = {
            'total_files': total_files,
            'python_files': len(python_files),
            'javascript_files': len(js_files),
            'total_elements': total_elements,
            'documented_elements': total_documented,
            'undocumented_elements': total_elements - total_documented,
            'overall_coverage': overall_coverage,
            'public_api_missing': len([u for u in self.results['undocumented'] if u.get('is_public', True)])
        }

    def _calculate_quality_score(self):
        """计算文档质量评分"""
        if not self.results['files']:
            self.results['quality_score'] = 0
            return

        # 统计文档质量分布
        quality_counts = {'complete': 0, 'good': 0, 'basic': 0, 'poor': 0, 'missing': 0}

        for file_result in self.results['files']:
            for cls in file_result.get('classes', []):
                if cls.get('doc_quality'):
                    quality_counts[cls['doc_quality']] = quality_counts.get(cls['doc_quality'], 0) + 1

                for method in cls.get('methods', []):
                    if method.get('doc_quality'):
                        quality_counts[method['doc_quality']] = quality_counts.get(method['doc_quality'], 0) + 1

            for func in file_result.get('functions', []):
                if func.get('doc_quality'):
                    quality_counts[func['doc_quality']] = quality_counts.get(func['doc_quality'], 0) + 1

        # 计算加权评分
        total = sum(quality_counts.values())
        if total == 0:
            self.results['quality_score'] = 0
            return

        score = (
            quality_counts.get('complete', 0) * 100 +
            quality_counts.get('good', 0) * 80 +
            quality_counts.get('basic', 0) * 50 +
            quality_counts.get('poor', 0) * 20
        ) / total

        self.results['quality_score'] = round(score, 2)
        self.results['quality_distribution'] = quality_counts


def generate_report(analyzer: DocCoverageAnalyzer, output_file: str = 'doc_coverage_report.txt'):
    """生成文档覆盖率报告"""
    results = analyzer.results
    summary = results['summary']

    report = []
    report.append("=" * 140)
    report.append("📚 文档覆盖率分析报告")
    report.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 140)
    report.append("")

    # 总体统计
    report.append("📊 总体统计")
    report.append("-" * 140)
    report.append(f"  分析文件总数: {summary['total_files']}")
    report.append(f"    - Python 文件: {summary['python_files']}")
    report.append(f"    - JavaScript/TypeScript 文件: {summary['javascript_files']}")
    report.append(f"  代码元素总数: {summary['total_elements']}")
    report.append(f"    - 已文档化: {summary['documented_elements']}")
    report.append(f"    - 未文档化: {summary['undocumented_elements']}")
    report.append(f"  总体覆盖率: {summary['overall_coverage']:.2f}%")
    report.append(f"  文档质量评分: {results['quality_score']:.1f}/100")
    report.append("")

    # 质量评分说明
    quality_score = results['quality_score']
    if quality_score >= 80:
        quality_level = "优秀 ✅"
    elif quality_score >= 60:
        quality_level = "良好 🟡"
    elif quality_score >= 40:
        quality_level = "一般 🟠"
    else:
        quality_level = "需要改进 🔴"

    report.append(f"  文档质量等级: {quality_level}")
    report.append("")

    # 质量分布
    if 'quality_distribution' in results:
        report.append("📈 文档质量分布")
        report.append("-" * 140)
        dist = results['quality_distribution']
        report.append(f"  完整文档 (complete): {dist.get('complete', 0)}")
        report.append(f"  良好文档 (good): {dist.get('good', 0)}")
        report.append(f"  基础文档 (basic): {dist.get('basic', 0)}")
        report.append(f"  较差文档 (poor): {dist.get('poor', 0)}")
        report.append(f"  缺失文档 (missing): {dist.get('missing', 0)}")
        report.append("")

    # 各文件详细情况
    report.append("📁 各文件文档覆盖率")
    report.append("-" * 140)
    report.append(f"{'文件路径':<50} {'总元素':<8} {'已文档化':<10} {'覆盖率':<10} {'类型'}")
    report.append("-" * 140)

    # 按覆盖率排序
    sorted_files = sorted(results['files'], key=lambda x: x.get('coverage', 0))
    for file_result in sorted_files:
        path = file_result['path'][:48]
        total = file_result.get('total_elements', 0)
        documented = file_result.get('documented_elements', 0)
        coverage = file_result.get('coverage', 0)
        file_type = file_result.get('type', 'unknown')

        # 根据覆盖率添加标记
        if coverage >= 80:
            emoji = "✅"
        elif coverage >= 50:
            emoji = "🟡"
        else:
            emoji = "🔴"

        report.append(f"{path:<50} {total:<8} {documented:<10} {coverage:>6.2f}% {emoji}  {file_type}")

    report.append("")

    # 未文档化的公共 API
    if results['undocumented']:
        report.append("⚠️  缺失文档的公共 API")
        report.append("-" * 140)
        report.append(f"共有 {len(results['undocumented'])} 个公共 API 缺少文档")
        report.append("")

        # 按文件分组显示
        undocumented_by_file = {}
        for item in results['undocumented']:
            file_path = item['path']
            if file_path not in undocumented_by_file:
                undocumented_by_file[file_path] = []
            undocumented_by_file[file_path].append(item)

        # 显示前 10 个文件
        for file_path, items in list(undocumented_by_file.items())[:10]:
            report.append(f"  📄 {file_path}")
            for item in items[:5]:  # 每个文件显示前 5 个
                item_type = item['type']
                name = item['name']
                line = item.get('line', '?')
                report.append(f"    - {item_type}: {name} (行 {line})")

            if len(items) > 5:
                report.append(f"    ... 还有 {len(items) - 5} 个")
            report.append("")

        if len(undocumented_by_file) > 10:
            report.append(f"  ... 还有 {len(undocumented_by_file) - 10} 个文件包含未文档化的 API")
            report.append("")
    else:
        report.append("✅ 所有公共 API 都有文档！")
        report.append("")

    # 改进建议
    report.append("💡 改进建议")
    report.append("-" * 140)

    if summary['overall_coverage'] < 50:
        report.append("  1. 优先为公共 API 添加文档")
        report.append("  2. 至少添加函数/类的基本描述")
        report.append("  3. 使用文档字符串模板规范格式")
    elif summary['overall_coverage'] < 80:
        report.append("  1. 完善现有文档，添加参数和返回值说明")
        report.append("  2. 为复杂函数添加使用示例")
        report.append("  3. 补充异常和错误情况的说明")
    else:
        report.append("  1. 继续保持文档质量")
        report.append("  2. 定期审查和更新文档")
        report.append("  3. 考虑添加更多使用示例")

    report.append("")
    report.append("=" * 140)
    report.append("📋 Python 文档字符串建议格式")
    report.append("=" * 140)
    report.append("""
def function_name(param1, param2):
    '''
    函数的简短描述（一句话）

    详细描述函数的功能、用途和行为。

    Args:
        param1 (type): 参数1的描述
        param2 (type): 参数2的描述

    Returns:
        type: 返回值的描述

    Raises:
        ExceptionType: 异常情况的描述

    Examples:
        >>> function_name('value1', 'value2')
        'result'
    '''
    pass
    """)

    report.append("=" * 140)
    report.append("📋 JavaScript JSDoc 建议格式")
    report.append("=" * 140)
    report.append("""
/**
 * 函数的简短描述
 *
 * 详细描述函数的功能、用途和行为。
 *
 * @param {type} param1 - 参数1的描述
 * @param {type} param2 - 参数2的描述
 * @returns {type} 返回值的描述
 * @throws {Error} 异常情况的描述
 *
 * @example
 * // 使用示例
 * functionName('value1', 'value2');
 */
function functionName(param1, param2) {
    // 实现
}
    """)

    report_content = '\n'.join(report)

    # 保存报告
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    # 同时生成 JSON 报告
    json_file = output_file.replace('.txt', '.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return report_content


def main():
    """主函数"""
    import sys

    # 获取项目路径
    project_path = sys.argv[1] if len(sys.argv) > 1 else "."

    print("📚 文档覆盖率检查工具")
    print("=" * 60)
    print(f"🔍 分析路径: {os.path.abspath(project_path)}")
    print()

    try:
        # 创建分析器并执行分析
        analyzer = DocCoverageAnalyzer(project_path)
        results = analyzer.analyze()

        # 生成报告
        print("📊 正在生成报告...")
        report = generate_report(analyzer)

        # 输出摘要
        summary = results['summary']
        print()
        print("=" * 60)
        print("✅ 分析完成！")
        print("=" * 60)
        print(f"📁 分析文件: {summary['total_files']}")
        print(f"📝 代码元素: {summary['total_elements']}")
        print(f"✅ 已文档化: {summary['documented_elements']}")
        print(f"❌ 未文档化: {summary['undocumented_elements']}")
        print(f"📊 覆盖率: {summary['overall_coverage']:.2f}%")
        print(f"⭐ 质量评分: {results['quality_score']:.1f}/100")
        print()
        print(f"📄 详细报告已保存到:")
        print(f"   - doc_coverage_report.txt")
        print(f"   - doc_coverage_report.json")
        print()

        # 根据覆盖率给出评估
        if summary['overall_coverage'] >= 80:
            print("🎉 文档覆盖率优秀！继续保持！")
        elif summary['overall_coverage'] >= 50:
            print("🟡 文档覆盖率良好，还有提升空间。")
        else:
            print("⚠️  文档覆盖率较低，建议优先为公共 API 添加文档。")

    except Exception as e:
        print(f"❌ 分析过程中出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
