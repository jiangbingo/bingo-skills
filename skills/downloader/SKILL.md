---
name: bingo-downloader
description: Download videos from YouTube, Bilibili, Twitter, TikTok and 1000+ sites. Extract audio, download subtitles, quality selection. Features: smart format selection, auto-retry, playlist detection, batch download. Triggers: 下载视频, download video, yt-dlp, YouTube, B站, Bilibili, 抖音, Douyin, 提取音频, extract audio, video downloader, playlist, 智能下载, smart download, 批量下载, batch download.
license: MIT
compatibility: Requires yt-dlp, ffmpeg, Python 3.8+
metadata:
  version: "2.0.0"
  author: jiangbingo
---

# Bingo Video Downloader

A powerful video downloader powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp).

## Quick Start

```bash
# Install dependencies
make check

# Basic download
make download URL="VIDEO_URL"

# YouTube (auto uses cookies)
make download URL="YOUTUBE_URL"

# Extract audio
make audio URL="VIDEO_URL"

# With subtitles
make subs URL="VIDEO_URL"
```

## Quick Reference

| Platform | Special Handling |
|----------|------------------|
| YouTube | Auto uses cookies to avoid 403 errors |
| Bilibili | Works directly |
| Twitter/X | Works directly |
| TikTok/Douyin | Works directly |

## Common Commands

```bash
# Basic download (best quality)
make download URL="VIDEO_URL"

# YouTube with cookies
make cookie-download URL="YOUTUBE_URL"

# Extract audio (MP3)
make audio URL="VIDEO_URL"

# With subtitles
make subs URL="VIDEO_URL"

# Specific quality
make quality URL="VIDEO_URL" Q=720

# List available formats
make list URL="VIDEO_URL"

# Download playlist
make playlist URL="PLAYLIST_URL"

# Smart download (AI-powered)
make smart-download USE_PYTHON=true URL="VIDEO_URL"

# View history
make history

# View statistics
make stats
```

## Installation

```bash
# Clone and install
git clone https://github.com/jiangbingo/bingo-downloader-skill.git
cd bingo-downloader-skill
make install
```

## Workflow

1. Identify platform from URL
2. Ask user what they want (download/audio/subs/quality)
3. Apply platform-specific handling (YouTube → cookies)
4. Execute command
5. Handle errors gracefully

## Quick Troubleshooting

| Error | Fix |
|-------|-----|
| `yt-dlp not found` | `pip install yt-dlp` |
| `ffmpeg not found` | `brew install ffmpeg` |
| `HTTP Error 403` | Use `make cookie-download` |
| `Video unavailable` | Try cookies or check URL |

## More Information

- [Download Guide](references/DOWNLOAD_GUIDE.md) - Detailed command reference
- [Platform Support](references/PLATFORMS.md) - All supported sites
- [Troubleshooting](references/TROUBLESHOOTING.md) - Common issues and solutions
- [Advanced Features](references/ADVANCED.md) - Smart features, batch download, presets
