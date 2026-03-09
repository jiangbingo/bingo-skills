---
name: "code-smell-detector"
description: "Use when detecting code smells, checking code quality, identifying duplicate code, or analyzing code complexity"
---

# Code Smell Detector

## Overview
Detects code smells and quality issues across multiple programming languages, providing actionable recommendations for code improvement and refactoring.

## When to Invoke

Invoke this skill when:
- User asks to check code quality
- User requests code smell detection
- User wants to identify duplicate code
- User asks about code complexity
- User needs refactoring recommendations
- User wants to find potential bugs or issues

## What It Does

1. **Detects Code Smells**: Identifies common anti-patterns and code issues
2. **Analyzes Complexity**: Measures cyclomatic complexity and cognitive load
3. **Finds Duplicate Code**: Detects repeated code patterns
4. **Checks Naming Conventions**: Validates naming standards
5. **Identifies Long Functions**: Flags functions that are too long
6. **Finds Dead Code**: Detects unused or unreachable code
7. **Generates Quality Score**: Provides overall code health rating

## Supported Languages

| Language | Tools | Detection Methods |
|----------|-------|-------------------|
| Python | pylint, flake8 | AST analysis, heuristic rules |
| JavaScript/TypeScript | eslint | AST analysis, pattern matching |
| Go | go vet, golangci-lint | Static analysis |
| General | Heuristic rules | Function length, nesting, parameters |

## Code Smell Categories

### Complexity Issues
- **High Cyclomatic Complexity**: Functions with too many branches
- **Deep Nesting**: Excessive indentation levels
- **Long Parameter Lists**: Functions with too many parameters
- **Long Functions**: Functions exceeding length thresholds

### Duplication Issues
- **Copy-Paste Code**: Identical or similar code blocks
- **Repeated Patterns**: Similar logic structures

### Naming Issues
- **Poor Names**: Non-descriptive variable/function names
- **Inconsistent Conventions**: Mixed naming styles
- **Magic Numbers**: Unnamed numeric literals

### Design Issues
- **God Classes**: Classes doing too much
- **Feature Envy**: Methods that belong elsewhere
- **Data Clumps**: Variables that should be grouped

### Dead Code
- **Unused Imports**: Import statements never used
- **Unreachable Code**: Code that can never execute
- **Commented Code**: Old code left in comments

## Usage Examples

### Detect Code Smells
```
User: "Detect code smells"
User: "检查代码异味"
User: "Find code quality issues"
```

### Check Code Quality
```
User: "Check code quality"
User: "代码质量检查"
User: "Analyze code health"
```

### Find Complex Code
```
User: "Find complex functions"
User: "找出复杂函数"
User: "Show high complexity areas"
```

### Get Refactoring Suggestions
```
User: "Refactoring recommendations"
User: "重构建议"
User: "How to improve this code"
```

## Output Format

Generates a `code_smell_report.txt` file with:

1. **Overall Quality Score**: 0-100 rating with severity level
2. **Summary Statistics**: Total issues by category
3. **Detailed Findings**: Each code smell with location and severity
4. **Prioritized Recommendations**: Action items sorted by impact
5. **Complexity Hotspots**: Files/functions needing attention

## Severity Levels

- **🔴 Critical**: Must fix - security risks, bugs
- **🟠 High**: Should fix - design issues, complexity
- **🟡 Medium**: Consider fixing - style, maintainability
- **🟢 Low**: Nice to fix - minor improvements

## Implementation Notes

- Uses `subprocess` to invoke static analysis tools
- Falls back to heuristic analysis when tools unavailable
- Supports multi-language projects with auto-detection
- Generates Chinese-friendly output with clear formatting
- Handles errors gracefully with helpful messages

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Ignoring all warnings | May miss real issues | Review each finding individually |
| Fixing style over substance | Low impact changes | Prioritize complexity and design issues |
- Tool not installed | Cannot run analysis | Install suggested tool or use heuristic mode |
| False positives | Tools may flag valid code | Use judgment when reviewing findings |

## Quality Score Calculation

```
Score = 100 - (critical × 10) - (high × 5) - (medium × 2) - (low × 1)

Rating:
  90-100: 🟢 Excellent
  75-89:  🟡 Good
  60-74:  🟠 Fair
  < 60:   🔴 Poor
```

## Example Report Structure

```
════════════════════════════════════════════════════════════════
代码异味检测报告
分析时间: 2025-01-30 18:00:00
项目类型: Python
════════════════════════════════════════════════════════════════

📊 代码质量评分: 72/100 🟠
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 严重问题 (3)
🟠 高优先级 (8)
🟡 中等问题 (15)
🟢 低优先级 (12)

📁 问题文件排行
🔍 详细问题列表
💡 改进建议
```
