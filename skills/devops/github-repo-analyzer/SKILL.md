---
name: "github-repo-analyzer"
description: "Use when user asks to analyze GitHub repositories, check fork status, get repository cleanup recommendations, view repository statistics, or identify unused repos"
---

# GitHub Repository Analyzer

## Overview
Analyzes GitHub repositories to identify cleanup opportunities, categorize forks vs originals, and provide actionable recommendations for repository management.

## When to Invoke

Invoke this skill when:
- User asks to analyze their GitHub repositories
- User requests fork project analysis
- User wants to know which repos can be deleted
- User needs repository cleanup recommendations
- User asks for repository statistics or storage analysis

## What It Does

1. **Fetches Repository Data**: Uses GitHub CLI to fetch all repositories with detailed metadata
2. **Analyzes Repository Types**: Separates forks from original repositories
3. **Evaluates Activity**: Checks update dates, stars, forks, and community engagement
4. **Identifies Cleanup Candidates**: Finds inactive, unused, or duplicate repositories
5. **Generates Reports**: Creates comprehensive analysis reports with recommendations

## Analysis Criteria

### Fork Repositories
- **Inactive**: No updates in 6+ months
- **No Engagement**: 0 stars and 0 forks
- **No Custom Changes**: Minimal or no contributions
- **Redundant**: Original repo is archived or unmaintained

### Original Repositories  
- **Old**: No updates in 1+ year
- **Unused**: 0 stars and 0 forks
- **Small**: Less than 100KB disk usage
- **Inactive**: No recent commits or activity

## Usage Examples

### Analyze All Repositories
```
User: "Analyze my GitHub repositories"
```

### Get Cleanup Suggestions
```
User: "Which repos should I delete?"
User: "Clean up my old fork projects"
```

### Check Fork Status
```
User: "Show me all my fork projects"
User: "How many forks do I have?"
```

## Output Format

The skill provides:

1. **Summary Statistics**: Total repos, forks vs originals, storage usage
2. **Language Distribution**: Top programming languages used
3. **Activity Analysis**: Active vs inactive repositories
4. **Cleanup Recommendations**: Repositories safe to delete with reasons
5. **Preservation List**: Active projects worth keeping

## Implementation Notes

- Uses `gh` CLI tool for GitHub API access
- Generates JSON and text reports for easy review
- Categorizes recommendations by priority (high/medium/low)
- Provides space estimates for cleanup impact

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Deleting forks without checking original | Original may have been deleted or changed | Verify original repo status before deleting fork |
| Assuming inactivity means uselessness | Some repos are reference/learning material | Check stars, forks, and personal notes |
| Ignoring license implications | Some forks have different licenses | Review license before cleanup |
| Batch deleting without review | May accidentally delete active projects | Review each recommendation individually |
