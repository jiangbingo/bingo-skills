# Bingo Downloader - Web Backend Makefile
# Convenient commands when working in the web/backend directory

.PHONY: help run dev install clean test shell status

# Default target
help:
	@echo "Bingo Downloader - Web Backend Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@echo "  run     - Start Web UI server (production mode)"
	@echo "  dev     - Start Web UI server (development mode with auto-reload)"
	@echo "  install - Install/update dependencies"
	@echo "  clean   - Clean Python cache files"
	@echo "  test    - Run tests"
	@echo "  shell   - Activate virtual environment and open shell"
	@echo ""
	@echo "Examples:"
	@echo "  make run       # Start server on http://localhost:8000"
	@echo "  make dev       # Start with auto-reload"
	@echo "  make shell     # Enter venv shell"
	@echo ""
	@echo "Note: Virtual environment is at .venv/"
	@echo ""

# Run server (production mode)
run:
	@echo "Starting Web UI server..."
	@PYTHONPATH=../.. .venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Run server (development mode)
dev:
	@echo "Starting Web UI server in development mode..."
	@PYTHONPATH=../.. .venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Install dependencies
install:
	@echo "Installing dependencies..."
	@uv pip install -r requirements.txt
	@echo "✓ Dependencies installed"

# Clean cache files
clean:
	@echo "Cleaning Python cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@rm -rf .pytest_cache 2>/dev/null || true
	@echo "✓ Clean complete"

# Run tests
test:
	@echo "Running tests..."
	@.venv/bin/pytest -v

# Activate virtual environment and open shell
shell:
	@echo "Activating virtual environment..."
	@echo "Type 'exit' to leave the shell"
	@echo "$$(basename .venv/bin/activate)"
	@.venv/bin/bash

# Show status
status:
	@echo "Web Backend Status:"
	@echo "  Virtual env: $$(test -f .venv/bin/python && echo '✓ Installed' || echo '✗ Not found')"
	@echo "  Python: $$(.venv/bin/python --version 2>&1)"
	@echo "  Location: $$(pwd)/.venv/"
