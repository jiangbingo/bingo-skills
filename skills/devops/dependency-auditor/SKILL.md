---
name: "dependency-auditor"
description: "Use when user asks to check dependency security, scan for vulnerabilities, audit licenses, identify outdated packages, or get dependency update recommendations"
---

# Dependency Auditor

## Overview
Audits project dependencies for security vulnerabilities, outdated packages, and license compliance across multiple package managers (npm, pip, cargo, composer).

## When to Invoke

Invoke this skill when:
- User asks to check dependency security
- User requests vulnerability scanning
- User wants to audit package licenses
- User needs dependency update recommendations
- User asks to analyze dependency trees
- User wants to check for outdated packages

## What It Does

1. **Detects Package Managers**: Automatically detects npm, pip, cargo, composer, and other package managers
2. **Security Scanning**: Runs native audit commands (npm audit, pip-audit, cargo audit) to find vulnerabilities
3. **License Audit**: Checks package licenses for compliance issues
4. **Outdated Detection**: Identifies packages with available updates
5. **Dependency Tree Analysis**: Shows direct and transitive dependencies
6. **Update Recommendations**: Provides prioritized update suggestions

## Supported Package Managers

| Manager | Config File | Audit Command | License Check |
|---------|-------------|---------------|---------------|
| npm/Node.js | package.json | `npm audit` | Yes (license field) |
| pip/Python | requirements.txt, pyproject.toml | `pip-audit` | Yes (license classifier) |
| cargo/Rust | Cargo.toml | `cargo audit` | Yes (SPDX identifiers) |
| composer/PHP | composer.json | `composer audit` | Yes (license field) |
| maven/Java | pom.xml | N/A (manual) | Yes (license element) |
| gradle/Java | build.gradle | N/A (manual) | Yes |

## Analysis Criteria

### Security Vulnerabilities
- **Critical**: Remote code execution, SQL injection, auth bypass
- **High**: Privilege escalation, data exposure, XSS
- **Medium**: DoS, information disclosure
- **Low**: Minor issues, optional hardening

### Outdated Packages
- **Major**: New major version available (breaking changes)
- **Minor**: New minor version available (new features)
- **Patch**: New patch version available (bug fixes)
- **Deprecated**: Package officially deprecated

### License Compliance
- **Permissive**: MIT, Apache-2.0, BSD (generally safe)
- **Weak Copyleft**: LGPL, MPL (may require attribution)
- **Strong Copyleft**: GPL, AGPL (may require source disclosure)
- **Proprietary**: Commercial licenses (check terms)
- **Unknown**: No license specified (risk)

## Usage Examples

### Check All Dependencies
```
User: "Check my dependencies for security issues"
User: "Scan for vulnerabilities"
User: "Dependency audit"
```

### Get Update Recommendations
```
User: "What dependencies should I update?"
User: "Show outdated packages"
User: "Dependency update suggestions"
```

### License Audit
```
User: "Check package licenses"
User: "License compliance audit"
User: "Are there any GPL dependencies?"
```

## Output Format

The skill generates `dependency_audit_report.txt` with:

1. **Summary Statistics**: Total packages, vulnerable count, outdated count
2. **Security Findings**: Vulnerabilities grouped by severity
3. **Outdated Packages**: Updates available grouped by type (major/minor/patch)
4. **License Report**: All licenses with compliance notes
5. **Dependency Tree**: Direct vs transitive dependencies
6. **Recommendations**: Prioritized action items

## Security Best Practices

- Always audit dependencies before deploying to production
- Update critical/high vulnerabilities immediately
- Review license compatibility for your project type
- Keep dependencies updated to minimize attack surface
- Lock dependency versions in production
- Review new package versions before updating

## Implementation Notes

- Uses native audit tools when available (npm audit, pip-audit, cargo audit)
- Falls back to manual inspection for managers without audit commands
- Parses package config files for metadata
- Generates comprehensive reports with actionable recommendations
- Handles multiple package managers in a single project

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Updating without testing | Breaking changes can introduce bugs | Always test after dependency updates |
| Ignoring dev dependencies | Dev tools can have security issues too | Audit all dependencies, not just production |
| Assuming latest is best | May introduce incompatible changes | Review changelogs before updating |
| Batch updating everything | Hard to identify which update broke something | Update incrementally and test between updates |
| Ignoring license compatibility | GPL licenses may require source disclosure | Check license compatibility with your project |
