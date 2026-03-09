# Advanced Features Guide

Advanced capabilities including AI-powered features, batch downloads, and configuration.

## Table of Contents

- [Smart Download (AI-Powered)](#smart-download-ai-powered)
- [Playlist Management](#playlist-management)
- [Download History & Statistics](#download-history--statistics)
- [Configuration Presets](#configuration-presets)
- [Batch Downloads](#batch-downloads)
- [Smart Retry System](#smart-retry-system)
- [Thumbnail Extraction](#thumbnail-extraction)
- [Custom Configuration](#custom-configuration)

---

## Smart Download (AI-Powered)

### Overview

The smart download feature automatically selects the best video format based on:

- **User preference history** - Learns from your past downloads
- **Network conditions** - Adapts to current speed
- **File size optimization** - Balances quality vs size
- **Codec compatibility** - Prioritizes H.264/H.265
- **Frame rate preference** - Prefers 60fps over 30fps

### Usage

```bash
# Using Makefile
make smart-download USE_PYTHON=true URL="VIDEO_URL"

# Using Python script directly
python3 scripts/download.py --smart "VIDEO_URL"
```

### How It Works

1. **Analyzes available formats** from the video
2. **Checks download history** for user preferences
3. **Evaluates network conditions** (speed, stability)
4. **Selects optimal format** balancing:
   - Quality (resolution, bitrate)
   - File size
   - Codec compatibility
   - Your device capabilities

### Example

```bash
$ python3 scripts/download.py --smart "https://www.youtube.com/watch?v=xxx"

🔍 Smart Format Selection Active...
📊 Analyzing 45 available formats...
🧠 Based on your history, you prefer 1080p @ 60fps
📈 Network: Excellent (50 Mbps)
✅ Selected: 1080p60 (H.264) + 320kbps audio
📁 File: Rick Astley - Never Gonna Give You Up [1080p60].mp4
📊 Size: ~125 MB
```

---

## Playlist Management

### Auto-Detection

The script automatically detects playlist URLs and offers interactive options:

```bash
$ make playlist URL="https://www.youtube.com/playlist?list=xxx"

🎵 Playlist Detected: "My Favorite Music"
📊 25 videos found

What would you like to do?
1. Download all videos (25)
2. Specify range (e.g., 1-5, 8, 10-15)
3. Cancel

Enter choice: 2
Enter range: 1-5,10-12

✅ Downloading 7 videos: 1, 2, 3, 4, 5, 10, 11, 12
```

### Playlist Range Syntax

```bash
# Single items
1,5,10

# Ranges
1-5
10-15

# Mixed
1-3,7,10-12,15

# From X to end
5-

# Up to X
-5
```

### Playlist Output Template

Organize downloads in folders:

```bash
# Create playlist folder with numbered videos
yt-dlp -o "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s" "PLAYLIST_URL"

# Result:
# My Favorite Music/
# ├── 01 - Song One.mp4
# ├── 02 - Song Two.mp4
# └── 03 - Song Three.mp4
```

---

## Download History & Statistics

### View History

All downloads are tracked in `~/.yt-dlp-downloads.json`:

```bash
# Using Makefile
make history

# Using Python script
python3 scripts/download.py --history
```

**Example output:**
```
📊 Download History (recent 10)

1. Rick Astley - Never Gonna Give You Up
   URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
   Platform: YouTube
   Quality: 1080p60
   Size: 125 MB
   Date: 2024-01-30 14:32:15 ✓

2. Amazing Bilibili Video
   URL: https://www.bilibili.com/video/BV1xx411c7mD
   Platform: Bilibili
   Quality: 720p
   Size: 89 MB
   Date: 2024-01-30 13:15:42 ✓
```

### View Statistics

```bash
# Using Makefile
make stats

# Using Python script
python3 scripts/download.py --stats
```

**Example output:**
```
📈 Download Statistics

Total Downloads: 156
Successful: 148 ✓
Failed: 8 ✗
Success Rate: 94.9%

Total Data Downloaded: 18.7 GB

Platform Breakdown:
├─ YouTube: 98 (62.8%)
├─ Bilibili: 32 (20.5%)
├─ Twitter: 18 (11.5%)
└─ TikTok: 8 (5.1%)
```

### Filter by Platform

```bash
# YouTube only
python3 scripts/download.py --history --platform YouTube

# Bilibili only
python3 scripts/download.py --stats --platform Bilibili
```

---

## Configuration Presets

### Built-in Presets

```bash
# List all presets
make presets

python3 scripts/download.py --list-presets
```

**Available presets:**

| Preset | Description |
|--------|-------------|
| `high-quality` | 1080p with subtitles and thumbnail |
| `fast` | 720p quick download |
| `audio-only` | High-quality MP3 extraction |
| `best` | Best quality available (no limit) |

### Using Presets

```bash
# Using Makefile
make download URL="VIDEO_URL" PRESET=high-quality

# Using Python script
python3 scripts/download.py --preset high-quality "VIDEO_URL"
```

### Custom Presets

Save your own preset configurations:

```bash
# Create preset with multiple options
python3 scripts/download.py --save-preset my-premium --audio --subs --thumbnail --quality 1080

# Use your preset
python3 scripts/download.py --preset my-premium "VIDEO_URL"

# List all presets (including custom)
python3 scripts/download.py --list-presets
```

### Preset Configuration File

Presets are stored in `~/.yt-dlp-presets.json`:

```json
{
  "high-quality": {
    "quality": "1080",
    "audio": false,
    "subs": true,
    "thumbnail": true
  },
  "my-premium": {
    "quality": "1080",
    "audio": true,
    "subs": true,
    "thumbnail": true
  }
}
```

---

## Batch Downloads

### Prepare URL List

Create a text file with URLs (one per line):

```bash
# url_list.txt
# My download list

https://www.youtube.com/watch?v=xxx1
https://www.youtube.com/watch?v=xxx2
https://www.bilibili.com/video/BV1xx

# Comments start with #
```

### Execute Batch Download

```bash
# Using Makefile
make batch-download FILE=url_list.txt

# Using Python script
python3 scripts/download.py --batch url_list.txt
```

**Example output:**
```
📦 Batch Download: 3 URLs

[1/3] https://www.youtube.com/watch?v=xxx1
✅ Success: Video One.mp4 (125 MB)

[2/3] https://www.youtube.com/watch?v=xxx2
✅ Success: Video Two.mp4 (89 MB)

[3/3] https://www.bilibili.com/video/BV1xx
❌ Failed: HTTP Error 403

📊 Summary: 2 successful, 1 failed
```

### Batch with Preset

```bash
# Apply preset to all URLs in batch
python3 scripts/download.py --batch url_list.txt --preset high-quality
```

---

## Smart Retry System

### Overview

Network failures are automatically retried with exponential backoff:

- **Up to 3 attempts** (configurable)
- **Exponential backoff:** 5s → 10s → 20s
- **Retryable errors detected:** 429, 503, 502, timeout
- **Clear progress indication**

### Retryable Errors

| Error Code | Retryable | Backoff |
|------------|-----------|---------|
| 429 (Too Many Requests) | ✅ Yes | 5s → 10s → 20s |
| 503 (Service Unavailable) | ✅ Yes | 5s → 10s → 20s |
| 502 (Bad Gateway) | ✅ Yes | 5s → 10s → 20s |
| Connection Timeout | ✅ Yes | 5s → 10s → 20s |
| 403 (Forbidden) | ❌ No | Use cookies |
| 404 (Not Found) | ❌ No | Video unavailable |

### Example

```
⬇️  Downloading... [45%]
⚠️  HTTP Error 429 - Retrying in 5 seconds... (Attempt 1/3)
⬇️  Downloading... [45%]
⚠️  HTTP Error 429 - Retrying in 10 seconds... (Attempt 2/3)
⬇️  Downloading... [45%]
✅ Success!
```

### Configure Retry Settings

Edit `scripts/download.py`:

```python
MAX_RETRIES = 3  # Maximum retry attempts
RETRY_DELAYS = [5, 10, 20]  # Backoff in seconds
```

---

## Thumbnail Extraction

### Download Thumbnail

```bash
# Separate thumbnail file
yt-dlp --write-thumbnail --skip-download "VIDEO_URL"

# Download video + thumbnail
yt-dlp --write-thumbnail "VIDEO_URL"
```

### Embed Thumbnail

```bash
# Embed in video file (requires ffmpeg)
yt-dlp --write-thumbnail --embed-thumbnail "VIDEO_URL"

# Using script
scripts/download.sh --write-thumbnail --embed-thumbnail "VIDEO_URL"
```

### Thumbnail Formats

Thumbnails are downloaded in the original format (usually webp or jpg).

---

## Custom Configuration

### Configuration File

Create `~/.yt-dlp.conf` for default settings:

```ini
# Output settings
-o ~/Videos/%(title)s.%(ext)s

# Format selection
-f bestvideo+bestaudio

# Subtitle settings
--sub-langs en,zh-Hans
--embed-subs

# Thumbnail settings
--write-thumbnail
--embed-thumbnail

# Cookies (for YouTube)
--cookies-from-browser chrome

# Performance
--concurrent-fragments 4

# Metadata
--embed-metadata
```

### Environment Variables

```bash
# Set default download path
export DOWNLOAD_PATH="~/Videos"

# Set default quality
export DEFAULT_QUALITY="1080"

# Set cookies browser
export COOKIES_BROWSER="chrome"
```

### Script Configuration

Create `~/.yt-dlp-script-config.json`:

```json
{
  "downloadPath": "~/Videos",
  "defaultQuality": "1080",
  "cookiesBrowser": "chrome",
  "maxRetries": 3,
  "enableHistory": true,
  "enableStats": true
}
```

---

## Advanced yt-dlp Options

### Concurrent Fragment Downloads

Speed up large downloads:

```bash
# Download 4 fragments concurrently
yt-dlp --concurrent-fragments 4 "VIDEO_URL"

# Even faster (more CPU usage)
yt-dlp --concurrent-fragments 8 "VIDEO_URL"
```

### External Downloader

Use external downloaders for better speed:

```bash
# Use aria2
yt-dlp --external-downloader aria2 --concurrent-fragments 4 "VIDEO_URL"

# Use wget
yt-dlp --external-downloader wget "VIDEO_URL"
```

### Split Video by Chapters

```bash
# Download each chapter as separate file
yt-dlp --split-chapters "VIDEO_URL"
```

### Metadata Embedding

```bash
# Embed all metadata
yt-dlp --embed-metadata "VIDEO_URL"

# Embed metadata from internet
yt-dlp --embed-info-json "VIDEO_URL"
```

---

## Performance Tips

1. **Keep yt-dlp updated:**
   ```bash
   pip install -U yt-dlp
   ```

2. **Use appropriate quality:**
   - 720p for most content (good balance)
   - 1080p for high-quality content
   - 4K only when necessary (large files)

3. **Enable concurrent fragments:**
   ```bash
   yt-dlp --concurrent-fragments 4 "VIDEO_URL"
   ```

4. **Use cookies for YouTube:**
   ```bash
   make cookie-download URL="YOUTUBE_URL"
   ```

5. **Download during off-peak hours:**
   - Faster speeds
   - Less rate limiting

---

## See Also

- [Download Command Guide](DOWNLOAD_GUIDE.md) - Basic commands
- [Platform Support](PLATFORMS.md) - All supported sites
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues
