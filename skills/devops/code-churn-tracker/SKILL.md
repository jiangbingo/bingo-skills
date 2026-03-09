---
name: "code-churn-tracker"
description: "Use when user asks to track code changes, identify unstable files, analyze code stability, find frequently modified code, or detect high-churn areas"
---

# Code Churn Tracker

## Overview
Tracks code churn (change rate) to identify unstable, frequently modified files that may indicate technical debt, design issues, or areas needing refactoring.

## When to Invoke

Invoke this skill when:
- User asks which files change most frequently
- User requests code stability analysis
- User wants to identify high-churn code areas
- User asks about code modification patterns
- User needs to identify potential technical debt hotspots

## What It Does

1. **Analyzes Git History**: Uses git log to extract file change history
2. **Counts Modifications**: Tracks how many times each file has been modified
3. **Calculates Churn Metrics**: Computes change frequency and stability scores
4. **Identifies Hotspots**: Finds files with high modification rates
5. **Generates Reports**: Creates comprehensive analysis with recommendations

## Analysis Metrics

### Churn Rate
- **Total Commits**: Number of commits affecting each file
- **Change Frequency**: Commits per time period (daily/weekly/monthly)
- **Lines Changed**: Total added/deleted lines per file

### Stability Score
- **High Stability** (80-100): Rarely modified, stable code
- **Medium Stability** (50-79): Moderate changes, acceptable
- **Low Stability** (0-49): Frequent changes, potential issues

### Risk Assessment
- **High Churn Files**: Modified 10+ times in analysis period
- **Trending Files**: Recent increase in modification rate
- **Large Impact Files**: High churn + large file size

## Usage Examples

### Find High-Churn Files
```
User: "Which files change most frequently?"
User: "Show me high-churn files"
```

### Analyze Code Stability
```
User: "Analyze code stability"
User: "Check which files are unstable"
```

### Track Changes Over Time
```
User: "Track code changes over the last month"
User: "What files have been changing a lot lately?"
```

## Output Format

The skill provides:

1. **Summary Statistics**: Total commits, files analyzed, time range
2. **Top Churn Files**: Most frequently modified files
3. **Stability Analysis**: Files categorized by stability score
4. **Risk Assessment**: High-risk files needing attention
5. **Change Trends**: Files with increasing/decreasing churn
6. **Recommendations**: Actions to reduce code churn

## Implementation Notes

- Uses `git log --name-status --pretty=format:` for change tracking
- Analyzes commits within configurable time window (default: 90 days)
- Excludes certain file patterns (vendor, node_modules, etc.)
- Calculates stability index based on modification frequency
- Provides actionable recommendations for each risk level

## Risk Indicators

- **Churn Rate > 10 commits/week**: Very high churn
- **Stability Score < 30**: Unstable code
- **Consistent Recent Changes**: Ongoing instability
- **Large File + High Churn**: Complex, unstable area

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Assuming high churn means bad code | Some files legitimately change often (configs, tests) | Consider file type and purpose |
| Ignoring recently added files | New files have high churn but may be stabilizing | Check file age alongside churn rate |
| Focusing only on count, not impact | A 5-line utility changing often matters less than core logic | Weight by file size and complexity |
| Comparing across different file types | Test files naturally change more than stable libraries | Normalize by file type and purpose |
