# Code Smell Detector

自动检测代码异味和代码质量问题的工具，支持 Python、JavaScript/TypeScript 等多种编程语言。

## 功能特性

- 🔍 **多语言支持**: Python、JavaScript、TypeScript
- 📊 **质量评分**: 0-100 分的代码质量评分
- 🎯 **智能分类**: 按严重程度和类别分类问题
- 💡 **改进建议**: 提供具体的重构建议
- 📈 **详细报告**: 生成全面的代码质量报告

## 检测的代码异味类型

| 类别 | 检测项 | 说明 |
|------|--------|------|
| **复杂度** | 高圈复杂度 | 函数分支过多 |
| | 过长函数 | 超过 50 行的函数 |
| | 深层嵌套 | 超过 4 层的嵌套 |
| **设计** | 参数过多 | 超过 5 个参数 |
| **命名** | 命名规范 | 不符合语言规范 |
| | 魔法数字 | 未命名的常量 |
| **死代码** | 遗留调试 | console.log 等 |
| | var 使用 | 建议用 const/let |

## 安装

无需额外依赖，使用 Python 3.7+ 即可运行：

```bash
git clone https://github.com/your-repo/bingo-devops-skills.git
cd bingo-devops-skills/skillsets/code-smell-detector
```

## 使用方法

### 基本用法

在项目根目录运行：

```bash
python3 skillsets/code-smell-detector/impl.py
```

### 指定项目目录

```bash
python3 skillsets/code-smell-detector/impl.py --project-dir /path/to/project
```

### 指定输出文件

```bash
python3 skillsets/code-smell-detector/impl.py --output my_report.txt
```

### 完整参数

```bash
python3 skillsets/code-smell-detector/impl.py \
  --project-dir ./my-project \
  --output code_smell_report.txt
```

## 输出示例

```
════════════════════════════════════════════════════════════════
🔍 代码异味检测报告
分析时间: 2025-01-30 18:00:00
项目路径: /path/to/project
════════════════════════════════════════════════════════════════

📊 代码质量评分
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  总评分: 72/100 🟠 一般
  分析文件: 25 个
  发现问题: 45 个

📈 问题统计
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

按严重程度:
  🔴 严重问题: 3 个
  🟠 高优先级: 8 个
  🟡 中等问题: 15 个
  🟢 轻微问题: 19 个

按类别:
  - 复杂度: 18 个
  - 命名规范: 12 个
  - 设计问题: 8 个
  - 死代码: 7 个

🔍 问题详情（按严重程度排序）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 [HIGH] src/utils.py:45
   函数 'process_data' 圈复杂度过高 (18)
   💡 考虑将函数 'process_data' 拆分为更小的函数

...
```

## 评分标准

| 分数范围 | 等级 | 说明 |
|---------|------|------|
| 90-100 | 🟢 优秀 | 代码质量很高 |
| 75-89 | 🟡 良好 | 代码质量良好 |
| 60-74 | 🟠 一般 | 需要改进 |
| 0-59 | 🔴 较差 | 急需重构 |

## 测试

运行测试脚本验证功能：

```bash
python3 skillsets/code-smell-detector/test_skill.py
```

## CI/CD 集成

### GitHub Actions 示例

```yaml
name: Code Quality Check

on: [push, pull_request]

jobs:
  code-smell:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Code Smell Detector
        run: |
          python3 skillsets/code-smell-detector/impl.py
      - name: Upload Report
        uses: actions/upload-artifact@v2
        with:
          name: code-smell-report
          path: code_smell_report.txt
```

## 支持的语言

### Python
- ✅ 圈复杂度分析
- ✅ 函数长度检测
- ✅ 嵌套深度检测
- ✅ 参数数量检测
- ✅ PEP8 命名规范检查
- ✅ 魔法数字检测

### JavaScript / TypeScript
- ✅ 函数长度检测
- ✅ 嵌套深度检测
- ✅ 遗留 console.log 检测
- ✅ var 使用检测

### 扩展支持

可以通过添加新的 Analyzer 类来支持更多语言。

## 常见问题

### Q: 为什么没有检测到所有问题？

A: 工具使用启发式规则和静态分析，可能无法检测所有类型的代码异味。建议结合其他工具（如 pylint、eslint）一起使用。

### Q: 如何过滤误报？

A: 查看报告后，可以根据实际情况判断是否需要修复。工具只是辅助，最终决策需要开发者判断。

### Q: 可以自定义检测规则吗？

A: 目前规则是硬编码的，未来版本可能支持配置文件自定义。

## 贡献

欢迎提交问题和改进建议！

## 许可证

MIT License
