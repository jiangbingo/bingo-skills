# GitHub Repository Analyzer Skill

## 概述

这个 Skill 用于分析 GitHub 仓库，帮助用户管理和清理仓库。

## 文件结构

```
.github-repo-analyzer/
├── SKILL.md          # Skill 定义文件
├── impl.py           # 实现脚本
├── test_skill.py     # 测试脚本
└── README.md         # 使用文档
```

## 如何使用

### 方式 1: 直接运行脚本

```bash
python3 skillsets/github-repo-analyzer/impl.py
```

### 方式 2: 运行测试脚本

```bash
python3 skillsets/github-repo-analyzer/test_skill.py
```

### 方式 3: 通过 Skill 触发

在对话中使用以下短语：
- "分析我的 GitHub 仓库"
- "检查我的 fork 项目"
- "哪些仓库可以删除"
- "GitHub 仓库清理建议"

## 输出文件

执行后会生成 `repos_analysis_report.txt` 文件，包含：
- 仓库统计信息
- 语言分布
- Fork 项目分析
- 原始项目分析
- 清理建议
- 活跃项目推荐保留

## 分析标准

### Fork 项目清理标准
- 超过 6 个月未更新
- 0 stars 和 0 forks
- 无自定义修改

### 原始项目清理标准
- 超过 1 年未更新
- 0 stars 和 0 forks
- 小于 100KB 磁盘使用

## 测试状态

✅ 所有测试通过

## 依赖

- `gh` CLI 工具
- Python 3.x

## 下一步

1. 查看 `repos_analysis_report.txt` 获取详细分析
2. 根据报告中的建议进行仓库清理
3. 定期重新运行此分析以跟踪仓库状态
