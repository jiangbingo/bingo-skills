#!/usr/bin/env python3
"""
Bingo Video Downloader - Python Version

A powerful video downloader powered by yt-dlp with enhanced features.
Supports 1000+ websites including YouTube, Bilibili, Twitter, TikTok, and more.

Usage:
    python download.py "https://www.youtube.com/watch?v=xxx"
    python download.py --audio "VIDEO_URL"
    python download.py --quality 720 --subs "VIDEO_URL"
"""

import argparse
import json
import logging
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add web/backend to path for logger import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "web" / "backend"))

try:
    from utils.logger import BingoLogger, log_download_start, log_download_success, log_download_error
    logger = BingoLogger.get_logger('bingo_downloader', log_file='download')
except ImportError:
    # Fallback to legacy logger if web backend is not available
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )
    logger = logging.getLogger(__name__)

    def log_download_start(lg, url, platform, **kwargs):
        lg.info(f"Download started | URL: {url} | Platform: {platform}")

    def log_download_success(lg, url, file_path, duration=None):
        dur_str = f" | Duration: {duration:.2f}s" if duration else ""
        lg.info(f"Download completed | URL: {url} | File: {file_path}{dur_str}")

    def log_download_error(lg, url, error, duration=None):
        dur_str = f" | Duration: {duration:.2f}s" if duration else ""
        lg.error(f"Download failed | URL: {url} | Error: {str(error)}{dur_str}")

try:
    import yt_dlp
except ImportError:
    print("❌ Error: yt-dlp not installed")
    print("\nInstall with:")
    print("  uv pip install yt-dlp")
    print("  pip install yt-dlp")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠ Warning: 'rich' not installed. Install for better output:")
    print("  pip install rich")

# Default configuration
DEFAULT_DOWNLOAD_PATH = Path.home() / "Downloads" / "yt-dlp"
DEFAULT_QUALITY = 1080
DEFAULT_COOKIES_BROWSER = "chrome"
PREFERENCES_FILE = Path.home() / ".yt-dlp-preferences.json"
MAX_FILE_SIZE_WARNING = 2 * 1024 * 1024 * 1024  # 2GB

# Retry configuration
MAX_RETRY_ATTEMPTS = 3
INITIAL_RETRY_DELAY = 5  # seconds
RETRY_BACKOFF_MULTIPLIER = 2  # exponential backoff

# 可重试的错误类型
RETRYABLE_ERRORS = [
    'HTTP Error 429',  # Too Many Requests
    'HTTP Error 503',  # Service Unavailable
    'HTTP Error 502',  # Bad Gateway
    'ConnectionError',
    'Timeout',
    'ReadTimeout',
    'network',
    'unable to download',
]


class ConfigPresets:
    """配置预设管理器"""

    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path.home() / '.yt-dlp-presets'
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def save_preset(self, name: str, config: Dict[str, Any]):
        """保存预设"""
        preset_file = self.config_dir / f"{name}.json"
        preset_file.write_text(json.dumps(config, indent=2))

    def load_preset(self, name: str) -> Optional[Dict[str, Any]]:
        """加载预设"""
        preset_file = self.config_dir / f"{name}.json"
        if preset_file.exists():
            try:
                return json.loads(preset_file.read_text())
            except Exception:
                return None
        return None

    def list_presets(self) -> List[Dict]:
        """列出所有预设"""
        presets = []
        for preset_file in self.config_dir.glob("*.json"):
            try:
                config = json.loads(preset_file.read_text())
                presets.append({
                    'name': preset_file.stem,
                    'description': config.get('description', ''),
                    'config': config
                })
            except Exception:
                pass
        return presets

    def delete_preset(self, name: str) -> bool:
        """删除预设"""
        preset_file = self.config_dir / f"{name}.json"
        if preset_file.exists():
            preset_file.unlink()
            return True
        return False

    def create_default_presets(self):
        """创建默认预设"""
        default_presets = {
            'high-quality': {
                'description': '高质量视频 (1080p, 包含字幕)',
                'quality': 1080,
                'subtitles': True,
                'write_thumbnail': True
            },
            'fast': {
                'description': '快速下载 (720p, 无字幕)',
                'quality': 720,
                'subtitles': False,
                'write_thumbnail': False
            },
            'audio-only': {
                'description': '仅音频 (高质量 MP3)',
                'audio_only': True,
                'subtitles': False,
                'write_thumbnail': False
            },
            'best': {
                'description': '最佳质量 (无限制)',
                'quality': None,
                'subtitles': True,
                'write_thumbnail': True
            }
        }

        for name, config in default_presets.items():
            if not self.load_preset(name):
                self.save_preset(name, config)


class DownloadHistory:
    """下载历史记录管理器"""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path.home() / '.yt-dlp-history.db'
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                platform TEXT,
                title TEXT,
                quality TEXT,
                filesize INTEGER,
                success BOOLEAN,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                download_path TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def record_download(self, url: str, platform: str, title: str = "",
                       quality: str = "", filesize: int = 0,
                       success: bool = True, download_path: str = ""):
        """记录下载"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO downloads
                (url, platform, title, quality, filesize, success, download_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (url, platform, title, quality, filesize, success, download_path))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠ Warning: Could not save to history: {e}")

    def get_history(self, limit: int = 20) -> List[Dict]:
        """获取历史记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT url, platform, title, quality, filesize, success, timestamp, download_path
                FROM downloads
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    'url': row[0],
                    'platform': row[1],
                    'title': row[2],
                    'quality': row[3],
                    'filesize': row[4],
                    'success': row[5],
                    'timestamp': row[6],
                    'download_path': row[7]
                }
                for row in rows
            ]
        except Exception as e:
            print(f"⚠ Warning: Could not read history: {e}")
            return []

    def get_stats(self) -> Dict:
        """获取统计信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 总下载次数
            cursor.execute('SELECT COUNT(*) FROM downloads')
            total = cursor.fetchone()[0]

            # 成功次数
            cursor.execute('SELECT COUNT(*) FROM downloads WHERE success = 1')
            success = cursor.fetchone()[0]

            # 失败次数
            cursor.execute('SELECT COUNT(*) FROM downloads WHERE success = 0')
            failed = cursor.fetchone()[0]

            # 总文件大小
            cursor.execute('SELECT SUM(filesize) FROM downloads WHERE success = 1')
            total_size = cursor.fetchone()[0] or 0

            # 按平台统计
            cursor.execute('''
                SELECT platform, COUNT(*) as count
                FROM downloads
                GROUP BY platform
                ORDER BY count DESC
            ''')
            by_platform = {row[0]: row[1] for row in cursor.fetchall()}

            conn.close()

            return {
                'total': total,
                'success': success,
                'failed': failed,
                'success_rate': f"{(success / total * 100):.1f}%" if total > 0 else "0%",
                'total_size': total_size,
                'by_platform': by_platform
            }
        except Exception as e:
            print(f"⚠ Warning: Could not get stats: {e}")
            return {}


class UserPreferences:
    """管理用户下载偏好设置"""

    def __init__(self):
        self.preferences = self._load_preferences()

    def _load_preferences(self) -> Dict[str, Any]:
        """从文件加载用户偏好"""
        if PREFERENCES_FILE.exists():
            try:
                return json.loads(PREFERENCES_FILE.read_text())
            except Exception:
                pass
        return {
            'preferred_quality': None,
            'preferred_codecs': ['h264', 'avc1'],
            'max_file_size': MAX_FILE_SIZE_WARNING,
            'download_count': 0,
            'format_history': []
        }

    def save_preferences(self):
        """保存用户偏好到文件"""
        try:
            PREFERENCES_FILE.write_text(json.dumps(self.preferences, indent=2))
        except Exception as e:
            print(f"⚠ Warning: Could not save preferences: {e}")

    def record_download(self, format_id: str, quality: int, filesize: int):
        """记录下载历史"""
        self.preferences['download_count'] += 1
        self.preferences['format_history'].append({
            'format_id': format_id,
            'quality': quality,
            'filesize': filesize,
            'timestamp': str(Path.ctime(PREFERENCES_FILE))
        })
        # 只保留最近 20 条记录
        if len(self.preferences['format_history']) > 20:
            self.preferences['format_history'] = self.preferences['format_history'][-20:]
        self.save_preferences()

    def get_preferred_quality(self) -> Optional[int]:
        """获取用户偏好的质量"""
        return self.preferences.get('preferred_quality')

    def set_preferred_quality(self, quality: int):
        """设置用户偏好的质量"""
        self.preferences['preferred_quality'] = quality
        self.save_preferences()


class SmartFormatSelector:
    """智能格式选择器 - 根据多个因素自动选择最佳格式"""

    def __init__(self, preferences: UserPreferences):
        self.preferences = preferences
        self.codecs_priority = {
            'h264': 10,
            'avc1': 10,
            'h265': 9,
            'hevc': 9,
            'vp9': 8,
            'av01': 7,
            'vp8': 5
        }

    def select_best_format(self, url: str, audio_only: bool = False) -> Optional[str]:
        """智能选择最佳视频格式"""
        try:
            # 获取视频信息
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)

            if audio_only:
                return self._select_best_audio(info)

            return self._select_best_video(info)

        except Exception as e:
            print(f"⚠ Warning: Smart format selection failed: {e}")
            print("Falling back to default format selection")
            return None

    def _select_best_video(self, info: Dict) -> str:
        """选择最佳视频格式"""
        formats = info.get('formats', [])

        # 过滤有效的视频格式
        video_formats = [
            f for f in formats
            if f.get('vcodec', 'none') != 'none' and f.get('height')
        ]

        if not video_formats:
            return 'bestvideo+bestaudio/best'

        # 为每个格式评分
        scored_formats = []
        for fmt in video_formats:
            score = self._score_format(fmt)
            scored_formats.append((score, fmt))

        # 按分数排序
        scored_formats.sort(key=lambda x: x[0], reverse=True)

        # 获取最佳格式
        best_score, best_format = scored_formats[0]

        # 检查文件大小
        filesize = best_format.get('filesize') or best_format.get('filesize_approx') or 0
        max_size = self.preferences.preferences.get('max_file_size', MAX_FILE_SIZE_WARNING)

        if filesize > max_size:
            print(f"\n⚠ Warning: Selected file is {filesize / 1024 / 1024 / 1024:.2f} GB")
            # 尝试选择较小的替代格式
            for score, fmt in scored_formats[1:]:
                size = fmt.get('filesize') or fmt.get('filesize_approx') or 0
                if size < max_size:
                    print(f"   → Using smaller alternative: {fmt.get('format', 'N/A')}")
                    return fmt.get('format_id')

            # 如果所有格式都太大，询问用户
            print(f"   All available formats exceed {max_size / 1024 / 1024 / 1024:.1f} GB")
            if RICH_AVAILABLE:
                from rich.prompt import Confirm
                if Confirm.ask("Continue with large download?"):
                    return best_format.get('format_id')
            else:
                response = input("Continue with large download? [y/N] ")
                if response.lower() == 'y':
                    return best_format.get('format_id')
            return None

        # 显示选择信息
        height = best_format.get('height', 'N/A')
        ext = best_format.get('ext', 'N/A')
        vcodec = best_format.get('vcodec', 'N/A')
        print(f"  ✓ Smart selection: {height}p {ext} ({vcodec}) - Score: {best_score}")

        # 记录用户偏好（如果他们多次选择相同质量）
        if isinstance(height, int):
            pref_quality = self.preferences.get_preferred_quality()
            if pref_quality == height:
                # 强化这个偏好
                pass
            elif not pref_quality:
                self.preferences.set_preferred_quality(height)

        return best_format.get('format_id')

    def _select_best_audio(self, info: Dict) -> str:
        """选择最佳音频格式"""
        formats = info.get('formats', [])

        # 过滤音频格式
        audio_formats = [
            f for f in formats
            if f.get('acodec', 'none') != 'none' and f.get('vcodec', 'none') == 'none'
        ]

        if audio_formats:
            # 优先选择高品质音频
            audio_formats.sort(
                key=lambda x: (x.get('abr') or 0, x.get('asr') or 0),
                reverse=True
            )
            best = audio_formats[0]
            print(f"  ✓ Smart audio selection: {best.get('ext', 'N/A')} - {best.get('abr', 'N/A')} kbps")
            return best.get('format_id')

        return 'bestaudio/best'

    def _score_format(self, fmt: Dict) -> int:
        """为格式评分"""
        score = 0

        # 1. 分辨率评分 (优先用户偏好)
        user_pref_quality = self.preferences.get_preferred_quality()
        height = fmt.get('height', 0)

        if user_pref_quality and height == user_pref_quality:
            score += 50
        elif height:
            # 1080p 以下优先级递减
            if height >= 1080:
                score += 40
            elif height >= 720:
                score += 35
            elif height >= 480:
                score += 25
            else:
                score += 10

        # 2. 编码格式评分
        vcodec = fmt.get('vcodec', '')
        for codec, priority in self.codecs_priority.items():
            if codec in vcodec:
                score += priority
                break

        # 3. 文件大小合理性 (避免过大文件)
        filesize = fmt.get('filesize') or fmt.get('filesize_approx') or 0
        if filesize > 0:
            # 500MB - 2GB 为理想范围
            if 500 * 1024 * 1024 <= filesize <= 2 * 1024 * 1024 * 1024:
                score += 15
            elif filesize > 2 * 1024 * 1024 * 1024:
                score -= 20  # 惩罚过大文件

        # 4. 帧率奖励 (60fps)
        fps = fmt.get('fps', 0)
        if fps >= 60:
            score += 10
        elif fps >= 30:
            score += 5

        # 5. HDR 奖励
        if fmt.get('dynamic_range') == 'HDR':
            score += 5

        return score


class SmartRetry:
    """智能重试管理器 - 带指数退避的自动重试"""

    def __init__(
        self,
        max_attempts: int = MAX_RETRY_ATTEMPTS,
        initial_delay: int = INITIAL_RETRY_DELAY,
        backoff_multiplier: float = RETRY_BACKOFF_MULTIPLIER
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.backoff_multiplier = backoff_multiplier

    def is_retryable_error(self, error_message: str) -> bool:
        """检查错误是否可以重试"""
        error_lower = error_message.lower()
        return any(err.lower() in error_lower for err in RETRYABLE_ERRORS)

    def execute_with_retry(self, func, *args, **kwargs):
        """执行函数，失败时自动重试"""
        last_error = None

        for attempt in range(self.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                error_msg = str(e)

                # 检查是否可重试
                if not self.is_retryable_error(error_msg):
                    if RICH_AVAILABLE:
                        print(f"\n[red]❌ Non-retryable error: {error_msg}[/red]")
                    else:
                        print(f"\n❌ Non-retryable error: {error_msg}")
                    raise

                # 如果是最后一次尝试，不再等待
                if attempt == self.max_attempts - 1:
                    break

                # 计算退避时间
                delay = self.initial_delay * (self.backoff_multiplier ** attempt)

                if RICH_AVAILABLE:
                    from rich.console import Console
                    console = Console()
                    console.print(f"\n[ yellow]⚠ Attempt {attempt + 1}/{self.max_attempts} failed:[/yellow] {error_msg[:100]}")
                    console.print(f"[yellow]   Retrying in {delay:.0f} seconds...[/yellow]")
                else:
                    print(f"\n⚠ Attempt {attempt + 1}/{self.max_attempts} failed: {error_msg[:100]}")
                    print(f"   Retrying in {delay:.0f} seconds...")

                time.sleep(delay)

        # 所有重试都失败
        if RICH_AVAILABLE:
            from rich.console import Console
            console = Console()
            console.print(f"\n[red]❌ All {self.max_attempts} attempts failed[/red]")
            console.print(f"[red]Last error: {last_error}[/red]")
        else:
            print(f"\n❌ All {self.max_attempts} attempts failed")
            print(f"Last error: {last_error}")

        raise last_error


class BingoDownloader:
    """Enhanced video downloader with yt-dlp backend."""

    def __init__(
        self,
        download_path: Path = DEFAULT_DOWNLOAD_PATH,
        audio_only: bool = False,
        quality: Optional[int] = None,
        subtitles: bool = False,
        cookies_browser: Optional[str] = None,
        cookies_file: Optional[str] = None,
        format_id: Optional[str] = None,
        list_formats: bool = False,
        smart_format: bool = False,
        write_thumbnail: bool = False,
    ):
        self.download_path = Path(download_path)
        self.audio_only = audio_only
        self.quality = quality
        self.subtitles = subtitles
        self.cookies_browser = cookies_browser
        self.cookies_file = cookies_file
        self.format_id = format_id
        self.list_formats = list_formats
        self.smart_format = smart_format
        self.write_thumbnail = write_thumbnail
        self.console = Console() if RICH_AVAILABLE else None

        # 初始化偏好和智能选择器
        self.preferences = UserPreferences()
        self.smart_selector = SmartFormatSelector(self.preferences) if smart_format else None
        self.retry_manager = SmartRetry()
        self.history = DownloadHistory()

    def _get_ydl_opts(self) -> dict:
        """Build yt-dlp options."""
        opts = {
            'outtmpl': str(self.download_path / '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'progress_hooks': [self._progress_hook] if RICH_AVAILABLE else [],
        }

        # Format selection
        if self.format_id:
            opts['format'] = self.format_id
        elif self.quality:
            opts['format'] = f'bestvideo[height<={self.quality}]+bestaudio/best[height<={self.quality}]'
        else:
            opts['format'] = 'bestvideo+bestaudio/best'

        # Audio extraction
        if self.audio_only:
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
            opts['audioformat'] = 'mp3'

        # Subtitles
        if self.subtitles:
            opts['writesubtitles'] = True
            opts['writeautomaticsub'] = True
            opts['subtitleslangs'] = ['all']
            opts['embedsubs'] = True

        # Thumbnail
        if self.write_thumbnail:
            opts['writethumbnail'] = True
            # Convert thumbnails to PNG for better compatibility
            opts['postprocessors'] = opts.get('postprocessors', [])
            opts['postprocessors'].append({
                'key': 'FFmpegThumbnailsConvertor',
                'format': 'png',
            })

        # Cookies
        if self.cookies_file:
            opts['cookiefile'] = self.cookies_file
        elif self.cookies_browser:
            opts['cookiesfrombrowser'] = (self.cookies_browser,)

        return opts

    def _progress_hook(self, d: dict):
        """Progress callback for downloads."""
        if d['status'] == 'downloading':
            if self.console:
                # Rich handles progress display separately
                pass
            else:
                percent = d.get('_percent_str', 'N/A')
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')
                print(f"\r  {percent} | Speed: {speed} | ETA: {eta}", end='', flush=True)
        elif d['status'] == 'finished':
            if not RICH_AVAILABLE:
                print("\n  ✓ Download complete, processing...")

    def detect_platform(self, url: str) -> str:
        """Detect video platform from URL."""
        if 'youtube.com' in url or 'youtu.be' in url:
            return 'YouTube'
        elif 'bilibili.com' in url:
            return 'Bilibili'
        elif 'twitter.com' in url or 'x.com' in url:
            return 'Twitter/X'
        elif 'tiktok.com' in url or 'douyin.com' in url:
            return 'TikTok/Douyin'
        else:
            return 'Unknown'

    def is_playlist(self, url: str) -> bool:
        """检测 URL 是否为播放列表"""
        playlist_indicators = [
            'list=',
            'playlist',
            '/playlist/',
            'fid=',  # Bilibili 收藏夹
            '/fav/',
            'series/',
            'collection/'
        ]
        return any(indicator in url for indicator in playlist_indicators)

    def get_playlist_info(self, url: str) -> Optional[Dict]:
        """获取播放列表信息"""
        try:
            with yt_dlp.YoutubeDL({
                'quiet': True,
                'extract_flat': True,  # 不下载每个视频的详细信息，提高速度
                'ignoreerrors': True
            }) as ydl:
                info = ydl.extract_info(url, download=False)

                if 'entries' in info:
                    # 这是播放列表
                    valid_entries = [e for e in info['entries'] if e is not None]
                    return {
                        'title': info.get('title', 'Unknown Playlist'),
                        'count': len(valid_entries),
                        'id': info.get('id', ''),
                        'uploader': info.get('uploader', 'Unknown'),
                        'type': 'playlist'
                    }
                else:
                    # 单个视频
                    return None
        except Exception as e:
            if RICH_AVAILABLE:
                self.console.print(f"[yellow]⚠ Could not check playlist status: {e}[/yellow]")
            else:
                print(f"⚠ Could not check playlist status: {e}")
            return None

    def _handle_playlist(self, url: str, playlist_info: Dict, playlist_items: Optional[str] = None):
        """处理播放列表下载"""
        # 显示播放列表信息
        if RICH_AVAILABLE:
            from rich.table import Table
            table = Table(title=f"📋 Playlist Detected")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            table.add_row("Title", playlist_info['title'])
            table.add_row("Videos", str(playlist_info['count']))
            table.add_row("Uploader", playlist_info['uploader'])
            self.console.print(table)
        else:
            print(f"\n  📋 Playlist Detected")
            print(f"  Title:   {playlist_info['title']}")
            print(f"  Videos:  {playlist_info['count']}")
            print(f"  Uploader: {playlist_info['uploader']}")

        # 如果没有指定范围，询问用户
        if not playlist_items:
            if RICH_AVAILABLE:
                from rich.prompt import Prompt
                self.console.print("\n[bold cyan]Download options:[/bold cyan]")
                self.console.print("  1. All videos")
                self.console.print("  2. Specify range (e.g., 1-5, 8-10)")
                self.console.print("  3. Cancel")
                choice = Prompt.ask("[bold cyan]Choose option[/bold cyan]", choices=["1", "2", "3"], default="1")

                if choice == "3":
                    self.console.print("[yellow]Download cancelled[/yellow]")
                    return
                elif choice == "2":
                    playlist_items = Prompt.ask("[bold cyan]Enter range[/bold cyan]", default="1-5")
                else:
                    playlist_items = None  # Download all
            else:
                print("\n  Download options:")
                print("  1. All videos")
                print("  2. Specify range (e.g., 1-5, 8-10)")
                print("  3. Cancel")
                choice = input("Choose option [1/2/3]: ").strip()

                if choice == "3":
                    print("  Download cancelled")
                    return
                elif choice == "2":
                    playlist_items = input("Enter range [1-5]: ").strip()
                else:
                    playlist_items = None  # Download all

        # 使用播放列表专用输出模板
        opts = self._get_ydl_opts()
        opts['outtmpl'] = str(self.download_path / '%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s')

        # 添加播放列表范围
        if playlist_items:
            opts['playlistitems'] = playlist_items
            if RICH_AVAILABLE:
                self.console.print(f"\n[bold cyan]Downloading items: {playlist_items}[/bold cyan]")
            else:
                print(f"\n  Downloading items: {playlist_items}")
        else:
            if RICH_AVAILABLE:
                self.console.print(f"\n[bold cyan]Downloading all {playlist_info['count']} videos...[/bold cyan]")
            else:
                print(f"\n  Downloading all {playlist_info['count']} videos...")

        # 下载播放列表
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                if RICH_AVAILABLE:
                    self.console.print("[bold cyan]Starting playlist download...[/bold cyan]\n")
                else:
                    print("  Starting playlist download...")

                ydl.download([url])

            if RICH_AVAILABLE:
                self.console.print("\n[bold green]✓ Playlist download complete![/bold green]")
                self.console.print(f"[green]Files saved to: {self.download_path / playlist_info['title']}[/green]")
            else:
                print(f"\n  ✓ Playlist download complete!")
                print(f"  Files saved to: {self.download_path / playlist_info['title']}")

        except Exception as e:
            if RICH_AVAILABLE:
                self.console.print(f"\n[red]❌ Playlist download failed: {e}[/red]")
            else:
                print(f"\n❌ Playlist download failed: {e}")
            sys.exit(1)

    def list_available_formats(self, url: str):
        """List all available formats for a video."""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)

            if RICH_AVAILABLE:
                table = Table(title=f"Available Formats - {info.get('title', 'Unknown')}")
                table.add_column("ID", style="cyan", no_wrap=True)
                table.add_column("Ext", style="green")
                table.add_column("Quality", style="yellow")
                table.add_column("FPS", style="blue")
                table.add_column("Size", style="magenta")

                for fmt in info.get('formats', [])[:20]:  # Show first 20
                    table.add_row(
                        fmt.get('format_id', 'N/A'),
                        fmt.get('ext', 'N/A'),
                        fmt.get('format_note', 'N/A'),
                        str(fmt.get('fps', 'N/A')),
                        fmt.get('filesize_approx', 'N/A') and f"{fmt['filesize_approx']/1024/1024:.1f}MB" or 'N/A'
                    )

                self.console.print(table)
            else:
                print(f"\n  Available formats for: {info.get('title', 'Unknown')}")
                print(f"  {'ID':<15} {'Ext':<6} {'Quality':<20} {'FPS':<6}")
                print("  " + "-" * 50)
                for fmt in info.get('formats', [])[:20]:
                    print(f"  {fmt.get('format_id', 'N/A'):<15} {fmt.get('ext', 'N/A'):<6} "
                          f"{fmt.get('format_note', 'N/A'):<20} {fmt.get('fps', 'N/A'):<6}")

        except Exception as e:
            print(f"❌ Error listing formats: {e}")
            sys.exit(1)

    def download(self, url: str, playlist_items: Optional[str] = None):
        """Download video(s) from URL."""
        # Create download directory
        self.download_path.mkdir(parents=True, exist_ok=True)

        # Detect platform
        platform = self.detect_platform(url)

        # Track download start time
        download_start_time = time.time()

        # Log download start
        log_download_start(logger, url, platform, quality=self.quality, audio_only=self.audio_only)

        # Auto-use cookies for YouTube if not specified
        if platform == 'YouTube' and not self.cookies_browser:
            self.cookies_browser = DEFAULT_COOKIES_BROWSER

        # 检测播放列表
        if self.is_playlist(url):
            playlist_info = self.get_playlist_info(url)
            if playlist_info:
                self._handle_playlist(url, playlist_info, playlist_items)
                return

        # 智能格式选择
        if self.smart_format and not self.format_id and not self.quality:
            if RICH_AVAILABLE:
                self.console.print("[bold cyan]🤖 Smart format selection enabled[/bold cyan]\n")
            else:
                print("\n  🤖 Smart format selection enabled")

            selected_format = self.smart_selector.select_best_format(url, self.audio_only)
            if selected_format:
                self.format_id = selected_format

        # Show download info
        if RICH_AVAILABLE:
            info_panel = Panel.fit(
                f"[bold cyan]Platform:[/bold cyan] {platform}\n"
                f"[bold cyan]Path:[/bold cyan] {self.download_path}\n"
                f"[bold cyan]Audio Only:[/bold cyan] {self.audio_only}\n"
                f"[bold cyan]Subtitles:[/bold cyan] {self.subtitles}\n"
                f"[bold cyan]Thumbnail:[/bold cyan] {self.write_thumbnail}\n"
                f"[bold cyan]Quality:[/bold cyan] {self.quality or 'Best available'}\n"
                f"[bold cyan]Smart Mode:[/bold cyan] {self.smart_format}\n"
                f"[bold cyan]Cookies:[/bold cyan] {self.cookies_browser or 'None'}",
                title="[bold green]Download Configuration[/bold green]",
                border_style="green"
            )
            self.console.print(info_panel)
        else:
            print(f"\n  Platform:     {platform}")
            print(f"  Download to:  {self.download_path}")
            print(f"  Audio only:   {self.audio_only}")
            print(f"  Subtitles:    {self.subtitles}")
            print(f"  Thumbnail:    {self.write_thumbnail}")
            print(f"  Quality:      {self.quality or 'Best available'}")
            print(f"  Smart Mode:   {self.smart_format}")
            print(f"  Cookies:      {self.cookies_browser or 'None'}\n")

        # Download with smart retry
        try:
            def _do_download():
                ydl_opts = self._get_ydl_opts()

                if RICH_AVAILABLE:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        self.console.print("[bold cyan]Starting download...[/bold cyan]\n")
                        ydl.download([url])
                else:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        print(f"  Starting download...")
                        ydl.download([url])

            # 使用智能重试
            self.retry_manager.execute_with_retry(_do_download)

            if RICH_AVAILABLE:
                self.console.print("\n[bold green]✓ Download complete![/bold green]")
                self.console.print(f"[green]Files saved to: {self.download_path}[/green]")
            else:
                print(f"\n  ✓ Download complete!")
                print(f"  Files saved to: {self.download_path}")

            # Log success
            duration = time.time() - download_start_time
            log_download_success(logger, url, str(self.download_path), duration)

            # 记录下载历史
            try:
                # 获取视频信息用于历史记录
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Unknown')
                    filesize = info.get('filesize') or info.get('filesize_approx') or 0

                self.history.record_download(
                    url=url,
                    platform=platform,
                    title=title,
                    quality=str(self.quality) if self.quality else "auto",
                    filesize=filesize,
                    success=True,
                    download_path=str(self.download_path)
                )
            except Exception:
                # 即使记录失败也不影响下载结果
                pass

        except Exception as e:
            # Log failure
            duration = time.time() - download_start_time
            log_download_error(logger, url, e, duration)

            # 记录失败的下载
            try:
                self.history.record_download(
                    url=url,
                    platform=platform,
                    quality=str(self.quality) if self.quality else "auto",
                    success=False
                )
            except Exception:
                pass

            if RICH_AVAILABLE:
                self.console.print(f"\n[red]❌ Download failed: {e}[/red]")
            else:
                print(f"\n❌ Download failed: {e}")
            sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Bingo Video Downloader - Download from 1000+ sites',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://www.youtube.com/watch?v=xxx"
  %(prog)s --audio "VIDEO_URL"
  %(prog)s --quality 720 --subs "VIDEO_URL"
  %(prog)s --cookies chrome "VIDEO_URL"
  %(prog)s --list "VIDEO_URL"
        """
    )

    parser.add_argument('url', nargs='?', help='Video URL to download')

    # Download options
    parser.add_argument('-p', '--path', type=Path, default=DEFAULT_DOWNLOAD_PATH,
                       help=f'Download path (default: {DEFAULT_DOWNLOAD_PATH})')
    parser.add_argument('-a', '--audio', action='store_true',
                       help='Extract audio only (MP3)')
    parser.add_argument('-s', '--subs', action='store_true',
                       help='Download subtitles')
    parser.add_argument('-q', '--quality', type=int, metavar='NUM',
                       help='Max video height (720, 1080, etc.)')
    parser.add_argument('-f', '--format', dest='format_id', metavar='ID',
                       help='Specific format ID')
    parser.add_argument('-l', '--list', action='store_true',
                       help='List available formats')
    parser.add_argument('-c', '--cookies', metavar='BROWSER',
                       help='Use cookies from browser (chrome, firefox, safari, etc.)')
    parser.add_argument('--smart', action='store_true',
                       help='Enable smart format selection (AI-powered quality selection)')
    parser.add_argument('-b', '--batch', type=Path, metavar='FILE',
                       help='Batch download from file (one URL per line)')
    parser.add_argument('--playlist-items', metavar='RANGE',
                       help='Download specific playlist items (e.g., "1-5,8,10-15")')
    parser.add_argument('--thumbnail', '--thumb', action='store_true',
                       help='Download video thumbnail')
    parser.add_argument('--history', action='store_true',
                       help='Show download history')
    parser.add_argument('--stats', action='store_true',
                       help='Show download statistics')
    parser.add_argument('--preset', metavar='NAME',
                       help='Use a configuration preset')
    parser.add_argument('--list-presets', action='store_true',
                       help='List available presets')
    parser.add_argument('--save-preset', metavar='NAME',
                       help='Save current options as a preset')

    args = parser.parse_args()

    # 检查历史和统计
    if args.history or args.stats:
        history = DownloadHistory()

        if args.stats:
            # 显示统计信息
            stats = history.get_stats()

            if RICH_AVAILABLE:
                from rich.console import Console
                from rich.table import Table
                from rich.panel import Panel
                console = Console()

                console.print("\n[bold cyan]📊 Download Statistics[/bold cyan]\n")

                # 总体统计
                console.print(Panel.fit(
                    f"[bold cyan]Total Downloads:[/bold cyan] {stats['total']}\n"
                    f"[green]✓ Success:[/green] {stats['success']}\n"
                    f"[red]✗ Failed:[/red] {stats['failed']}\n"
                    f"[bold]Success Rate:[/bold] {stats['success_rate']}\n"
                    f"[bold]Total Size:[/bold] {stats['total_size'] / 1024 / 1024 / 1024:.2f} GB",
                    title="[bold green]Summary[/bold green]",
                    border_style="green"
                ))

                # 按平台统计
                if stats.get('by_platform'):
                    table = Table(title="Downloads by Platform")
                    table.add_column("Platform", style="cyan")
                    table.add_column("Downloads", justify="right", style="green")
                    for platform, count in stats['by_platform'].items():
                        table.add_row(platform or "Unknown", str(count))
                    console.print(table)
            else:
                print(f"\n  📊 Download Statistics\n")
                print(f"  Total Downloads:  {stats['total']}")
                print(f"  ✓ Success:        {stats['success']}")
                print(f"  ✗ Failed:        {stats['failed']}")
                print(f"  Success Rate:    {stats['success_rate']}")
                print(f"  Total Size:      {stats['total_size'] / 1024 / 1024 / 1024:.2f} GB\n")

                if stats.get('by_platform'):
                    print("  By Platform:")
                    for platform, count in stats['by_platform'].items():
                        print(f"    {platform or 'Unknown'}: {count}")

        if args.history:
            # 显示历史记录
            records = history.get_history(limit=20)

            if RICH_AVAILABLE:
                from rich.console import Console
                from rich.table import Table
                console = Console()

                table = Table(title="Recent Downloads (Last 20)")
                table.add_column("Time", style="cyan", no_wrap=False)
                table.add_column("Platform", style="green")
                table.add_column("Title", style="yellow")
                table.add_column("Quality", style="blue")
                table.add_column("Result", style="bold")

                for record in records:
                    result = "[green]✓[/green]" if record['success'] else "[red]✗[/red]"
                    table.add_row(
                        record['timestamp'][:19] if record['timestamp'] else 'N/A',
                        record['platform'] or 'N/A',
                        record['title'][:40] if record['title'] else 'N/A',
                        record['quality'] or 'N/A',
                        result
                    )
                console.print(table)
            else:
                print(f"\n  📜 Recent Downloads (Last 20)\n")
                print(f"  {'Time':<20} {'Platform':<12} {'Title':<40} {'Quality':<8} {'Result'}")
                print("  " + "-" * 90)
                for record in records:
                    result = "✓" if record['success'] else "✗"
                    time_str = record['timestamp'][:19] if record['timestamp'] else 'N/A'
                    title = (record['title'][:37] + '..') if record['title'] and len(record['title']) > 40 else (record['title'] or 'N/A')
                    print(f"  {time_str:<20} {record['platform'] or 'N/A':<12} {title:<40} {record['quality'] or 'N/A':<8} {result}")

        sys.exit(0)

    # 预设管理
    presets = ConfigPresets()

    # 创建默认预设（如果不存在）
    if args.list_presets or args.preset:
        presets.create_default_presets()

    if args.list_presets:
        # 列出所有预设
        preset_list = presets.list_presets()

        if RICH_AVAILABLE:
            from rich.console import Console
            from rich.table import Table
            console = Console()

            table = Table(title="Configuration Presets")
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Description", style="green")
            table.add_column("Settings", style="yellow")

            for preset in preset_list:
                settings_str = ", ".join([
                    f"{k}={v}" for k, v in preset['config'].items()
                    if k != 'description' and v is not None and v is not False
                ])
                table.add_row(preset['name'], preset['description'], settings_str)
            console.print(table)
        else:
            print(f"\n  📁 Configuration Presets\n")
            for preset in preset_list:
                settings_str = ", ".join([
                    f"{k}={v}" for k, v in preset['config'].items()
                    if k != 'description' and v is not None and v is not False
                ])
                print(f"  [{preset['name']}]")
                print(f"    {preset['description']}")
                print(f"    Settings: {settings_str}")
                print()

        sys.exit(0)

    if args.save_preset:
        # 保存当前选项为预设
        preset_config = {
            'description': f'Preset: {args.save_preset}',
            'audio_only': args.audio,
            'quality': args.quality,
            'subtitles': args.subs,
            'write_thumbnail': args.thumbnail,
            'cookies_browser': args.cookies,
            'smart_format': args.smart
        }
        # 移除 None 和 False 值
        preset_config = {k: v for k, v in preset_config.items() if v is not None and v is not False}

        presets.save_preset(args.save_preset, preset_config)
        print(f"✓ Preset '{args.save_preset}' saved!")
        sys.exit(0)

    # 加载预设
    if args.preset:
        preset_config = presets.load_preset(args.preset)
        if preset_config:
            # 应用预设配置
            if 'audio_only' in preset_config:
                args.audio = preset_config['audio_only']
            if 'quality' in preset_config:
                args.quality = preset_config['quality']
            if 'subtitles' in preset_config:
                args.subs = preset_config['subtitles']
            if 'write_thumbnail' in preset_config:
                args.thumbnail = preset_config['write_thumbnail']
            if 'cookies_browser' in preset_config:
                args.cookies = preset_config['cookies_browser']
            if 'smart_format' in preset_config:
                args.smart = preset_config['smart_format']

            if RICH_AVAILABLE:
                from rich.console import Console
                console = Console()
                console.print(f"[green]✓ Using preset: {args.preset}[/green]")
            else:
                print(f"✓ Using preset: {args.preset}")
        else:
            print(f"❌ Preset '{args.preset}' not found")
            print(f"   Use --list-presets to see available presets")
            sys.exit(1)

    # Batch download mode
    if args.batch:
        if not args.batch.exists():
            print(f"❌ Batch file not found: {args.batch}")
            sys.exit(1)

        if RICH_AVAILABLE:
            from rich.console import Console
            from rich.panel import Panel
            console = Console()
            console.print(Panel.fit(
                f"[bold cyan]File:[/bold cyan] {args.batch}\n"
                f"[bold cyan]Audio Only:[/bold cyan] {args.audio}\n"
                f"[bold cyan]Subtitles:[/bold cyan] {args.subs}\n"
                f"[bold cyan]Smart Mode:[/bold cyan] {args.smart}",
                title="[bold green]Batch Download Mode[/bold green]",
                border_style="green"
            ))

            # Read URLs from file
            urls = []
            with open(args.batch) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        urls.append(line)

            console.print(f"\n[bold cyan]Found {len(urls)} URLs to process[/bold cyan]\n")

            # Process each URL
            results = {'success': 0, 'failed': 0, 'skipped': 0}

            for i, url in enumerate(urls, 1):
                console.print(f"[bold cyan][{i}/{len(urls)}] Processing:[/bold cyan] {url[:70]}")

                try:
                    downloader = BingoDownloader(
                        download_path=args.path,
                        audio_only=args.audio,
                        quality=args.quality,
                        subtitles=args.subs,
                        cookies_browser=args.cookies,
                        format_id=args.format_id,
                        list_formats=False,
                        smart_format=args.smart,
                        write_thumbnail=args.thumbnail,
                    )

                    # 尝试下载
                    old_stdout = sys.stdout
                    old_stderr = sys.stderr
                    try:
                        # 重定向输出以避免混乱
                        downloader.download(url)
                        results['success'] += 1
                        console.print("[green]  ✓ Success[/green]\n")
                    except Exception as e:
                        results['failed'] += 1
                        console.print(f"[red]  ✗ Failed: {str(e)[:60]}[/red]\n")
                    finally:
                        sys.stdout = old_stdout
                        sys.stderr = old_stderr

                except Exception as e:
                    results['failed'] += 1
                    console.print(f"[red]  ✗ Error: {str(e)[:60]}[/red]\n")

            # 显示总结
            console.print("\n" + "━" * 50)
            console.print("[bold cyan]Batch Download Summary[/bold cyan]")
            console.print(f"  [green]✓ Success:[/green] {results['success']}")
            console.print(f"  [red]✗ Failed:[/red] {results['failed']}")
            console.print(f"  [yellow]⊘ Skipped:[/yellow] {results['skipped']}")
            console.print(f"  [bold]Total:[/bold] {len(urls)}")
            console.print("━" * 50 + "\n")

            if results['failed'] > 0:
                sys.exit(1)
        else:
            # Terminal without rich
            print(f"\n  📋 Batch Download Mode")
            print(f"  File: {args.batch}")
            print(f"  Audio Only: {args.audio}")
            print(f"  Subtitles: {args.subs}")
            print(f"  Smart Mode: {args.smart}\n")

            # Read URLs from file
            urls = []
            with open(args.batch) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        urls.append(line)

            print(f"  Found {len(urls)} URLs to process\n")

            # Process each URL
            results = {'success': 0, 'failed': 0, 'skipped': 0}

            for i, url in enumerate(urls, 1):
                print(f"  [{i}/{len(urls)}] Processing: {url[:70]}")

                try:
                    downloader = BingoDownloader(
                        download_path=args.path,
                        audio_only=args.audio,
                        quality=args.quality,
                        subtitles=args.subs,
                        cookies_browser=args.cookies,
                        format_id=args.format_id,
                        list_formats=False,
                        smart_format=args.smart,
                        write_thumbnail=args.thumbnail,
                    )

                    downloader.download(url)
                    results['success'] += 1
                    print(f"  ✓ Success\n")

                except Exception as e:
                    results['failed'] += 1
                    print(f"  ✗ Failed: {str(e)[:60]}\n")

            # 显示总结
            print("\n  " + "─" * 50)
            print("  Batch Download Summary")
            print(f"  ✓ Success: {results['success']}")
            print(f"  ✗ Failed: {results['failed']}")
            print(f"  ⊘ Skipped: {results['skipped']}")
            print(f"  Total: {len(urls)}")
            print("  " + "─" * 50 + "\n")

            if results['failed'] > 0:
                sys.exit(1)

        sys.exit(0)

    # Check URL
    if not args.url:
        parser.print_help()
        sys.exit(1)

    # Check dependencies
    missing = []
    if args.audio and not sys.stdout.isatty():
        # For audio extraction, we need ffmpeg
        try:
            import subprocess
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            missing.append('ffmpeg')

    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("\nInstall with:")
        if 'ffmpeg' in missing:
            print("  brew install ffmpeg  # macOS")
            print("  sudo apt install ffmpeg  # Linux")
        sys.exit(1)

    # Create downloader and run
    downloader = BingoDownloader(
        download_path=args.path,
        audio_only=args.audio,
        quality=args.quality,
        subtitles=args.subs,
        cookies_browser=args.cookies,
        format_id=args.format_id,
        list_formats=args.list,
        smart_format=args.smart,
        write_thumbnail=args.thumbnail,
    )

    if args.list:
        downloader.list_available_formats(args.url)
    else:
        downloader.download(args.url, playlist_items=args.playlist_items)


if __name__ == '__main__':
    main()
