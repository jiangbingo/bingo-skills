# .PHONY declarations
.PHONY: help check install install-all install-force uninstall uninstall-all update test clean \
	download audio subs quality list list-formats \
	cookie-download cookie-audio smart-download smart-audio \
	playlist playlist-range thumbnail history stats presets \
	batch-download batch-audio batch-subs \
	install-cursor install-claude install-gemini install-trae install-windsurf \
	uninstall-cursor uninstall-claude uninstall-gemini uninstall-trae uninstall-windsurf

# Default values
DOWNLOAD_PATH ?= $(HOME)/Downloads/yt-dlp
QUALITY ?= 1080
COOKIES_BROWSER ?= chrome

# Script selection: Use 'true' to use Python version, 'false' for Bash
USE_PYTHON ?= false

# Platform-specific skill directories
SKILL_NAME = bingo-downloader
CURSOR_SKILL_DIR ?= $(HOME)/.cursor/skills/$(SKILL_NAME)
CLAUDE_SKILL_DIR ?= $(HOME)/.claude/skills/$(SKILL_NAME)
CLAUDE_PLUGINS_DIR ?= $(HOME)/.claude/plugins/$(SKILL_NAME)
GEMINI_SKILL_DIR ?= $(HOME)/.gemini/skills/$(SKILL_NAME)
TRAE_SKILL_DIR ?= $(HOME)/.trae/skills/$(SKILL_NAME)
WINDSURF_SKILL_DIR ?= $(HOME)/.windsurf/skills/$(SKILL_NAME)

# Default to Cursor for backward compatibility
SKILL_DIR ?= $(CURSOR_SKILL_DIR)

# Auto-detect yt-dlp path (supports virtual environments)
YT_DLP_PATH := $(shell command -v yt-dlp 2>/dev/null)
ifeq ($(YT_DLP_PATH),)
    # Try common virtual environment locations
    YT_DLP_PATH := $(shell [ -f "$(HOME)/.venv/bin/yt-dlp" ] && echo "$(HOME)/.venv/bin/yt-dlp")
    ifeq ($(YT_DLP_PATH),)
        YT_DLP_PATH := $(shell [ -f "$(HOME)/.local/bin/yt-dlp" ] && echo "$(HOME)/.local/bin/yt-dlp")
    endif
endif

# Export for sub-shells
export YT_DLP_PATH

# Colors for terminal output
COLOR_RESET := \033[0m
COLOR_BOLD := \033[1m
COLOR_GREEN := \033[32m
COLOR_BLUE := \033[34m
COLOR_YELLOW := \033[33m
COLOR_CYAN := \033[36m

help: ## Show this help message
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)$(COLOR_BLUE)Bingo Downloader - Makefile Commands$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_BOLD)Script Mode:$(COLOR_RESET)"
	@echo "  $(COLOR_YELLOW)USE_PYTHON=false$(COLOR_RESET)     Use Bash script (default, fast)"
	@echo "  $(COLOR_YELLOW)USE_PYTHON=true$(COLOR_RESET)      Use Python script (rich output, cross-platform)"
	@echo ""
	@echo "  Example: $(COLOR_CYAN)make download USE_PYTHON=true URL=...$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_BOLD)Setup Commands:$(COLOR_RESET)"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*?##/ && $$1 !~ /^_/ {printf "  $(COLOR_GREEN)%-25s$(COLOR_RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(COLOR_BOLD)Platform Installation:$(COLOR_RESET)"
	@echo "  $(COLOR_YELLOW)make install-all       $(COLOR_RESET)Install to all detected platforms"
	@echo "  $(COLOR_YELLOW)make install-cursor    $(COLOR_RESET)Install to Cursor (~/.cursor/skills)"
	@echo "  $(COLOR_YELLOW)make install-claude    $(COLOR_RESET)Install to Claude Code (~/.claude/skills)"
	@echo "  $(COLOR_YELLOW)make install-gemini    $(COLOR_RESET)Install to Gemini Code (~/.gemini/skills)"
	@echo "  $(COLOR_YELLOW)make install-trae      $(COLOR_RESET)Install to Trae (~/.trae/skills)"
	@echo "  $(COLOR_YELLOW)make install-windsurf  $(COLOR_RESET)Install to Windsurf (~/.windsurf/skills)"
	@echo ""
	@echo "$(COLOR_BOLD)Download Commands:$(COLOR_RESET)"
	@echo "  $(COLOR_YELLOW)download URL=...        $(COLOR_RESET)Download video (best quality)"
	@echo "  $(COLOR_YELLOW)audio URL=...           $(COLOR_RESET)Extract audio only (MP3)"
	@echo "  $(COLOR_YELLOW)subs URL=...            $(COLOR_RESET)Download with subtitles"
	@echo "  $(COLOR_YELLOW)thumbnail URL=...       $(COLOR_RESET)Download with thumbnail image"
	@echo "  $(COLOR_YELLOW)quality URL=... Q=720   $(COLOR_RESET)Download with specific quality"
	@echo "  $(COLOR_YELLOW)list URL=...            $(COLOR_RESET)List available formats"
	@echo ""
	@echo "$(COLOR_BOLD)Smart Download (AI-Powered):$(COLOR_RESET)"
	@echo "  $(COLOR_YELLOW)smart-download URL=...  $(COLOR_RESET)Auto-select best format (requires USE_PYTHON=true)"
	@echo "  $(COLOR_YELLOW)smart-audio URL=...     $(COLOR_RESET)Auto-select best audio format"
	@echo ""
	@echo "$(COLOR_BOLD)Cookie Commands (for YouTube):$(COLOR_RESET)"
	@echo "  $(COLOR_YELLOW)cookie-download URL=... $(COLOR_RESET)Download using browser cookies"
	@echo "  $(COLOR_YELLOW)cookie-audio URL=...    $(COLOR_RESET)Extract audio using cookies"
	@echo ""
	@echo "$(COLOR_BOLD)Playlist Commands:$(COLOR_RESET)"
	@echo "  $(COLOR_YELLOW)playlist URL=...           $(COLOR_RESET)Auto-detect and download playlist"
	@echo "  $(COLOR_YELLOW)playlist-range URL=... RANGE=1-5  $(COLOR_RESET)Download specific playlist items"
	@echo ""
	@echo "$(COLOR_BOLD)History & Stats:$(COLOR_RESET)"
	@echo "  $(COLOR_YELLOW)history                    $(COLOR_RESET)Show download history (last 20)"
	@echo "  $(COLOR_YELLOW)stats                      $(COLOR_RESET)Show download statistics"
	@echo ""
	@echo "$(COLOR_BOLD)Configuration Presets:$(COLOR_RESET)"
	@echo "  $(COLOR_YELLOW)presets                    $(COLOR_RESET)List available presets"
	@echo "  $(COLOR_YELLOW)download URL=... PRESET=high-quality  $(COLOR_RESET)Use a preset"
	@echo ""
	@echo "$(COLOR_BOLD)Batch Commands:$(COLOR_RESET)"
	@echo "  $(COLOR_YELLOW)batch-download FILE=... $(COLOR_RESET)Batch download URLs from file"
	@echo "  $(COLOR_YELLOW)batch-audio FILE=...    $(COLOR_RESET)Batch extract audio from file"
	@echo ""
	@echo "$(COLOR_BOLD)Examples:$(COLOR_RESET)"
	@echo "  make check"
	@echo "  make install-all"
	@echo "  make download URL=\"https://www.youtube.com/watch?v=xxx\""
	@echo "  make audio URL=\"https://www.youtube.com/watch?v=xxx\""
	@echo "  make quality URL=\"https://www.youtube.com/watch?v=xxx\" Q=720"
	@echo "  make download USE_PYTHON=true URL=\"https://www.youtube.com/watch?v=xxx\""
	@echo "  make cookie-download URL=\"https://www.youtube.com/watch?v=xxx\""
	@echo "  make smart-download USE_PYTHON=true URL=\"https://www.youtube.com/watch?v=xxx\""
	@echo ""

check: ## Check if required dependencies are installed
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)Checking Dependencies...$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo ""
	@if [ -n "$(YT_DLP_PATH)" ]; then \
		VERSION=$$($(YT_DLP_PATH) --version 2>/dev/null); \
		echo "$(COLOR_GREEN)✓ yt-dlp$(COLOR_RESET) $$VERSION"; \
		echo "  Location: $(YT_DLP_PATH)"; \
	else \
		echo "$(COLOR_YELLOW)⚠ yt-dlp not found$(COLOR_RESET)"; \
		echo ""; \
		echo "  Install with:"; \
		if command -v uv >/dev/null 2>&1; then \
			echo "    $(COLOR_GREEN)uv pip install yt-dlp$(COLOR_RESET)"; \
		else \
			echo "    $(COLOR_GREEN)uv pip install yt-dlp$(COLOR_RESET)  # Recommended (fast)"; \
			echo "    $(COLOR_GREEN)curl -LsSf https://astral.sh/uv/install.sh | sh$(COLOR_RESET)  # Install uv first"; \
			echo "    $(COLOR_GREEN)pip install yt-dlp$(COLOR_RESET)  # Or use pip"; \
			echo "    $(COLOR_GREEN)pip3 install yt-dlp$(COLOR_RESET)  # Or use pip3"; \
		fi; \
		exit 1; \
	fi
	@command -v ffmpeg >/dev/null 2>&1 || { \
		echo "$(COLOR_YELLOW)⚠ ffmpeg not found$(COLOR_RESET)"; \
		echo ""; \
		echo "  Install with:"; \
		echo "    $(COLOR_GREEN)brew install ffmpeg$(COLOR_RESET)  # macOS"; \
		echo "    $(COLOR_GREEN)sudo apt install ffmpeg$(COLOR_RESET)  # Ubuntu/Debian"; \
		echo "    $(COLOR_GREEN)sudo dnf install ffmpeg$(COLOR_RESET)  # Fedora"; \
		exit 1; \
	}
	@echo "$(COLOR_GREEN)✓ ffmpeg$(COLOR_RESET) $$(ffmpeg -version | head -n1 | awk '{print $$3}')"
	@echo ""
	@echo "$(COLOR_GREEN)All dependencies satisfied!$(COLOR_RESET)"
	@echo ""

install: install-cursor ## Install to Cursor (default)
	@echo "$(COLOR_GREEN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)Installation Summary$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)✓ Installed to Cursor$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_YELLOW)To install to other platforms, use:$(COLOR_RESET)"
	@echo "  make install-all          # Install to all platforms"
	@echo "  make install-claude       # Install to Claude Code"
	@echo "  make install-gemini       # Install to Gemini"
	@echo "  make install-trae         # Install to Trae"
	@echo "  make install-windsurf     # Install to Windsurf"
	@echo ""

install-all: ## Install to all detected platforms
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)Installing to All Platforms...$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo ""
	@$(MAKE) install-cursor || true
	@$(MAKE) install-claude || true
	@$(MAKE) install-gemini || true
	@$(MAKE) install-trae || true
	@$(MAKE) install-windsurf || true
	@echo ""
	@echo "$(COLOR_GREEN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)All installations complete!$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo ""

install-cursor: check ## Install to Cursor
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)Installing to Cursor...$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@mkdir -p $(CURSOR_SKILL_DIR)/scripts
	@cp SKILL.md $(CURSOR_SKILL_DIR)/
	@cp scripts/download.sh $(CURSOR_SKILL_DIR)/scripts/
	@chmod +x $(CURSOR_SKILL_DIR)/scripts/download.sh
	@echo "$(COLOR_GREEN)✓ Installed to:$(COLOR_RESET) $(CURSOR_SKILL_DIR)"
	@echo ""

install-claude: check ## Install to Claude Code
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)Installing to Claude Code...$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@mkdir -p $(CLAUDE_SKILL_DIR)/scripts
	@cp SKILL.md $(CLAUDE_SKILL_DIR)/
	@cp scripts/download.sh $(CLAUDE_SKILL_DIR)/scripts/
	@chmod +x $(CLAUDE_SKILL_DIR)/scripts/download.sh
	@echo "$(COLOR_GREEN)✓ Installed to:$(COLOR_RESET) $(CLAUDE_SKILL_DIR)"
	@echo ""

install-gemini: check ## Install to Gemini Code
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)Installing to Gemini Code...$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@mkdir -p $(GEMINI_SKILL_DIR)/scripts
	@cp SKILL.md $(GEMINI_SKILL_DIR)/
	@cp scripts/download.sh $(GEMINI_SKILL_DIR)/scripts/
	@chmod +x $(GEMINI_SKILL_DIR)/scripts/download.sh
	@echo "$(COLOR_GREEN)✓ Installed to:$(COLOR_RESET) $(GEMINI_SKILL_DIR)"
	@echo ""

install-trae: check ## Install to Trae
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)Installing to Trae...$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@mkdir -p $(TRAE_SKILL_DIR)/scripts
	@cp SKILL.md $(TRAE_SKILL_DIR)/
	@cp scripts/download.sh $(TRAE_SKILL_DIR)/scripts/
	@chmod +x $(TRAE_SKILL_DIR)/scripts/download.sh
	@echo "$(COLOR_GREEN)✓ Installed to:$(COLOR_RESET) $(TRAE_SKILL_DIR)"
	@echo ""

install-windsurf: check ## Install to Windsurf
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)Installing to Windsurf...$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@mkdir -p $(WINDSURF_SKILL_DIR)/scripts
	@cp SKILL.md $(WINDSURF_SKILL_DIR)/
	@cp scripts/download.sh $(WINDSURF_SKILL_DIR)/scripts/
	@chmod +x $(WINDSURF_SKILL_DIR)/scripts/download.sh
	@echo "$(COLOR_GREEN)✓ Installed to:$(COLOR_RESET) $(WINDSURF_SKILL_DIR)"
	@echo ""

install-force: ## Force install without dependency check (Cursor only)
	@echo "$(COLOR_YELLOW)Installing without dependency check...$(COLOR_RESET)"
	@mkdir -p $(CURSOR_SKILL_DIR)/scripts
	@cp SKILL.md $(CURSOR_SKILL_DIR)/
	@cp scripts/download.sh $(CURSOR_SKILL_DIR)/scripts/
	@chmod +x $(CURSOR_SKILL_DIR)/scripts/download.sh
	@echo "$(COLOR_GREEN)✓ Skill installed to:$(COLOR_RESET) $(CURSOR_SKILL_DIR)"

uninstall: uninstall-cursor ## Uninstall from Cursor (default)
	@echo "$(COLOR_GREEN)✓ Uninstalled from Cursor$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_YELLOW)To uninstall from other platforms:$(COLOR_RESET)"
	@echo "  make uninstall-all"

uninstall-all: ## Uninstall from all platforms
	@echo "$(COLOR_YELLOW)Uninstalling from all platforms...$(COLOR_RESET)"
	@rm -rf $(CURSOR_SKILL_DIR) $(CLAUDE_SKILL_DIR) $(GEMINI_SKILL_DIR) $(TRAE_SKILL_DIR) $(WINDSURF_SKILL_DIR)
	@echo "$(COLOR_GREEN)✓ Uninstalled from all platforms$(COLOR_RESET)"

uninstall-cursor: ## Uninstall from Cursor
	@echo "$(COLOR_YELLOW)Removing from Cursor...$(COLOR_RESET)"
	@rm -rf $(CURSOR_SKILL_DIR)
	@echo "$(COLOR_GREEN)✓ Removed$(COLOR_RESET)"

uninstall-claude: ## Uninstall from Claude Code
	@echo "$(COLOR_YELLOW)Removing from Claude Code...$(COLOR_RESET)"
	@rm -rf $(CLAUDE_SKILL_DIR)
	@echo "$(COLOR_GREEN)✓ Removed$(COLOR_RESET)"

uninstall-gemini: ## Uninstall from Gemini Code
	@echo "$(COLOR_YELLOW)Removing from Gemini Code...$(COLOR_RESET)"
	@rm -rf $(GEMINI_SKILL_DIR)
	@echo "$(COLOR_GREEN)✓ Removed$(COLOR_RESET)"

uninstall-trae: ## Uninstall from Trae
	@echo "$(COLOR_YELLOW)Removing from Trae...$(COLOR_RESET)"
	@rm -rf $(TRAE_SKILL_DIR)
	@echo "$(COLOR_GREEN)✓ Removed$(COLOR_RESET)"

uninstall-windsurf: ## Uninstall from Windsurf
	@echo "$(COLOR_YELLOW)Removing from Windsurf...$(COLOR_RESET)"
	@rm -rf $(WINDSURF_SKILL_DIR)
	@echo "$(COLOR_GREEN)✓ Removed$(COLOR_RESET)"

update: ## Update yt-dlp to latest version
	@echo "$(COLOR_CYAN)Updating yt-dlp...$(COLOR_RESET)"
	@if command -v uv >/dev/null 2>&1; then \
		uv pip install -U yt-dlp; \
	elif command -v pip >/dev/null 2>&1; then \
		pip install -U yt-dlp; \
	elif command -v pip3 >/dev/null 2>&1; then \
		pip3 install -U yt-dlp; \
	else \
		echo "$(COLOR_YELLOW)⚠ No package manager found$(COLOR_RESET)"; \
		echo "Install uv or pip first"; \
		exit 1; \
	fi
	@echo "$(COLOR_GREEN)✓ yt-dlp updated$(COLOR_RESET)"

test: check ## Run tests and validation
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)Running Tests...$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_BLUE)Testing download.sh syntax...$(COLOR_RESET)"
	@bash -n scripts/download.sh && echo "$(COLOR_GREEN)✓ Script syntax valid$(COLOR_RESET)" || echo "$(COLOR_YELLOW)✗ Script syntax error$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_BLUE)Testing SKILL.md exists...$(COLOR_RESET)"
	@test -f SKILL.md && echo "$(COLOR_GREEN)✓ SKILL.md found$(COLOR_RESET)" || echo "$(COLOR_YELLOW)✗ SKILL.md not found$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_BLUE)Testing dependencies...$(COLOR_RESET)"
	@command -v yt-dlp >/dev/null 2>&1 && echo "$(COLOR_GREEN)✓ yt-dlp available$(COLOR_RESET)" || echo "$(COLOR_YELLOW)✗ yt-dlp not found$(COLOR_RESET)"
	@command -v ffmpeg >/dev/null 2>&1 && echo "$(COLOR_GREEN)✓ ffmpeg available$(COLOR_RESET)" || echo "$(COLOR_YELLOW)✗ ffmpeg not found$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_GREEN)Tests complete!$(COLOR_RESET)"
	@echo ""

clean: ## Clean temporary files
	@echo "$(COLOR_YELLOW)Cleaning temporary files...$(COLOR_RESET)"
	@rm -rf .DS_Store
	@echo "$(COLOR_GREEN)✓ Clean complete$(COLOR_RESET)"

# ============================================
# Download Commands
# ============================================

# Helper to determine which script to use
SCRIPT_CMD = $(shell if [ "$(USE_PYTHON)" = "true" ]; then echo "python3 scripts/download.py"; else echo "scripts/download.sh"; fi)

download: ## Download video (best quality)
	@if [ -z "$(URL)" ]; then \
		echo "$(COLOR_YELLOW)Usage: make download URL=<video_url>$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)Downloading Video...$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)Using: $(SCRIPT_CMD)$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@if [ "$(USE_PYTHON)" = "true" ]; then \
		python3 scripts/download.py -p "$(DOWNLOAD_PATH)" "$(URL)"; \
	else \
		scripts/download.sh -p "$(DOWNLOAD_PATH)" "$(URL)"; \
	fi

audio: ## Extract audio only (MP3)
	@if [ -z "$(URL)" ]; then \
		echo "$(COLOR_YELLOW)Usage: make audio URL=<video_url>$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)Extracting Audio...$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)Using: $(SCRIPT_CMD)$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@if [ "$(USE_PYTHON)" = "true" ]; then \
		python3 scripts/download.py -p "$(DOWNLOAD_PATH)" --audio "$(URL)"; \
	else \
		scripts/download.sh -p "$(DOWNLOAD_PATH)" -a "$(URL)"; \
	fi

subs: ## Download video with subtitles
	@if [ -z "$(URL)" ]; then \
		echo "$(COLOR_YELLOW)Usage: make subs URL=<video_url>$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)Downloading with Subtitles...$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)Using: $(SCRIPT_CMD)$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@if [ "$(USE_PYTHON)" = "true" ]; then \
		python3 scripts/download.py -p "$(DOWNLOAD_PATH)" --subs "$(URL)"; \
	else \
		scripts/download.sh -p "$(DOWNLOAD_PATH)" -s "$(URL)"; \
	fi

quality: ## Download with specific quality (Q=720,1080,etc.)
	@if [ -z "$(URL)" ]; then \
		echo "$(COLOR_YELLOW)Usage: make quality URL=<video_url> Q=720$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)Downloading at $(QUALITY)p...$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)Using: $(SCRIPT_CMD)$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@if [ "$(USE_PYTHON)" = "true" ]; then \
		python3 scripts/download.py -p "$(DOWNLOAD_PATH)" --quality "$(QUALITY)" "$(URL)"; \
	else \
		scripts/download.sh -p "$(DOWNLOAD_PATH)" -q "$(QUALITY)" "$(URL)"; \
	fi

list: list-formats ## List available formats for video
list-formats:
	@if [ -z "$(URL)" ]; then \
		echo "$(COLOR_YELLOW)Usage: make list URL=<video_url>$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)Available Formats:$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)Using: $(SCRIPT_CMD)$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@if [ "$(USE_PYTHON)" = "true" ]; then \
		python3 scripts/download.py --list "$(URL)"; \
	else \
		scripts/download.sh -l "$(URL)"; \
	fi

# ============================================
# Cookie Commands (for YouTube, etc.)
# ============================================

cookie-download: ## Download using browser cookies (for YouTube)
	@if [ -z "$(URL)" ]; then \
		echo "$(COLOR_YELLOW)Usage: make cookie-download URL=<video_url>$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)Downloading with Cookies ($(COOKIES_BROWSER))...$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)Using: $(SCRIPT_CMD)$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@if [ "$(USE_PYTHON)" = "true" ]; then \
		python3 scripts/download.py -p "$(DOWNLOAD_PATH)" --cookies "$(COOKIES_BROWSER)" "$(URL)"; \
	else \
		scripts/download.sh -p "$(DOWNLOAD_PATH)" -c "$(COOKIES_BROWSER)" "$(URL)"; \
	fi

cookie-audio: ## Extract audio using browser cookies
	@if [ -z "$(URL)" ]; then \
		echo "$(COLOR_YELLOW)Usage: make cookie-audio URL=<video_url>$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)Extracting Audio with Cookies ($(COOKIES_BROWSER))...$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)Using: $(SCRIPT_CMD)$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@if [ "$(USE_PYTHON)" = "true" ]; then \
		python3 scripts/download.py -p "$(DOWNLOAD_PATH)" --audio --cookies "$(COOKIES_BROWSER)" "$(URL)"; \
	else \
		scripts/download.sh -p "$(DOWNLOAD_PATH)" -a -c "$(COOKIES_BROWSER)" "$(URL)"; \
	fi

# ============================================
# Smart Download Commands (AI-Powered)
# ============================================

smart-download: ## Smart download with AI-powered format selection (requires USE_PYTHON=true)
	@if [ "$(USE_PYTHON)" != "true" ]; then \
		echo "$(COLOR_YELLOW)Smart download requires USE_PYTHON=true$(COLOR_RESET)"; \
		echo "Usage: make smart-download USE_PYTHON=true URL=<video_url>"; \
		exit 1; \
	fi
	@if [ -z "$(URL)" ]; then \
		echo "$(COLOR_YELLOW)Usage: make smart-download USE_PYTHON=true URL=<video_url>$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)🤖 Smart Download (AI-Powered Format Selection)$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@python3 scripts/download.py -p "$(DOWNLOAD_PATH)" --smart "$(URL)"

smart-audio: ## Smart audio extraction with AI-powered format selection (requires USE_PYTHON=true)
	@if [ "$(USE_PYTHON)" != "true" ]; then \
		echo "$(COLOR_YELLOW)Smart download requires USE_PYTHON=true$(COLOR_RESET)"; \
		echo "Usage: make smart-audio USE_PYTHON=true URL=<video_url>"; \
		exit 1; \
	fi
	@if [ -z "$(URL)" ]; then \
		echo "$(COLOR_YELLOW)Usage: make smart-audio USE_PYTHON=true URL=<video_url>$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)🤖 Smart Audio Extraction (AI-Powered Format Selection)$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@python3 scripts/download.py -p "$(DOWNLOAD_PATH)" --audio --smart "$(URL)"

# ============================================
# Playlist Commands
# ============================================

playlist: ## Download playlist (auto-detects and asks for range)
	@if [ -z "$(URL)" ]; then \
		echo "$(COLOR_YELLOW)Usage: make playlist URL=<playlist_url>$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)📋 Playlist Download$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@if [ "$(USE_PYTHON)" = "true" ]; then \
		python3 scripts/download.py -p "$(DOWNLOAD_PATH)" "$(URL)"; \
	else \
		scripts/download.sh -p "$(DOWNLOAD_PATH)" "$(URL)"; \
	fi

playlist-range: ## Download specific playlist items (RANGE=1-5,8,10-15)
	@if [ -z "$(URL)" ]; then \
		echo "$(COLOR_YELLOW)Usage: make playlist-range URL=<playlist_url> RANGE=1-5$(COLOR_RESET)"; \
		exit 1; \
	fi
	@if [ -z "$(RANGE)" ]; then \
		echo "$(COLOR_YELLOW)Usage: make playlist-range URL=<playlist_url> RANGE=1-5$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)📋 Playlist Download (Items: $(RANGE))$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@if [ "$(USE_PYTHON)" = "true" ]; then \
		python3 scripts/download.py -p "$(DOWNLOAD_PATH)" --playlist-items "$(RANGE)" "$(URL)"; \
	else \
		scripts/download.sh -p "$(DOWNLOAD_PATH)" --playlist-items "$(RANGE)" "$(URL)"; \
	fi

thumbnail: ## Download video with thumbnail image
	@if [ -z "$(URL)" ]; then \
		echo "$(COLOR_YELLOW)Usage: make thumbnail URL=<video_url>$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)🖼️  Download with Thumbnail$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@if [ "$(USE_PYTHON)" = "true" ]; then \
		python3 scripts/download.py -p "$(DOWNLOAD_PATH)" --thumbnail "$(URL)"; \
	else \
		scripts/download.sh -p "$(DOWNLOAD_PATH)" --thumbnail "$(URL)"; \
	fi

history: ## Show download history (last 20)
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)📜 Download History$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@python3 scripts/download.py --history

stats: ## Show download statistics
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)📊 Download Statistics$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@python3 scripts/download.py --stats

# ============================================
# Batch Commands
# ============================================

batch-download: ## Batch download videos from file (one URL per line)
	@if [ -z "$(FILE)" ]; then \
		echo "$(COLOR_YELLOW)Usage: make batch-download FILE=<url_list.txt>$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)📋 Batch Video Download$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@if [ "$(USE_PYTHON)" = "true" ]; then \
		python3 scripts/download.py -p "$(DOWNLOAD_PATH)" --batch "$(FILE)"; \
	else \
		scripts/download.sh -p "$(DOWNLOAD_PATH)" -b "$(FILE)"; \
	fi

batch-audio: ## Extract audio from multiple URLs in a file
	@if [ -z "$(FILE)" ]; then \
		echo "$(COLOR_YELLOW)Usage: make batch-audio FILE=<url_list.txt>$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)Batch Audio Extraction...$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@scripts/download.sh -p "$(DOWNLOAD_PATH)" -a -b "$(FILE)"

batch-subs: ## Download subtitles from multiple URLs in a file
	@if [ -z "$(FILE)" ]; then \
		echo "$(COLOR_YELLOW)Usage: make batch-subs FILE=<url_list.txt>$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)Batch Subtitle Download...$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@scripts/download.sh -p "$(DOWNLOAD_PATH)" -s -b "$(FILE)"

presets: ## List available configuration presets
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)📁 Configuration Presets$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_RESET)"
	@python3 scripts/download.py --list-presets
