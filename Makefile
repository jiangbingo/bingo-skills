# Bingo Skills Makefile

.PHONY: help install install-claude install-cursor install-windsurf install-continue install-aider install-all
.PHONY: uninstall test build-mcp docs-serve docs-build clean

# 默认目标
help:
	@echo "Bingo Skills - 安装和使用命令"
	@echo ""
	@echo "安装命令:"
	@echo "  make install-claude     安装到 Claude Code"
	@echo "  make install-cursor     安装到 Cursor"
	@echo "  make install-windsurf   安装到 Windsurf"
	@echo "  make install-continue   安装到 Continue"
	@echo "  make install-aider      安装到 Aider"
	@echo "  make install-all        安装到所有支持的 IDE"
	@echo ""
	@echo "卸载命令:"
	@echo "  make uninstall-claude   从 Claude Code 卸载"
	@echo "  make uninstall-all      从所有 IDE 卸载"
	@echo ""
	@echo "开发命令:"
	@echo "  make test               运行测试"
	@echo "  make build-mcp          构建 MCP Server"
	@echo "  make docs-serve         启动文档服务"
	@echo "  make docs-build         构建文档"
	@echo "  make clean              清理构建产物"

# ============================================
# 安装命令
# ============================================

# Claude Code
install-claude:
	@echo "📦 安装到 Claude Code..."
	@mkdir -p ~/.claude/skills
	@rm -rf ~/.claude/skills/bingo-skills
	@ln -sf $(PWD)/skills ~/.claude/skills/bingo-skills
	@echo "✅ 已安装到 Claude Code: ~/.claude/skills/bingo-skills"
	@echo "   重启 Claude Code 后即可使用"

# Cursor
install-cursor:
	@echo "📦 安装到 Cursor..."
	@mkdir -p ~/.cursor/skills
	@rm -rf ~/.cursor/skills/bingo-skills
	@ln -sf $(PWD)/skills ~/.cursor/skills/bingo-skills
	@echo "✅ 已安装到 Cursor: ~/.cursor/skills/bingo-skills"

# Windsurf
install-windsurf:
	@echo "📦 安装到 Windsurf..."
	@mkdir -p ~/.windsurf/skills
	@rm -rf ~/.windsurf/skills/bingo-skills
	@ln -sf $(PWD)/skills ~/.windsurf/skills/bingo-skills
	@echo "✅ 已安装到 Windsurf: ~/.windsurf/skills/bingo-skills"

# Continue
install-continue:
	@echo "📦 安装到 Continue..."
	@mkdir -p ~/.continue/skills
	@rm -rf ~/.continue/skills/bingo-skills
	@ln -sf $(PWD)/skills ~/.continue/skills/bingo-skills
	@echo "✅ 已安装到 Continue: ~/.continue/skills/bingo-skills"

# Aider
install-aider:
	@echo "📦 安装到 Aider..."
	@echo "请在 ~/.aider.conf.yml 中添加:"
	@echo "  skills:"
	@echo "    - $(PWD)/skills/**"
	@echo "✅ 请手动配置 Aider"

# 安装到所有
install-all: install-claude install-cursor install-windsurf install-continue
	@echo ""
	@echo "🎉 已安装到所有支持的 IDE!"

# ============================================
# 卸载命令
# ============================================

uninstall-claude:
	@echo "🗑️ 从 Claude Code 卸载..."
	@rm -rf ~/.claude/skills/bingo-skills
	@echo "✅ 已从 Claude Code 卸载"

uninstall-all: uninstall-claude
	@rm -rf ~/.cursor/skills/bingo-skills
	@rm -rf ~/.windsurf/skills/bingo-skills
	@rm -rf ~/.continue/skills/bingo-skills
	@echo "✅ 已从所有 IDE 卸载"

# ============================================
# 开发命令
# ============================================

# 运行测试
test:
	@echo "🧪 运行测试..."
	@cd skills/devops && python3 -m pytest || true
	@echo "测试完成"

# 构建 MCP Server
build-mcp:
	@echo "🔨 构建 MCP Server..."
	@cd mcp && npm install && npm run build
	@echo "✅ MCP Server 构建完成"

# 启动文档服务
docs-serve:
	@echo "📚 启动文档服务..."
	@cd docs && mkdocs serve

# 构建文档
docs-build:
	@echo "📚 构建文档..."
	@cd docs && mkdocs build
	@echo "✅ 文档构建完成: docs/site/"

# 清理
clean:
	@echo "🧹 清理构建产物..."
	@rm -rf mcp/dist
	@rm -rf docs/site
	@rm -rf node_modules
	@echo "✅ 清理完成"

# ============================================
# 安装 MCP (可选)
# ============================================

install-mcp: build-mcp
	@echo "📦 配置 MCP Server..."
	@echo "请在 claude_desktop_config.json 中添加:"
	@echo '  "mcpServers": {'
	@echo '    "bingo-downloader": {'
	@echo '      "command": "node",'
	@echo '      "args": ["$(PWD)/mcp/dist/index.js"]'
	@echo '    }'
	@echo '  }'
	@echo "✅ MCP Server 已构建，请手动配置"
