---
name: "branch-hygiene-checker"
description: "Use when user asks to check branch status, clean up old branches, identify zombie branches, analyze branch naming conventions, or get branch cleanup recommendations"
---

# Branch Hygiene Checker

## Overview
Checks Git repository branch health to identify zombie branches, merged branches, and naming convention violations for cleanup recommendations.

## When to Invoke

Invoke this skill when:
- User asks to check branch status
- User requests cleaning up old branches
- User wants to identify zombie branches
- User needs branch naming convention analysis
- User asks for branch cleanup recommendations
- User wants to analyze branch dependencies

## What It Does

1. **Lists All Branches**: Fetches all local and remote branches
2. **Detects Zombie Branches**: Identifies branches with no recent activity
3. **Identifies Merged Branches**: Finds branches that have been merged
4. **Validates Naming Conventions**: Checks if branches follow standard patterns
5. **Analyzes Dependencies**: Shows branch relationships and merge status
6. **Provides Cleanup Recommendations**: Suggests which branches can be safely removed

## Analysis Criteria

### Zombie Branches
- **Inactive**: No commits in 90+ days
- **Abandoned**: No recent pushes or updates
- **Orphaned**: Branch not based on main/master

### Merged Branches
- **Fully Integrated**: All commits merged to main branch
- **Safe to Delete**: No unmerged changes
- **Obsolete**: Feature complete and deployed

### Naming Conventions
- **feature/**: New feature branches
- **bugfix/**: Bug fix branches
- **hotfix/**: Critical hotfix branches
- **release/**: Release preparation branches
- **develop/**: Development environment branches

## Usage Examples

### Check Branch Status
```
User: "检查分支状态"
User: "Check branch status"
```

### Clean Up Old Branches
```
User: "清理旧分支"
User: "Clean up old branches"
```

### Identify Zombie Branches
```
User: "有哪些僵尸分支"
User: "Show me zombie branches"
User: "Identify inactive branches"
```

## Output Format

The skill provides:

1. **Summary Statistics**: Total branches, active vs inactive
2. **Zombie Branch List**: Branches with no recent activity
3. **Merged Branch List**: Branches safe to delete
4. **Naming Convention Report**: Branches following/not following patterns
5. **Dependency Analysis**: Branch relationships and base branches
6. **Cleanup Recommendations**: Prioritized list of branches to remove

## Implementation Notes

- Uses `git branch` commands to fetch branch information
- Uses `git log` to check last commit date
- Uses `git branch --merged` to find merged branches
- Uses `git merge-base` to determine branch relationships
- Generates detailed text report for easy review
- Provides safe deletion commands for cleanup

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Deleting branches without checking PR status | Branch may have unreviewed PR | Check PR tools (GitHub/GitLab) before deletion |
| Assuming merged means safe to delete | Branch may be used for deployment | Verify branch is not a release or deployment branch |
| Cleaning up during active development | May delete work-in-progress branches | Coordinate with team before cleanup |
| Ignoring remote branches | Local cleanup doesn't affect remote | Clean both local and remote branches |

## Red Flags - STOP and Review

- Branch name is `main`, `master`, `develop`, or `production`
- Branch is protected in repository settings
- Branch has recent commits (within 7 days)
- Branch name contains `release`, `hotfix`, or `deploy`
- Unmerged commits exist on the branch
- CI/CD pipeline references this branch

**All of these mean: Do NOT delete without manual verification.**
