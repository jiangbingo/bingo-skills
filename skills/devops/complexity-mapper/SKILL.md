---
name: "complexity-mapper"
description: "Use when user asks to analyze code complexity, generate complexity heatmaps, identify refactoring priorities, or map cognitive complexity"
---

# Complexity Mapper

## Overview
Analyzes code complexity using cyclomatic and cognitive complexity metrics to identify areas needing refactoring, generates complexity heatmaps, and provides prioritized recommendations.

## When to Invoke

Invoke this skill when:
- User asks to analyze code complexity
- User wants to know which files need refactoring
- User requests complexity heatmaps
- User asks for refactoring priorities
- User needs to map cognitive complexity
- User wants to identify overly complex functions

## What It Does

1. **Calculates Cyclomatic Complexity**: Measures code paths and decision points
2. **Assesses Cognitive Complexity**: Evaluates how difficult code is to understand
3. **Ranks by Complexity**: Sorts files and functions by complexity scores
4. **Identifies Risk Zones**: Finds code exceeding complexity thresholds
5. **Generates Heatmaps**: Creates visual complexity distribution maps
6. **Provides Recommendations**: Suggests refactoring priorities

## Complexity Metrics

### Cyclomatic Complexity (CC)
- **1-10**: Simple, low risk
- **11-20**: Moderate complexity, medium risk
- **21-50**: High complexity, high risk
- **50+**: Very high complexity, critical risk

### Cognitive Complexity
- **0-5**: Easy to understand
- **6-10**: Moderate mental effort
- **11-20**: Difficult to understand
- **20+**: Very difficult, needs simplification

### Risk Levels
- **Low Risk**: CC < 15, Cognitive < 10
- **Medium Risk**: CC 15-25, Cognitive 10-15
- **High Risk**: CC 25-50, Cognitive 15-25
- **Critical Risk**: CC > 50, Cognitive > 25

## Usage Examples

### Analyze Code Complexity
```
User: "Analyze code complexity"
User: "分析代码复杂度"
User: "Show me complex code"
```

### Find Files Needing Refactoring
```
User: "Which files need refactoring?"
User: "哪些文件需要重构"
User: "Show refactoring priorities"
```

### Generate Complexity Heatmap
```
User: "Generate complexity heatmap"
User: "复杂度热图"
```

## Output Format

The skill generates `complexity_map_report.txt` containing:

1. **Summary Statistics**: Average complexity, total files analyzed
2. **Complexity Distribution**: Files grouped by risk level
3. **Top Complex Functions**: Most complex functions with line numbers
4. **File Rankings**: Files sorted by average complexity
5. **Risk Zones**: Code areas exceeding thresholds
6. **Refactoring Priorities**: Actionable recommendations

## Implementation Notes

- Uses radon for Python complexity analysis
- Uses lizard for multi-language complexity analysis
- Calculates both cyclomatic and cognitive complexity
- Identifies nesting depth and code duplication
- Provides function-level granularity for refactoring
- Excludes test files and generated code from analysis

## Supported Languages

| Language | Tool | Method |
|----------|------|--------|
| Python | radon | Cyclomatic complexity |
| Python | lizard | Cyclomatic complexity |
| JavaScript/TypeScript | eslint-plugin-complexity | Cyclomatic complexity |
| Java | lizard | Cyclomatic complexity |
| C/C++ | lizard | Cyclomatic complexity |
| Go | gocyclo | Cyclomatic complexity |

## Complexity Thresholds

Refactoring recommended when:
- **Function CC > 15**: Consider breaking down
- **Function CC > 25**: Should break down
- **Function CC > 50**: Must break down
- **File average CC > 20**: File needs restructuring
- **Nesting depth > 4**: Reduce nesting
- **Function length > 50 lines + high CC**: Split into smaller functions

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Confusing complexity with length | Short code can be complex | Measure decision points, not just lines |
| Ignoring context | Some domains are inherently complex | Consider business logic complexity |
| Focusing only on CC | Cyclomatic complexity misses readability | Also consider cognitive complexity |
| Refactoring without tests | May break functionality | Write tests before refactoring |
| Premature optimization | Small complexity may be acceptable | Focus on highest complexity first |

## Red Flags - STOP and Review

- Functions with CC > 100 (extremely complex)
- Files with average CC > 30
- Nesting depth > 6 levels
- Functions longer than 200 lines with high CC
- Critical business logic with CC > 20

**All of these mean: Critical complexity requiring immediate attention.**

## Running Complexity Analysis

### Python (radon)
```bash
pip install radon
radon cc . -a -s
```

### Multi-language (lizard)
```bash
pip install lizard
lizard . --CCN 15
```

## Refactoring Strategies

1. **Extract Method**: Break large functions into smaller ones
2. **Reduce Nesting**: Use early returns and guard clauses
3. **Simplify Conditions**: Break complex boolean expressions
4. **Strategy Pattern**: Replace complex conditionals with polymorphism
5. **State Machine**: Simplify complex state management

## Interpreting Results

**Low CC + Low Cognitive**: Good, maintainable code
**High CC + Low Cognitive**: May be verbose but straightforward
**Low CC + High Cognitive**: Subtle logic, needs documentation
**High CC + High Cognitive**: Critical refactoring needed
