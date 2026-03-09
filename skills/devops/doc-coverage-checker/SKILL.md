---
name: "doc-coverage-checker"
description: "Use when checking documentation coverage, finding undocumented functions, validating docstrings, or analyzing API documentation completeness"
---

# Documentation Coverage Checker

## Overview
Analyzes code documentation coverage to identify undocumented functions, classes, and modules. Provides comprehensive documentation quality scoring and generates detailed reports for improving code documentation.

## When to Invoke

Invoke this skill when:
- User asks to check documentation completeness or integrity
- User requests to find functions missing comments or docstrings
- User wants to know documentation coverage percentage
- User needs to validate API documentation
- User asks about code documentation quality
- User wants to identify undocumented public APIs

## What It Does

1. **Scans Code Files**: Analyzes Python, JavaScript/TypeScript, and other source files
2. **Parses AST**: Extracts functions, classes, and their documentation status
3. **Identifies Public APIs**: Distinguishes between public (non-underscore) and private members
4. **Checks Coverage**: Calculates documentation coverage rates for different code elements
5. **Quality Assessment**: Evaluates docstring quality and completeness
6. **Generates Reports**: Creates detailed reports with missing documentation lists

## Coverage Metrics

### Python Files
- **Function Coverage**: Functions with docstrings / total functions
- **Class Coverage**: Classes with docstrings / total classes
- **Method Coverage**: Methods with docstrings / total methods
- **Module Coverage**: Modules with docstrings / total modules
- **Public API**: Non-underscored functions/classes with documentation

### JavaScript/TypeScript Files
- **JSDoc Coverage**: Functions with JSDoc comments
- **Class Documentation**: Classes with documentation
- **Method Documentation**: Methods with JSDoc
- **Parameter Documentation**: Functions with parameter descriptions
- **Return Type Documentation**: Functions with return type documentation

## Documentation Quality Criteria

### High Quality Documentation
- Clear description of purpose
- Parameter types and descriptions
- Return value documentation
- Usage examples (for complex functions)
- Exception/rerror documentation
- Links to related functions

### Basic Documentation
- Function/class description
- Parameter list
- Return value (if applicable)

### Missing Documentation
- No docstring at all
- Empty docstring
- Single-word description (e.g., "TODO", "Fix me")

## Usage Examples

### Check Documentation Coverage
```
User: "Check documentation coverage for my project"
User: "Analyze code documentation completeness"
User: "Which functions are missing documentation?"
```

### Validate API Documentation
```
User: "Validate all public API documentation"
User: "Check if all public functions have docstrings"
User: "Find undocumented public methods"
```

### Documentation Quality
```
User: "Assess documentation quality"
User: "Rate our code documentation"
User: "Documentation completeness report"
```

## Output Format

The skill provides:

1. **Summary Statistics**: Overall coverage percentage, total elements analyzed
2. **Breakdown by Type**: Function, class, method, module coverage
3. **Public API Status**: Documentation status of public interfaces
4. **Missing Documentation**: List of undocumented elements
5. **Quality Assessment**: Documentation quality score and suggestions
6. **File-by-File Analysis**: Coverage per source file

## Analysis Approach

### Python Analysis
- Uses AST parsing to extract code structure
- Identifies docstrings from function/class/module bodies
- Separates public (non `_` prefixed) from private members
- Checks docstring content quality

### JavaScript/TypeScript Analysis
- Parses JSDoc comments
- Validates parameter documentation
- Checks return type documentation
- Identifies exported functions/classes

### Quality Scoring
- **Complete**: Has description, parameters, return value (90-100%)
- **Good**: Has description and key information (70-89%)
- **Basic**: Minimal description (50-69%)
- **Missing**: No documentation (0-49%)

## Implementation Notes

- Supports multiple programming languages
- Configurable file extensions and paths
- Excludes test files and generated code
- Generates both text and JSON reports
- Provides actionable improvement suggestions

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Only checking docstring existence | Empty docstrings pass the check | Validate docstring content and length |
| Including private methods | Inflates coverage percentage | Focus on public API documentation |
| Ignoring parameter documentation | Incomplete documentation | Check parameter and return value docs |
| Not excluding test files | Skews coverage metrics | Exclude test/ and tests/ directories |
| One-size-fits-all criteria | Different projects need different standards | Make quality thresholds configurable |
