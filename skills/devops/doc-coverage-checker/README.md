# Documentation Coverage Checker Skill

## 概述

这个 Skill 用于检查代码的文档覆盖率，识别缺失文档的函数、类和模块，并提供文档质量评分和改进建议。

## 功能特点

- **多语言支持**: 支持 Python、JavaScript/TypeScript 等多种编程语言
- **智能识别**: 自动识别公共 API（非下划线开头的函数/类）
- **质量评估**: 不仅检查文档是否存在，还评估文档质量
- **详细报告**: 生成易于阅读的文本报告和机器可读的 JSON 报告
- **改进建议**: 根据分析结果提供具体的改进建议

## 文件结构

```
doc-coverage-checker/
├── SKILL.md          # Skill 定义文件
├── impl.py           # 实现脚本
├── test_skill.py     # 测试脚本
└── README.md         # 使用文档
```

## 如何使用

### 方式 1: 直接运行脚本

```bash
# 分析当前目录
python3 skillsets/doc-coverage-checker/impl.py

# 分析指定项目
python3 skillsets/doc-coverage-checker/impl.py /path/to/project
```

### 方式 2: 运行测试脚本

```bash
python3 skillsets/doc-coverage-checker/test_skill.py
```

### 方式 3: 通过 Skill 触发

在对话中使用以下短语：
- "检查文档完整性"
- "哪些函数缺少注释"
- "文档覆盖率"
- "分析文档质量"
- "验证 API 文档"

## 输出文件

执行后会生成以下文件：

1. **doc_coverage_report.txt** - 详细的可读报告
2. **doc_coverage_report.json** - 机器可读的 JSON 数据

## 报告内容

### 总体统计
- 分析文件总数
- 代码元素总数
- 已/未文档化元素数量
- 总体覆盖率百分比
- 文档质量评分

### 各文件详细情况
- 每个文件的文档覆盖率
- 按覆盖率排序显示
- 覆盖率等级标识（✅ 80%+、🟡 50-80%、🔴 <50%）

### 缺失文档列表
- 按文件分组显示
- 标注元素类型（类、函数、方法）
- 显示所在行号

### 改进建议
- 根据当前覆盖率提供针对性建议
- 包含 Python 和 JavaScript 的文档字符串模板

## 文档质量标准

### 评分标准

| 质量等级 | 评分 | 说明 |
|---------|------|------|
| 完整 (complete) | 90-100% | 包含描述、参数、返回值、异常 |
| 良好 (good) | 70-89% | 有详细描述和关键信息 |
| 基础 (basic) | 50-69% | 有基本描述 |
| 较差 (poor) | 20-49% | 文档过短或只是占位符 |
| 缺失 (missing) | 0-19% | 无文档 |

### Python 文档字符串格式

```python
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
```

### JavaScript JSDoc 格式

```javascript
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
```

## 分析范围

### 包含的文件类型
- Python: `.py`
- JavaScript: `.js`, `.jsx`
- TypeScript: `.ts`, `.tsx`

### 排除的目录
- `node_modules`, `venv`, `.venv`, `env`
- `__pycache__`, `.git`, `dist`, `build`
- `tests`, `test`, `.tox`, `.pytest_cache`
- `vendor`, `third_party`, `.next`, `.nuxt`

### 公共 API 识别
- Python: 非下划线开头的类和函数
- JavaScript/TypeScript: 非下划线开头的函数和导出的函数

## 测试状态

✅ 所有测试通过

## 依赖

- Python 3.6+
- 无需额外依赖（仅使用标准库）

## 常见问题

### Q: 为什么有些文件没有被分析？
A: 工具会自动排除测试目录、虚拟环境、node_modules 等非源代码目录。

### Q: 如何只分析 Python 文件？
A: 当前版本会分析所有支持的文件类型。可以通过修改 `_find_source_files` 方法来自定义。

### Q: 覆盖率计算是否包含私有方法？
A: 公共 API 的覆盖率是主要指标，但报告中也会显示所有元素的统计信息。

### Q: 如何自定义质量评分标准？
A: 可以修改 `_assess_doc_quality` 方法中的评分逻辑。

## 下一步

1. 查看 `doc_coverage_report.txt` 获取详细分析
2. 根据报告中的建议补充缺失的文档
3. 使用报告中的模板规范化文档格式
4. 定期重新运行此分析以跟踪文档质量改进

## 贡献

欢迎提交问题报告和改进建议！
