---
name: "time-tracker-analyzer"
description: "Use when analyzing coding time patterns, identifying productive hours, tracking work habits, or visualizing commit time distribution"
---

# Time Tracker Analyzer

## Overview
Analyzes Git commit patterns to identify coding time distribution, productive hours, and work habits. Provides insights into when you're most active and productive.

## When to Invoke

Invoke this skill when:
- User asks to analyze their coding time
- User wants to know their most productive hours
- User requests work habit analysis
- User asks about commit time distribution
- User wants to understand their coding patterns

## What It Does

1. **Extracts Commit Data**: Uses git log to fetch commit timestamps
2. **Analyzes Time Patterns**: Groups commits by hour and day of week
3. **Identifies Peak Hours**: Finds most active time periods
4. **Compares Weekdays vs Weekends**: Analyzes work pattern differences
5. **Generates Visualizations**: Creates time distribution heatmaps and statistics
6. **Tracks Productivity Trends**: Shows coding activity over time

## Analysis Metrics

### Time Distribution
- **Hourly Activity**: Commits per hour (0-23)
- **Daily Activity**: Commits per day of week
- **Peak Hours**: Top 5 most active hours
- **Quiet Hours**: Least active time periods

### Work Patterns
- **Weekday vs Weekend**: Activity comparison
- **Morning/Afternoon/Evening**: Time-of-day preferences
- **Consistency**: Regularity of commit patterns
- **Burst Detection**: Identifies intense coding sessions

### Productivity Insights
- **Most Productive Day**: Day with highest commit count
- **Best Time Window**: Optimal 3-hour period for deep work
- **Work-Life Balance**: Weekend and late-night activity
- **Streak Analysis**: Consecutive days with commits

## Usage Examples

### Analyze Coding Time
```
User: "分析我的编码时间"
User: "什么时候最有效率"
User: "查看我的编码习惯"
```

### Time Distribution
```
User: "Show me when I commit code"
User: "What are my most productive hours?"
User: "Am I more active on weekdays or weekends?"
```

### Habit Analysis
```
User: "分析我的工作模式"
User: "我通常在什么时间写代码"
User: "查看我的提交时间分布"
```

## Output Format

The skill provides:

1. **Summary Statistics**: Total commits, date range, activity level
2. **Hourly Distribution**: Commits per hour with visualization
3. **Daily Distribution**: Activity by day of week
4. **Peak Hours**: Top 5 most active hours
5. **Work Patterns**: Weekday vs weekend comparison
6. **Productivity Insights**: Actionable recommendations
7. **Time Heatmap**: Visual representation of activity

## Implementation Notes

- Uses `git log --date=format:'%Y-%m-%d %H:%M'` for timestamp extraction
- Supports both local Git repositories and current directory analysis
- Handles timezones using local system time
- Generates text-based heatmap visualizations
- Provides Chinese-friendly output format

## Common Patterns Identified

| Pattern | Description | Recommendation |
|---------|-------------|----------------|
| Early Bird | Most commits 6-10 AM | Schedule deep work in morning |
| Night Owl | Most commits 10 PM-2 AM | Consider adjusting schedule for better balance |
| Weekend Warrior | High weekend activity | Ensure adequate rest and work-life balance |
| Consistent Coder | Even distribution across weekdays | Maintain sustainable schedule |
| Burst Coder | Intense activity periods | Regularize commit patterns for consistency |

## Technical Details

- Parses Git commit dates using datetime module
- Aggregates data by hour (0-23) and day (0-6)
- Generates ASCII-based heatmap visualizations
- Handles repositories with no commits gracefully
- Supports filtering by date range if needed

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Assuming more commits = more productive | High commit count may indicate small, trivial changes | Consider lines changed and complexity alongside count |
| Ignoring time zones | Commits may appear at unexpected times | Data uses local system time, be aware of timezone differences |
| Judging weekend activity negatively | Some developers prefer weekend coding | Personal preferences vary, focus on consistency instead |
| Expecting perfect distribution | Natural variation in activity patterns is normal | Look for general trends rather than perfection |
| Comparing across different roles | Different roles have different commit patterns | Compare your own patterns over time, not with others |
