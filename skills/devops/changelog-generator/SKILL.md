---
name: "changelog-generator"
description: "Use when generating changelogs, creating release notes, summarizing changes between versions, or documenting project history"
---

# Changelog Generator

## Overview
Automatically generates comprehensive changelogs from Git commit history, following the Keep a Changelog format with categorized changes (Added, Changed, Fixed, Removed).

## When to Invoke

Invoke this skill when:
- User asks to generate a changelog
- User requests release notes for a version
- User wants to know what changed between versions
- User asks for recent changes or modifications
- User needs to document project history
- User wants version release logs

## What It Does

1. **Parses Git History**: Extracts commit messages following Conventional Commits format
2. **Detects Version Tags**: Identifies version tags (v1.0.0, 2.0.0, etc.) for version organization
3. **Categorizes Changes**: Groups commits by type (feat, fix, refactor, docs, style, test, chore, perf, ci, build, revert)
4. **Generates Markdown**: Creates well-formatted CHANGELOG.md following Keep a Changelog standard
5. **Supports Version Ranges**: Can generate changelogs for specific version ranges or all history

## Commit Types Mapping

| Commit Type | Category | Description |
|-------------|----------|-------------|
| feat | Added | New features |
| fix | Fixed | Bug fixes |
| refactor | Changed | Code changes that neither fix a bug nor add a feature |
| perf | Changed | Performance improvements |
| docs | Changed | Documentation changes |
| style | Changed | Code style changes (formatting, etc.) |
| test | Changed | Test additions or modifications |
| chore | Changed | Maintenance tasks, dependency updates |
| ci | Changed | CI/CD configuration changes |
| build | Changed | Build system or external dependencies |
| revert | Removed | Reverted changes |

## Usage Examples

### Generate Full Changelog
```
User: "Generate changelog"
User: "Create a changelog for this project"
User: "生成变更日志"
```

### Generate for Specific Version Range
```
User: "What changed between v1.0.0 and v2.0.0?"
User: "Show changes since v1.5.0"
```

### Get Recent Changes
```
User: "What's new in the latest version?"
User: "最近有什么改动"
User: "Show me recent changes"
```

### Release Notes
```
User: "Generate release notes for v2.0.0"
User: "Create version 2.0.0 release log"
User: "版本发布日志"
```

## Output Format

Generates a `CHANGELOG.md` file with:

1. **Version Sections**: Each version has its own section with date
2. **Change Categories**: Added, Changed, Fixed, Removed sections
3. **Commit Links**: Each commit links to the commit in Git history
4. **Structured Format**: Follows Keep a Changelog standard for consistency

## Implementation Notes

- Uses `git log` to parse commit history
- Supports Conventional Commits format (type: description)
- Automatically detects version tags (v*, [0-9]*)
- Parses commit scope and breaking change indicators (!)
- Generates clean, human-readable Markdown output
- Handles Chinese and English commit messages

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Not following Conventional Commits | Changes won't be categorized correctly | Use proper commit format (feat: add feature) |
| Inconsistent tag formats | Version detection may fail | Use consistent tag format (v1.0.0 or 1.0.0) |
| Missing git tags | No version sections in changelog | Create tags for releases |
| Non-descriptive commit messages | Unclear changelog entries | Write clear, descriptive commit messages |

## Changelog Format

The generated CHANGELOG.md follows this structure:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-01-15

### Added
- New feature A (abc123)

### Fixed
- Bug fix B (def456)

### Changed
- Performance improvement C (ghi789)

## [1.0.0] - 2023-12-01
...
```
