# Changelog Generator Skill

## 概述

这个 Skill 用于自动生成项目变更日志（CHANGELOG.md），通过分析 Git 提交历史和版本标签，按照 Keep a Changelog 格式生成规范的 Markdown 文档。

## 文件结构

```
skillsets/changelog-generator/
├── SKILL.md          # Skill 定义文件
├── impl.py           # 实现脚本
├── test_skill.py     # 测试脚本
└── README.md         # 使用文档
```

## 如何使用

### 方式 1: 直接运行脚本

在 Git 仓库根目录执行：

```bash
python3 /path/to/skillsets/changelog-generator/impl.py
```

或者在项目根目录：

```bash
python3 skillsets/changelog-generator/impl.py
```

### 方式 2: 运行测试脚本

```bash
python3 skillsets/changelog-generator/test_skill.py
```

测试脚本会：
- 创建临时的测试 Git 仓库
- 生成测试提交和标签
- 运行变更日志生成器
- 验证输出文件
- 自动清理测试环境

### 方式 3: 通过 Skill 触发

在对话中使用以下短语：

**中文触发词：**
- "生成 changelog"
- "生成变更日志"
- "最近有什么改动"
- "版本发布日志"
- "创建 release notes"
- "显示版本变更"

**英文触发词：**
- "Generate changelog"
- "Create release notes"
- "Show recent changes"
- "What's new in this version"
- "Summarize changes between versions"

## 功能特性

### 1. 约定式提交解析

支持识别以下提交类型：

| 类型 | 分类 | 说明 |
|------|------|------|
| `feat` | Added | 新功能 |
| `fix` | Fixed | Bug 修复 |
| `perf` | Changed | 性能改进 |
| `refactor` | Changed | 代码重构 |
| `docs` | Changed | 文档更新 |
| `style` | Changed | 代码风格 |
| `test` | Changed | 测试更新 |
| `chore` | Changed | 构建/配置 |
| `revert` | Fixed | 回滚变更 |
| `build` | Changed | 构建系统 |
| `ci` | Changed | CI/CD |

### 2. 版本标签检测

- 自动读取 Git 标签（如 v1.0.0, 2.1.3）
- 按版本号排序
- 生成每个版本的变更内容
- 支持未发布提交（Unreleased）

### 3. 变更分类

按以下类别组织：
- **Added (新增)**: 新功能
- **Changed (变更)**: 现有功能的变更
- **Fixed (修复)**: Bug 修复
- **Removed (移除)**: 移除的功能
- **Security (安全)**: 安全相关

### 4. 破坏性变更

自动识别破坏性变更：
- 提交信息中包含 `!` 标记（如 `feat!: breaking change`）
- 提交描述中包含 `BREAKING CHANGE:`

## 输出格式

生成的 CHANGELOG.md 遵循 [Keep a Changelog](https://keepachangelog.com/) 格式：

```markdown
# Changelog

所有重要变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [v1.0.0] - 2024-01-15

### 新增 (Added)
- 添加用户认证功能 (abc12345)
- 添加 API 接口文档 (def67890)

### 修复 (Fixed)
- 修复登录超时问题 (ghi13579)

### 变更 (Changed)
- 性能优化：减少数据库查询 (jkl24680)

## [v0.9.0] - 2024-01-01

### 新增 (Added)
- 初始版本功能 (mno12345)
```

## 约定式提交格式

推荐的提交信息格式：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

示例：

```bash
# 简单提交
git commit -m "feat: 添加用户登录功能"

# 带作用域
git commit -m "feat(api): 添加用户注册接口"

# 破坏性变更
git commit -m "feat!: 移除旧的 API 端点"

# 带详细说明
git commit -m "fix: 修复内存泄漏

这个 bug 导致在高负载下内存持续增长，
现在使用对象池来解决这个问题。"

# 多个 footer
git commit -m "chore: 升级依赖包

Closes #123
BREAKING CHANGE: 移除对 Node.js 14 的支持"
```

## 使用场景

### 场景 1: 生成完整变更日志

```bash
# 在项目根目录运行
python3 skillsets/changelog-generator/impl.py
```

适用于：
- 项目首次添加 CHANGELOG
- 定期更新变更日志
- 准备版本发布

### 场景 2: 版本发布

```bash
# 1. 更新 CHANGELOG
python3 skillsets/changelog-generator/impl.py

# 2. 编辑 CHANGELOG.md，完善版本说明
# 3. 提交变更
git add CHANGELOG.md
git commit -m "docs: 更新 CHANGELOG for v1.0.0"

# 4. 打标签
git tag v1.0.0

# 5. 推送到远程
git push origin main --tags
```

### 场景 3: 查看最近变更

生成的 CHANGELOG.md 包含 "Unreleased" 部分，显示自上个标签以来的所有变更。

## 测试状态

✅ 所有测试通过

测试覆盖：
- 文件结构验证
- 脚本可执行性
- Git 仓库初始化
- 提交解析
- 标签检测
- 输出文件生成

## 依赖要求

- **Git**: 必须在 Git 仓库中运行
- **Python 3.x**: 脚本执行环境
- **提交规范**: 推荐使用约定式提交格式

## 常见问题

### Q: 没有标签怎么办？

A: 脚本会生成无版本的日志，包含所有提交历史。建议使用语义化版本标签（如 v1.0.0）来更好地组织变更日志。

### Q: 如何处理非约定式提交？

A: 非约定式提交会被归类到 "Changed" 分类中，确保所有提交都被记录。

### Q: 如何自定义输出文件名？

A: 修改 `impl.py` 中的 `output_file` 参数：

```python
generator.generate(output_file='CUSTOM_CHANGELOG.md')
```

### Q: 支持哪些标签格式？

A: 支持任何 Git 标签格式，推荐使用语义化版本：
- `v1.0.0`
- `2.1.3`
- `release-1.0`

## 最佳实践

1. **使用约定式提交**: 确保提交信息遵循规范
2. **定期打标签**: 为每个发布版本打标签
3. **审查生成的日志**: 自动生成后手动调整内容
4. **包含破坏性变更**: 明确标注不兼容的变更
5. **保持格式一致**: 遵循 Keep a Changelog 格式

## 下一步

1. 在项目中使用约定式提交格式
2. 为重要版本打标签
3. 定期运行此脚本更新 CHANGELOG
4. 将 CHANGELOG.md 纳入版本控制

## 相关资源

- [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)
- [语义化版本](https://semver.org/lang/zh-CN/)
- [约定式提交](https://www.conventionalcommits.org/zh-hans/)
