---
name: "task-completion-tracker"
description: "Use when tracking task completion, analyzing project velocity, identifying delayed tasks, measuring estimation accuracy, or examining task type distribution"
---

# Task Completion Tracker

## Overview
Analyzes Git commit history to track task completion patterns, measure project velocity, identify delayed tasks, and evaluate estimation accuracy based on conventional commit messages.

## When to Invoke

Invoke this skill when:
- User asks to analyze task completion rates
- User wants to understand why projects are delayed
- User requests task statistics or velocity analysis
- User needs to measure estimation accuracy
- User wants to analyze task type distribution (feature/bug/refactor)
- User asks about project productivity trends

## What It Does

1. **Parses Commit Messages**: Extracts task information from conventional commit format
2. **Categorizes Tasks**: Classifies commits into feat/fix/refactor/docs/test/chore
3. **Calculates Velocity**: Measures project velocity over time periods
4. **Identifies Patterns**: Detects task completion patterns and trends
5. **Analyzes Trends**: Shows task distribution and completion rates
6. **Generates Reports**: Creates comprehensive analysis with insights

## Task Categories

Based on Conventional Commits:
- **feat**: New features (feature tasks)
- **fix**: Bug fixes (bug tasks)
- **refactor**: Code refactoring (refactor tasks)
- **docs**: Documentation changes
- **test**: Test additions or updates
- **chore**: Maintenance tasks
- **style**: Code style changes
- **perf**: Performance improvements
- **ci**: CI/CD changes

## Analysis Metrics

### Task Distribution
- Percentage breakdown by task type
- Monthly/weekly task completion trends
- Feature vs bug fix ratio

### Project Velocity
- Tasks completed per week/month
- Velocity trends over time
- Comparison across time periods

### Task Patterns
- Peak completion days
- Active development periods
- Task clustering analysis

## Usage Examples

### Analyze Task Completion
```
User: "分析任务完成情况"
User: "Task completion analysis"
User: "Show me task statistics"
```

### Check Project Velocity
```
User: "项目速度怎么样？"
User: "Analyze project velocity"
User: "Are we completing tasks faster?"
```

### Understand Task Types
```
User: "我们主要在做什么类型的任务？"
User: "What type of tasks are we working on?"
```

## Output Format

The skill generates `task_completion_report.txt` with:

1. **Summary Statistics**: Total commits, time range, task types
2. **Task Distribution**: Breakdown by category (feat/fix/refactor/etc)
3. **Velocity Analysis**: Tasks completed per time period
4. **Trend Analysis**: Monthly/weekly patterns
5. **Type Trends**: How task mix changes over time
6. **Insights**: Key findings and recommendations

## Implementation Notes

- Parses conventional commit format: `type: description` or `type(scope): description`
- Supports common commit types from conventionalcommits.org
- Analyzes commits within configurable time window (default: 90 days)
- Excludes merge commits from task analysis
- Handles empty or malformed commit messages gracefully
- Generates visual charts using ASCII art

## Commit Types Reference

| Type | Description | Example |
|------|-------------|---------|
| feat | New feature | `feat: add user authentication` |
| fix | Bug fix | `fix: resolve login timeout issue` |
| refactor | Code refactoring | `refactor: simplify auth module` |
| docs | Documentation | `docs: update API documentation` |
| test | Test changes | `test: add unit tests for parser` |
| chore | Maintenance | `chore: upgrade dependencies` |
| style | Style changes | `style: format code with prettier` |
| perf | Performance | `perf: optimize database queries` |
| ci | CI/CD | `ci: add GitHub Actions workflow` |

## Velocity Calculation

Velocity is measured as:
- **Tasks per Week**: Number of completed tasks in a week
- **Tasks per Month**: Number of completed tasks in a month
- **Trend**: Increasing/decreasing/stable velocity

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Not using conventional commits | Can't categorize tasks | Adopt conventional commit format |
| Inconsistent commit messages | Skews task distribution | Follow commit conventions |
| Ignoring merge commits | Counts merges as tasks | Filter out merge commits |
| Short time windows | Insufficient data | Use at least 30-90 days |
| Counting all commits equally | Some commits are trivial | Consider commit scope/impact |
