---
name: "git-commit-analyzer"
description: "Use when user asks to analyze Git commit history, view contributor statistics, check commit patterns, understand code contribution distribution, or assess commit message quality"
---

# Git Commit Analyzer

## Overview
Analyzes Git commit history to reveal contribution patterns, team activity distribution, and commit message quality using Conventional Commits specification.

## When to Invoke

Invoke this skill when:
- User asks to analyze Git commit history
- User requests code contribution statistics
- User wants to know who contributed the most
- User asks about commit patterns or frequency
- User needs to check commit message quality
- User wants to understand team activity distribution

## What It Does

1. **Fetches Commit Data**: Uses git log with JSON formatting to extract commit information
2. **Analyzes Contributors**: Ranks contributors by commit count and provides distribution statistics
3. **Generates Activity Heatmap**: Shows commit activity by hour of day and day of week
4. **Evaluates Commit Patterns**: Analyzes commit message length, frequency, and timing
5. **Assesses Message Quality**: Checks compliance with Conventional Commits specification
6. **Creates Comprehensive Reports**: Generates detailed text reports with visual statistics

## Analysis Features

### Contributor Statistics
- Total commit count
- Top contributors ranking
- Contribution distribution percentage
- Author activity timeline

### Activity Patterns
- Commits by hour of day (showing peak productivity hours)
- Commits by day of week (showing work patterns)
- Commits by month (showing long-term trends)
- Average commits per day/week/month

### Commit Message Quality
- Conventional Commits compliance check
- Message length distribution
- Common commit types (feat, fix, docs, etc.)
- Quality score and recommendations

### Temporal Analysis
- First and last commit dates
- Most active periods
- Commit frequency trends
- Streak analysis

## Usage Examples

### Analyze Commit History
```
User: "分析这个项目的提交历史"
User: "查看代码贡献统计"
User: "谁提交的代码最多"
```

### Check Commit Patterns
```
User: "查看提交模式"
User: "什么时候提交最多"
User: "分析提交频率"
```

### Evaluate Message Quality
```
User: "检查提交信息质量"
User: "提交信息是否符合规范"
```

## Output Format

The skill generates `commit_analysis_report.txt` containing:

1. **Summary Statistics**: Total commits, contributors, date range
2. **Contributor Leaderboard**: Ranked list with commit counts and percentages
3. **Activity Heatmap**: Hour-by-hour and day-by-week breakdown
4. **Commit Patterns**: Frequency analysis and trends
5. **Message Quality Assessment**: Conventional Commits compliance
6. **Visual Charts**: ASCII-based visualizations

## Implementation Notes

- Uses `git log` with custom JSON formatting
- Supports ISO date format parsing
- Handles non-UTF-8 commit messages gracefully
- Works with any Git repository
- No external dependencies beyond Python standard library

## Conventional Commits Pattern

The skill checks for commit messages following the pattern:
- `feat: ` - New features
- `fix: ` - Bug fixes
- `docs: ` - Documentation changes
- `style: ` - Code style changes
- `refactor: ` - Code refactoring
- `test: ` - Test additions or modifications
- `chore: ` - Maintenance tasks
- `perf: ` - Performance improvements

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Judging productivity by commit count alone | Some developers make larger, fewer commits | Consider lines changed and complexity alongside count |
| Ignoring merge commits | May miss important branch integration activity | Include or exclude merges consistently |
| Assuming low activity means low contribution | Some work happens in private branches | Consider branch structure and PR activity |
| Over-focusing on commit quality | Can discourage good submission practices | Balance quality feedback with encouragement |
