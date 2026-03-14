# Bingo Skills

AI Agent 技能市场 - DevOps 工具 / 视频下载 / 技术指南

## 安装

```bash
# 克隆仓库
git clone https://github.com/jiangbingo/bingo-skills.git
cd bingo-skills

# 安装到 Claude Code
make install-claude

# 安装到 Cursor
make install-cursor

# 安装到所有支持的 IDE
make install-all
```

## Skills 列表

### DevOps 工具 (14个)

| Skill | 描述 |
|-------|------|
| `github-repo-analyzer` | GitHub 仓库分析 |
| `git-commit-analyzer` | Git 提交历史分析 |
| `branch-hygiene-checker` | 分支健康度检查 |
| `dependency-auditor` | 依赖安全审计 |
| `changelog-generator` | 变更日志生成 |
| `code-churn-tracker` | 代码变更率追踪 |
| `test-coverage-analyzer` | 测试覆盖率分析 |
| `complexity-mapper` | 代码复杂度映射 |
| `knowledge-mapper` | 知识图谱映射 |
| `code-smell-detector` | 代码异味检测 |
| `time-tracker-analyzer` | 编码时间分析 |
| `task-completion-tracker` | 任务完成追踪 |
| `context-switch-monitor` | 上下文切换监控 |
| `doc-coverage-checker` | 文档覆盖率检查 |

### 下载工具 (1个)

| Skill | 描述 |
|-------|------|
| `bingo-downloader` | 1000+ 网站视频下载、音频提取、字幕下载 |

### 演示工具 (2个)

| Skill | 描述 |
|-------|------|
| `flowchart-slides` | 卡通手绘风格HTML幻灯片生成器，适用于流程演示、教学培训、营销方案 |
| `sketch-notes` | 工程师笔记本风格幻灯片，网格纸背景+手绘涂鸦+咖啡渍，适用于技术文档、开发者教程 |

### 技术指南 (1篇)

| Guide | 描述 |
|-------|------|
| `macbook-openclaw-guide` | MacBook Pro 2015 OpenClaw 安装指南 |

## 使用

安装后，直接在对话中使用：

> "分析这个 GitHub 仓库的代码质量"
> "下载这个视频 https://youtube.com/..."
> "生成一个4步流程的卡通风格幻灯片"
> "创建一个工程师笔记本风格的开发流程图"
> "如何安装 OpenClaw"

## MCP Server

视频下载器包含 MCP Server，可用于支持 MCP 的 AI IDE：

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "bingo-downloader": {
      "command": "node",
      "args": ["/path/to/bingo-skills/mcp/dist/index.js"]
    }
  }
}
```

## 项目结构

```
bingo-skills/
├── skills/                    # Skills 目录
│   ├── devops/               # DevOps 工具集 (14个)
│   ├── downloader/           # 视频下载器
│   ├── flowchart-slides/     # 卡通风格幻灯片生成器
│   ├── sketch-notes/         # 工程师笔记本风格幻灯片
│   └── guides/               # 技术指南
├── mcp/                       # MCP Server
├── web/                       # Web UI
├── scripts/                   # 安装脚本
├── docs/                      # 文档
├── CLAUDE.md                  # 本文件
├── README.md
└── Makefile
```

## Makefile 命令

```bash
make install-claude    # 安装到 Claude Code
make install-cursor    # 安装到 Cursor
make install-windsurf  # 安装到 Windsurf
make install-all       # 安装到所有
make test             # 运行测试
make docs-serve       # 启动文档服务
```
