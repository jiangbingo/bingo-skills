#!/bin/bash
# Bingo Downloader - Web UI Convenience Script
# Quick launcher for the Web UI server

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Bingo Downloader - Web UI${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check virtual environment
if [ ! -f "$SCRIPT_DIR/.venv/bin/python" ]; then
    echo -e "${YELLOW}⚠ Virtual environment not found${NC}"
    echo "Run from project root: make install-web"
    exit 1
fi

# Detect mode
MODE="${1:-run}"

case "$MODE" in
    run|dev)
        if [ "$MODE" = "dev" ]; then
            echo -e "${GREEN}► Starting in development mode (auto-reload enabled)...${NC}"
            RELOAD="--reload"
        else
            echo -e "${GREEN}► Starting in production mode...${NC}"
            RELOAD=""
        fi
        echo ""

        cd "$SCRIPT_DIR"
        PYTHONPATH="$PROJECT_ROOT" .venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 $RELOAD
        ;;

    install)
        echo -e "${GREEN}► Installing dependencies...${NC}"
        cd "$SCRIPT_DIR"
        uv pip install -r requirements.txt
        ;;

    shell)
        echo -e "${GREEN}► Activating virtual environment...${NC}"
        echo "Type 'exit' to leave"
        echo ""
        cd "$SCRIPT_DIR"
        .venv/bin/bash
        ;;

    test)
        echo -e "${GREEN}► Running tests...${NC}"
        cd "$SCRIPT_DIR"
        .venv/bin/pytest -v
        ;;

    *)
        echo "Usage: $0 [run|dev|install|shell|test]"
        echo ""
        echo "Commands:"
        echo "  run     - Start server (default)"
        echo "  dev     - Start with auto-reload"
        echo "  install - Install dependencies"
        echo "  shell   - Activate venv shell"
        echo "  test    - Run tests"
        exit 1
        ;;
esac
