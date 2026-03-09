# 🎯 Bingo Skills

> AI Agent 技能市场 - DevOps 工具 / 视频下载 / 技术指南

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/Skills-16-blue)](#skills-列表)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-blue.svg)](https://modelcontextprotocol.io/)

## ✨ 特性

- 🎯 **16 个 Skills** - DevOps 工具、视频下载、技术指南
- 🤖 **多 IDE 支持** - Claude Code、Cursor、Windsurf、Continue 等
- 📦 **MCP Server** - 支持 Model Context Protocol 的 AI IDE
- 🌐 **Web UI** - 独立的 Web 界面（视频下载器）

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/jiangbingo/bingo-skills.git
cd bingo-skills
```

### 2. 安装到你的 AI IDE

```bash
# Claude Code
make install-claude

# Cursor
make install-cursor

# 所有支持的 IDE
make install-all
```

### 3. 开始使用

安装后，直接在对话中使用：

> "分析这个仓库的代码质量"
> "下载这个视频 https://youtube.com/..."
> "检查分支健康度"

## 📋 Skills 列表

### DevOps 工具 (14个)

| Skill | 描述 | 输出 |
|-------|------|------|
| `github-repo-analyzer` | GitHub 仓库分析 | 清理建议 |
| `git-commit-analyzer` | Git 提交历史分析 | 提交统计 |
| `branch-hygiene-checker` | 分支健康度检查 | 分支清理建议 |
| `dependency-auditor` | 依赖安全审计 | 漏洞报告 |
| `changelog-generator` | 变更日志生成 | CHANGELOG.md |
| `code-churn-tracker` | 代码变更率追踪 | 变更热点 |
| `test-coverage-analyzer` | 测试覆盖率分析 | 覆盖率报告 |
| `complexity-mapper` | 代码复杂度映射 | 复杂度热图 |
| `knowledge-mapper` | 知识图谱映射 | 依赖关系图 |
| `code-smell-detector` | 代码异味检测 | 质量评分 |
| `time-tracker-analyzer` | 编码时间分析 | 时间分布 |
| `task-completion-tracker` | 任务完成追踪 | 任务统计 |
| `context-switch-monitor` | 上下文切换监控 | 专注度分析 |
| `doc-coverage-checker` | 文档覆盖率检查 | 文档完整性 |

### 下载工具 (1个)

| Skill | 描述 | 支持平台 |
|-------|------|---------|
| `bingo-downloader` | 视频/音频下载 | YouTube, Bilibili, Twitter, TikTok 等 1000+ |

### 技术指南 (1篇)

| Guide | 描述 |
|-------|------|
| `macbook-openclaw-guide` | MacBook Pro 2015 OpenClaw 安装指南 |

## 🤖 支持的 AI IDE

| IDE | 安装命令 | 状态 |
|-----|---------|------|
| Claude Code | `make install-claude` | ✅ 完全支持 |
| Cursor | `make install-cursor` | ✅ 完全支持 |
| Windsurf | `make install-windsurf` | ✅ 完全支持 |
| Continue | `make install-continue` | ✅ 完全支持 |
| Aider | `make install-aider` | ✅ 完全支持 |
| Cline | `make install-cline` | ✅ 实验性 |

## 📦 MCP Server

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

### MCP 工具

- `download_video` - 下载视频
- `extract_audio` - 提取音频
- `download_with_subs` - 下载带字幕
- `list_formats` - 列出可用格式
- `get_history` - 获取下载历史
- `get_stats` - 获取统计信息

## 🌐 Web UI

视频下载器包含独立的 Web UI：

```bash
# 启动 Web UI
make run-web

# 访问
open http://localhost:8000
```

## 📁 项目结构

```
bingo-skills/
├── skills/                    # Skills 目录
│   ├── devops/               # DevOps 工具 (14个)
│   ├── downloader/           # 视频下载器
│   └── guides/               # 技术指南
├── mcp/                       # MCP Server
│   ├── src/                  # TypeScript 源码
│   └── dist/                 # 编译输出
├── web/                       # Web UI
│   ├── backend/              # FastAPI 后端
│   └── frontend/             # HTML/CSS/JS
├── scripts/                   # 安装脚本
├── docs/                      # 文档
├── CLAUDE.md                  # Claude Code 入口
├── README.md                  # 本文件
└── Makefile                   # 构建命令
```

## 🛠️ Makefile 命令

### 安装

```bash
make install-claude     # 安装到 Claude Code
make install-cursor     # 安装到 Cursor
make install-windsurf   # 安装到 Windsurf
make install-continue   # 安装到 Continue
make install-aider      # 安装到 Aider
make install-all        # 安装到所有
make uninstall          # 卸载
```

### 开发

```bash
make build             # 构建 MCP Server
make dev              # 开发模式
make test             # 运行测试
make check            # 检查依赖
```

### 文档

```bash
make docs-serve       # 启动文档服务
make docs-build       # 构建文档
```

## 📄 许可证

MIT License

## 🙏 致谢

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 视频下载引擎
- [Model Context Protocol](https://modelcontextprotocol.io/) - AI 工具标准

---

Made with ❤️ by [jiangbingo](https://github.com/jiangbingo)
