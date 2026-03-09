---
name: "context-switch-monitor"
description: "Use when monitoring context switches, analyzing work fragmentation, identifying focus periods, or measuring attention fragmentation"
---

# Context Switch Monitor

## Overview
Analyzes context switching patterns in your workflow by examining Git commit history to identify work fragmentation, measure switching costs, and recommend focus improvements.

## When to Invoke

Invoke this skill when:
- User asks to analyze work interruption patterns
- User requests context switch analysis
- User wants to evaluate focus/attention fragmentation
- User needs to identify deep work periods
- User asks about work efficiency and concentration
- User mentions "被打断"、"上下文切换"、"专注度分析"

## What It Does

1. **Analyzes Git History**: Examines commit patterns to understand workflow
2. **Measures Context Switching**: Calculates frequency of file/module changes
3. **Identifies Focus Periods**: Detects blocks of concentrated work
4. **Evaluates Work Fragmentation**: Assesses how scattered work activities are
5. **Recommends Improvements**: Provides actionable focus enhancement suggestions

## Analysis Metrics

### Context Switch Frequency
- **File Switching**: Number of different files modified within time windows
- **Module Switching**: Changes between different code modules/directories
- **Switch Rate**: Switches per hour/day

### Work Fragmentation
- **Fragmentation Index**: Ratio of switches to total commits
- **Session Dispersion**: How spread out work is across modules
- **Task Hopping**: Frequency of jumping between unrelated tasks

### Focus Periods
- **Deep Work Blocks**: Continuous work on same module
- **Focus Score**: Quality of sustained attention periods
- **Interruption Analysis**: Points where context switches occur

## Usage Examples

### Analyze Context Switching
```
User: "分析我的工作被打断情况"
User: "上下文切换分析"
User: "Check my context switching patterns"
```

### Evaluate Focus
```
User: "专注度评估"
User: "How focused is my work pattern?"
User: "分析我的工作效率"
```

### Identify Work Patterns
```
User: "我什么时候工作最专注"
User: "找出我的深度工作时段"
```

## Output Format

The skill generates `context_switch_report.txt` containing:

1. **Summary Statistics**
   - Total commits analyzed
   - Time span covered
   - Average commits per day

2. **Context Switch Analysis**
   - Total context switches
   - Switch rate (switches/hour)
   - File switching frequency

3. **Module Analysis**
   - Most frequently switched modules
   - Module transition matrix
   - Work distribution across modules

4. **Focus Periods**
   - Identified deep work blocks
   - Longest focus sessions
   - Optimal work time windows

5. **Fragmentation Assessment**
   - Fragmentation index (0-100 scale)
   - Work concentration score
   - Comparison with optimal patterns

6. **Recommendations**
   - Focus improvement strategies
   - Batch work suggestions
   - Environment optimization tips

## Implementation Notes

- Uses `git log` to analyze commit history
- Calculates directory/module changes as context switches
- Identifies switches within configurable time windows (default: 30 minutes)
- Generates both quantitative metrics and qualitative insights
- Supports custom time range analysis

## Key Metrics Explained

### Fragmentation Index
- **0-25**: Highly focused - excellent deep work patterns
- **26-50**: Moderately focused - good with some switching
- **51-75**: Fragmented - frequent context switching
- **76-100**: Highly fragmented - attention severely scattered

### Context Switch
A switch occurs when:
- Consecutive commits modify files in different directories/modules
- Time gap between commits exceeds threshold (suggesting task break)
- File types change significantly (e.g., code → config → docs)

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Assuming all switches are bad | Some switches are necessary for integration | Distinguish between productive and distracting switches |
| Ignoring commit message patterns | Commits with same prefix may be same task | Group commits by message patterns to reduce false switches |
| Not accounting for branch context | Different branches may have legitimate switching | Analyze per-branch or account for branch switches |
| Measuring short time periods | Daily patterns vary significantly | Use at least 1-2 weeks of data for accurate assessment |

## Focus Recommendations

Based on analysis results, the skill may suggest:
- **Batch Similar Tasks**: Group related work together
- **Time Blocking**: Dedicate specific hours to specific modules
- **Notification Management**: Reduce interruptions during deep work
- **Commit Hygiene**: Use atomic commits for better tracking
