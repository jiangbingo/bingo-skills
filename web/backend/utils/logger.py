"""
Logging Configuration for Bingo Downloader

Provides a unified logging system with:
- Structured log output
- Log level configuration via environment variables
- File rotation by date
- Separate error and info logs
- Console and file handlers
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Colored console output formatter"""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m',       # Reset
    }

    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        return super().format(record)


class BingoLogger:
    """Unified logger for Bingo Downloader"""

    _loggers = {}

    @staticmethod
    def _get_log_dir() -> Path:
        """Get log directory path"""
        # Can be overridden by LOG_DIR environment variable
        log_dir = Path.home() / '.bingo-downloader' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir

    @staticmethod
    def _get_log_level() -> int:
        """Get log level from environment variable"""
        import os
        level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
        return getattr(logging, level_str, logging.INFO)

    @classmethod
    def get_logger(cls, name: str, log_file: Optional[str] = None) -> logging.Logger:
        """
        Get or create a logger instance

        Args:
            name: Logger name (usually __name__ from calling module)
            log_file: Optional specific log file name

        Returns:
            Configured logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(cls._get_log_level())

        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()

        # Console Handler with colored output
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.DEBUG)
        console_formatter = ColoredFormatter(
            fmt='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File Handlers
        log_dir = cls._get_log_dir()
        base_name = log_file or name.replace('.', '_')

        # Info log file
        info_handler = TimedRotatingFileHandler(
            filename=log_dir / f'{base_name}.log',
            when='midnight',
            interval=1,
            backupCount=30,  # Keep 30 days of logs
            encoding='utf-8'
        )
        info_handler.setLevel(logging.INFO)
        info_formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)s] %(name)s [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        info_handler.setFormatter(info_formatter)
        info_handler.addFilter(lambda record: record.levelno < logging.ERROR)
        logger.addHandler(info_handler)

        # Error log file
        error_handler = TimedRotatingFileHandler(
            filename=log_dir / f'{base_name}-error.log',
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)s] %(name)s [%(filename)s:%(lineno)d] - %(message)s\n'
            'Exception: %(exc_info)s\n',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        error_handler.setFormatter(error_formatter)
        logger.addHandler(error_handler)

        # Prevent propagation to avoid duplicate logs
        logger.propagate = False

        cls._loggers[name] = logger
        return logger


# Convenience functions for common logging patterns
def log_download_start(logger: logging.Logger, url: str, platform: str, **kwargs):
    """Log download start event"""
    logger.info(f"Download started | URL: {url} | Platform: {platform} | {kwargs}")


def log_download_success(logger: logging.Logger, url: str, file_path: str, duration: Optional[float] = None):
    """Log download success event"""
    duration_str = f" | Duration: {duration:.2f}s" if duration else ""
    logger.info(f"Download completed | URL: {url} | File: {file_path}{duration_str}")


def log_download_error(logger: logging.Logger, url: str, error: Exception, duration: Optional[float] = None):
    """Log download error event"""
    duration_str = f" | Duration: {duration:.2f}s" if duration else ""
    logger.error(f"Download failed | URL: {url} | Error: {str(error)}{duration_str}", exc_info=True)


def log_api_call(logger: logging.Logger, method: str, path: str, status_code: Optional[int] = None):
    """Log API call event"""
    level = logger.warning if status_code and status_code >= 400 else logger.debug
    level(f"API {method} {path} | Status: {status_code}")


# Legacy compatibility - create default logger for skill/scripts/download.py
def create_legacy_logger() -> logging.Logger:
    """
    Create logger compatible with existing download.py script
    Maintains backward compatibility with LOG_FILE = Path.home() / '.yt-dlp-download.log'
    """
    logger = logging.getLogger('bingo_downloader_legacy')
    logger.setLevel(logging.INFO)

    # Don't add handlers if already configured
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler at legacy location
    log_file = Path.home() / '.yt-dlp-download.log'
    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(console_formatter)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger
