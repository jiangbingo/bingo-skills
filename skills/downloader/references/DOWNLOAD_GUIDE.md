# Download Command Guide

Complete reference for all download commands and options.

## Table of Contents

- [Basic Downloads](#basic-downloads)
- [Platform-Specific Commands](#platform-specific-commands)
- [Audio Extraction](#audio-extraction)
- [Subtitle Options](#subtitle-options)
- [Quality Selection](#quality-selection)
- [Format Selection](#format-selection)
- [Playlist Downloads](#playlist-downloads)
- [Advanced Options](#advanced-options)

---

## Basic Downloads

### Best Quality Download

```bash
# Using Makefile
make download URL="VIDEO_URL"

# Using script directly
scripts/download.sh "VIDEO_URL"

# Direct yt-dlp
yt-dlp -P "~/Downloads/yt-dlp" "VIDEO_URL"
```

---

## Platform-Specific Commands

### YouTube Downloads

**IMPORTANT:** YouTube requires cookies to avoid 403 Forbidden errors.

```bash
# Makefile (auto-applies cookies for YouTube)
make download URL="https://www.youtube.com/watch?v=xxx"

# Explicit cookies command
make cookie-download URL="https://www.youtube.com/watch?v=xxx"

# Using script with specific browser
scripts/download.sh -c chrome "https://www.youtube.com/watch?v=xxx"

# Direct yt-dlp with cookies
yt-dlp --cookies-from-browser chrome "YOUTUBE_URL"
```

**Supported browsers:** `chrome`, `firefox`, `safari`, `edge`, `brave`, `opera`

### Bilibili Downloads

```bash
# Works directly
make download URL="https://www.bilibili.com/video/BV1xx"

# With cookies (for restricted content)
scripts/download.sh -c chrome "BILIBILI_URL"
```

### Twitter/X Downloads

```bash
# Works directly
make download URL="https://twitter.com/user/status/12345"
```

### TikTok/Douyin Downloads

```bash
# Works directly
make download URL="TIKTOK_URL"
```

---

## Audio Extraction

### MP3 Audio (Best Quality)

```bash
# Using Makefile
make audio URL="VIDEO_URL"

# Using script
scripts/download.sh -a "VIDEO_URL"

# Direct yt-dlp
yt-dlp -P "~/Downloads/yt-dlp" -x --audio-format mp3 "VIDEO_URL"
```

### Other Audio Formats

```bash
# WAV (lossless)
scripts/download.sh -a --audio-format wav "VIDEO_URL"

# M4A (Apple)
scripts/download.sh -a --audio-format m4a "VIDEO_URL"

# FLAC (lossless)
scripts/download.sh -a --audio-format flac "VIDEO_URL"

# AAC
scripts/download.sh -a --audio-format aac "VIDEO_URL"
```

### Audio Quality Selection

```bash
# Best quality (320kbps)
scripts/download.sh -a --audio-quality 0 "VIDEO_URL"

# High quality (256kbps)
scripts/download.sh -a --audio-quality 5 "VIDEO_URL"

# Medium quality (192kbps)
scripts/download.sh -a --audio-quality 5 "VIDEO_URL"
```

---

## Subtitle Options

### Download with Embedded Subtitles

```bash
# Using Makefile
make subs URL="VIDEO_URL"

# Using script
scripts/download.sh -s "VIDEO_URL"

# Direct yt-dlp (all languages, embedded)
yt-dlp -P "~/Downloads/yt-dlp" --write-subs --sub-langs all --embed-subs "VIDEO_URL"
```

### Specific Subtitle Languages

```bash
# English only
scripts/download.sh -s --sub-langs en "VIDEO_URL"

# Chinese and English
scripts/download.sh -s --sub-langs zh-Hans,en "VIDEO_URL"

# Multiple languages
scripts/download.sh -s --sub-langs en,es,fr,de "VIDEO_URL"
```

### Subtitle Formats

```bash
# Download as separate SRT file
yt-dlp --write-subs --sub-langs en --skip-download "VIDEO_URL"

# Auto-generated subtitles (if available)
yt-dlp --write-auto-subs --sub-langs en "VIDEO_URL"
```

---

## Quality Selection

### Common Quality Presets

```bash
# 1080p (Full HD)
make quality URL="VIDEO_URL" Q=1080

# 720p (HD)
make quality URL="VIDEO_URL" Q=720

# 480p (SD)
make quality URL="VIDEO_URL" Q=480

# 360p (Low)
make quality URL="VIDEO_URL" Q=360
```

### Advanced Quality Selection

```bash
# Best video + best audio (merged)
yt-dlp -f "bestvideo+bestaudio" "VIDEO_URL"

# Best video under 1080p + best audio
yt-dlp -f "bestvideo[height<=1080]+bestaudio" "VIDEO_URL"

# Best video under 720p + best audio
yt-dlp -f "bestvideo[height<=720]+bestaudio" "VIDEO_URL"

# Best available (video only)
yt-dlp -f "best" "VIDEO_URL"
```

### Frame Rate Priority

```bash
# Prefer 60fps at 1080p
yt-dlp -f "bestvideo[height<=1080][fps>=60]+bestaudio" "VIDEO_URL"
```

---

## Format Selection

### List Available Formats

```bash
# Using Makefile
make list URL="VIDEO_URL"

# Using script
scripts/download.sh -l "VIDEO_URL"

# Direct yt-dlp
yt-dlp -F "VIDEO_URL"
```

**Output example:**
```
ID  EXT   RESOLUTION | FPS |   FILESIZE   | TBR PROTO | VC INFO
--------------------------------------------------------------
137 mp4   1920x1080  |     | ~ 150.00MiB | 4000k https | dash | video only
248 webm  1920x1080  |     | ~ 120.00MiB | 3000k https | dash | video only
140 m4a   audio only |     |   5.00MiB   |  128k https | dash | audio only
```

### Download Specific Format

```bash
# By format ID (from list)
yt-dlp -f 137+140 "VIDEO_URL"

# By format code
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]" "VIDEO_URL"

# Video only
yt-dlp -f "bestvideo[ext=mp4]" "VIDEO_URL"
```

---

## Playlist Downloads

### Download Entire Playlist

```bash
# Using Makefile
make playlist URL="PLAYLIST_URL"

# Direct yt-dlp with playlist structure
yt-dlp -o "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s" "PLAYLIST_URL"
```

### Download Specific Range

```bash
# Items 1-5
make playlist-range URL="PLAYLIST_URL" RANGE="1-5"

# Items 1, 3, 5-10
scripts/download.py --playlist-items "1,3,5-10" "PLAYLIST_URL"

# Direct yt-dlp
yt-dlp -I 1:5 "PLAYLIST_URL"
```

### Playlist Options

```bash
# Reverse order
yt-dlp --playlist-reverse "PLAYLIST_URL"

# Random order
yt-dlp --playlist-random "PLAYLIST_URL"

# Start from index 5
yt-dlp --playlist-start 5 "PLAYLIST_URL"

# Download only 10 items
yt-dlp --playlist-end 10 "PLAYLIST_URL"
```

---

## Advanced Options

### Download with Thumbnail

```bash
# Embedded thumbnail
scripts/download.sh --write-thumbnail "VIDEO_URL"

# Separate thumbnail file
yt-dlp --write-thumbnail --skip-download "VIDEO_URL"
```

### Custom Output Template

```bash
# With title and uploader
yt-dlp -o "%(title)s [%(uploader)s].%(ext)s" "VIDEO_URL"

# With upload date
yt-dlp -o "%(title)s %(upload_date)s.%(ext)s" "VIDEO_URL"

# With video ID
yt-dlp -o "%(title)s [%(id)s].%(ext)s" "VIDEO_URL"
```

### Custom Download Path

```bash
# Using Makefile
make download URL="VIDEO_URL" DOWNLOAD_PATH="~/Videos"

# Direct yt-dlp
yt-dlp -o "~/Videos/%(title)s.%(ext)s" "VIDEO_URL"
```

### Speed Limit

```bash
# Limit to 1MB/s
yt-dlp --limit-rate 1M "VIDEO_URL"

# Limit to 512KB/s
yt-dlp --limit-rate 512K "VIDEO_URL"
```

### Subtitle Embedding

```bash
# Embed subtitles in video file (requires ffmpeg)
yt-dlp --embed-subs --sub-langs en "VIDEO_URL"

# Embed thumbnails (requires ffmpeg)
yt-dlp --embed-thumbnail --write-thumbnail "VIDEO_URL"

# Embed metadata (requires ffmpeg)
yt-dlp --embed-metadata "VIDEO_URL"
```

### Concatenate Videos

```bash
# Download and merge multiple formats
yt-dlp --concat-playlist "PLAYLIST_URL"
```

---

## Configuration File

Create `~/.yt-dlp.conf` for default settings:

```ini
# Default download path
-o ~/Videos/%(title)s.%(ext)s

# Default format
-f bestvideo+bestaudio

# Default subtitle language
--sub-langs en,zh-Hans

# Embed subtitles
--embed-subs

# Write thumbnail
--write-thumbnail --embed-thumbnail

# Cookies browser
--cookies-from-browser chrome
```

---

## Batch Downloads

See [Advanced Features](ADVANCED.md#batch-downloads) for batch download capabilities.
