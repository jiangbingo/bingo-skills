"""
Bingo Downloader Web - Core Module
Reuses core logic from skill/scripts/download.py
"""
import sys
from pathlib import Path

# Add skill scripts to path for importing core classes
skill_scripts_path = Path(__file__).resolve().parent.parent.parent.parent / "skill" / "scripts"
if str(skill_scripts_path) not in sys.path:
    sys.path.insert(0, str(skill_scripts_path))

try:
    from download import (
        BingoDownloader,
        DownloadHistory,
        SmartFormatSelector,
        SmartRetry,
        ConfigPresets,
        UserPreferences
    )
    CORE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import core modules: {e}")
    CORE_AVAILABLE = False
    BingoDownloader = None
    DownloadHistory = None

__all__ = [
    "BingoDownloader",
    "DownloadHistory",
    "SmartFormatSelector",
    "SmartRetry",
    "ConfigPresets",
    "UserPreferences",
    "CORE_AVAILABLE",
]
