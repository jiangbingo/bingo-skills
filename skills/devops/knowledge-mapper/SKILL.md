---
name: "knowledge-mapper"
description: "Use when user asks to generate project knowledge maps, analyze module dependencies, identify code experts, detect knowledge silos, or understand code ownership"
---

# Project Knowledge Mapper

## Overview
Generates comprehensive knowledge maps of codebases by analyzing Git history to identify module relationships, code ownership patterns, and expert areas for team coordination.

## When to Invoke

Invoke this skill when:
- User asks to generate project knowledge graphs
- User wants to know who owns specific modules or files
- User requests module dependency analysis
- User needs to identify code experts
- User wants to detect knowledge silos
- User asks about file relationships and associations
- User needs code ownership analysis for team coordination

## What It Does

1. **Analyzes Git History**: Extracts author-file mappings from commit history
2. **Builds Co-occurrence Matrix**: Identifies which files are modified together
3. **Detects Module Dependencies**: Finds relationships between code modules
4. **Identifies Code Owners**: Maps authors to their areas of expertise
5. **Detects Knowledge Silos**: Finds files with few contributors (bus factor risk)
6. **Generates Knowledge Graph**: Creates Graphviz DOT format visualization

## Analysis Metrics

### Code Ownership
- **Primary Owner**: Author with most commits to a file
- **Contributor Count**: Number of unique authors per file
- **Ownership Concentration**: How concentrated the knowledge is

### Knowledge Risk
- **High Risk**: Files with 1-2 contributors (bus factor)
- **Medium Risk**: Files with 3-5 contributors
- **Low Risk**: Files with 6+ contributors

### Module Relationships
- **Strong Coupling**: Files frequently modified together
- **Weak Coupling**: Files rarely modified together
- **Isolated Modules**: Files with minimal cross-relationships

## Usage Examples

### Generate Knowledge Map
```
User: "Generate a knowledge map for this project"
User: "分析项目知识图谱"
User: "Who knows this codebase?"
```

### Identify Code Owners
```
User: "Who owns the authentication module?"
User: "谁是这个模块的专家?"
User: "Identify experts for each module"
```

### Detect Knowledge Silos
```
User: "Find knowledge silos in this project"
User: "哪些文件存在知识孤岛风险?"
User: "Check bus factor for critical files"
```

### Analyze Dependencies
```
User: "Show module dependencies"
User: "模块依赖关系分析"
User: "Which files are related to each other?"
```

## Output Format

The skill provides:

1. **Summary Statistics**: Total files, total authors, coverage
2. **Code Ownership Report**: Who owns what files
3. **Knowledge Risk Analysis**: Files at risk (bus factor)
4. **Module Relationships**: File co-occurrence matrix
5. **Expert Identification**: Top contributors per module
6. **Knowledge Graph**: DOT format for visualization

### Output Files

- `knowledge_map_report.txt`: Detailed text report
- `knowledge_graph.dot`: Graphviz DOT file (optional)

## Implementation Notes

- Uses `git log --pretty=format:'%an' --name-only` for author-file extraction
- Calculates Jaccard similarity for file relationships
- Generates DOT format for graph visualization
- Supports custom time range filtering
- Ignores generated files and common patterns

## Graph Visualization

To visualize the generated knowledge graph:

```bash
# Install Graphviz
brew install graphviz  # macOS
apt-get install graphviz  # Linux

# Generate PNG
dot -Tpng knowledge_graph.dot -o knowledge_graph.png

# Generate SVG
dot -Tsvg knowledge_graph.dot -o knowledge_graph.svg
```

## Risk Levels

| Risk Level | Contributors | Description |
|------------|-------------|-------------|
| 🔴 Critical | 1 | Single point of failure |
| 🟠 High | 2 | Bus factor = 2 |
| 🟡 Medium | 3-5 | Some knowledge sharing |
| 🟢 Low | 6+ | Good distribution |

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Assuming recent contributors = experts | Recent contributors may be fixing bugs, not designing | Look at commit history depth and type of changes |
| Ignoring generated files | May skew results with false knowledge silos | Exclude vendor, node_modules, build artifacts |
| Using commit count alone | Some contributors make many small commits | Consider lines changed and commit message patterns |
| Forgetting about code review knowledge | Reviewers know code without committing | Consider PR/code review data if available |
