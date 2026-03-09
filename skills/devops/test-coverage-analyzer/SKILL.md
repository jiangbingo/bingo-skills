---
name: "test-coverage-analyzer"
description: "Use when user asks to analyze test coverage, identify untested code, check coverage gaps, generate coverage reports, or find missing tests"
---

# Test Coverage Analyzer

## Overview
Analyzes test coverage data to identify untested code, generate coverage reports, and provide actionable recommendations for improving test coverage across multiple languages.

## When to Invoke

Invoke this skill when:
- User asks to analyze test coverage
- User requests identification of untested code
- User wants to check coverage gaps
- User asks for coverage reports
- User needs to find which code lacks tests
- User wants to track coverage trends

## What It Does

1. **Detects Coverage Tools**: Automatically detects coverage.py (Python), jest/vitest (JS), or other coverage tools
2. **Parses Coverage Data**: Reads .coverage files, coverage-report.json, or lcov.info
3. **Calculates Statistics**: Computes overall coverage percentage and per-file coverage
4. **Identifies Gaps**: Finds files, functions, or lines with zero or low coverage
5. **Generates Reports**: Creates detailed text reports with coverage heatmaps
6. **Provides Recommendations**: Suggests which areas need more testing

## Supported Coverage Tools

| Language | Tool | Config | Output File |
|----------|------|--------|-------------|
| Python | coverage.py | .coveragerc | .coverage, coverage.json |
| JavaScript/TypeScript | jest | jest.config.js | coverage/coverage-final.json |
| JavaScript/TypeScript | vitest | vitest.config.ts | coverage/coverage-final.json |
| Ruby | simplecov | .simplecov | coverage/.last_run.json |
| Java | jacoco | pom.xml / build.gradle | target/site/jacoco/jacoco.xml |
| Go | go test | - | profile.out |

## Analysis Metrics

### Coverage Levels
- **Excellent** (90-100%): Well-tested code
- **Good** (75-89%): Acceptable coverage
- **Fair** (50-74%): Needs improvement
- **Poor** (25-49%): Significant gaps
- **Critical** (0-24%): Barely tested

### Coverage Types
- **Line Coverage**: Percentage of executable lines covered
- **Branch Coverage**: Percentage of code branches covered
- **Function Coverage**: Percentage of functions called
- **Statement Coverage**: Percentage of statements executed

## Usage Examples

### Check Overall Coverage
```
User: "What's the test coverage?"
User: "测试覆盖率如何"
User: "Analyze test coverage"
```

### Find Untested Code
```
User: "Which code is not tested?"
User: "哪些代码缺少测试"
User: "Show me untested files"
```

### Generate Coverage Report
```
User: "Generate coverage report"
User: "生成测试覆盖率报告"
User: "Coverage analysis"
```

### Identify Coverage Gaps
```
User: "Where are the coverage gaps?"
User: "检查测试覆盖缺口"
```

## Output Format

The skill generates `test_coverage_report.txt` containing:

1. **Summary Statistics**: Overall coverage percentage, total files, covered lines
2. **Per-File Breakdown**: Coverage percentage for each file
3. **Zero Coverage Files**: List of files with no tests
4. **Low Coverage Files**: Files below threshold (default 50%)
5. **Coverage Distribution**: Files grouped by coverage level
6. **Recommendations**: Actionable suggestions for improvement
7. **Trend Analysis**: Comparison with previous reports (if available)

## Implementation Notes

- Runs coverage tools automatically if not already run
- Supports multiple programming languages in one project
- Handles missing coverage data gracefully
- Generates visual coverage heatmaps using ASCII
- Provides file-by-file breakdown for targeted testing
- Suggests priority files for testing based on complexity

## Coverage Thresholds

Default thresholds for recommendations:
- **Below 50%**: Critical - Add tests immediately
- **50-75%**: Needs improvement - Focus on uncovered paths
- **75-90%**: Good - Target edge cases
- **90%+**: Excellent - Maintain current level

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Assuming 100% coverage is always good | May test trivial code while missing edge cases | Focus on meaningful coverage, not just percentage |
| Ignoring branch coverage | Line coverage 100% but branches not tested | Check both line and branch coverage |
| Testing implementation, not behavior | Brittle tests that break on refactoring | Test interfaces and expected behavior |
| Counting generated code coverage | Inflates coverage without real value | Exclude vendor, generated files, mocks |
| Running coverage without tests | Shows 0% but doesn't indicate why | Ensure tests exist before running coverage |

## Red Flags - STOP and Review

- Coverage decreasing between runs
- Critical business logic below 75% coverage
- Authentication/authorization code below 90% coverage
- Zero coverage for files modified in last week
- Coverage report missing after running tests

**All of these mean: Investigate why coverage is low or declining before proceeding.**

## Running Coverage Tools

### Python (coverage.py)
```bash
pip install coverage
coverage run -m pytest
coverage report
coverage json  # Generates coverage.json
```

### JavaScript/TypeScript (jest)
```bash
npm test -- --coverage --coverageReporters=json
```

### JavaScript/TypeScript (vitest)
```bash
npx vitest run --coverage
```

## Interpreting Results

**High coverage + low bug rate**: Good test quality
**High coverage + high bug rate**: Tests may not be meaningful
**Low coverage + low bug rate**: Lucky - add tests before bugs appear
**Low coverage + high bug rate**: Critical - comprehensive testing needed
