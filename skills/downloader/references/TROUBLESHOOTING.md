# Troubleshooting Guide

Common issues, errors, and their solutions.

## Quick Reference Table

| Error | Quick Fix |
|-------|-----------|
| `command not found: yt-dlp` | `pip install yt-dlp` |
| `ffmpeg not found` | `brew install ffmpeg` (macOS) or `sudo apt install ffmpeg` (Linux) |
| `HTTP Error 403: Forbidden` | Use `make cookie-download` |
| `Video unavailable` | Try cookies or check URL validity |
| `Requested format not available` | Use `make list` to see available formats |
| `Sign in to confirm you're not a bot` | Use cookies from browser |
| Download slow/interrupted | Just retry - auto-resume enabled |

---

## Installation Issues

### yt-dlp Not Found

**Error:**
```
command not found: yt-dlp
```

**Solutions:**

```bash
# Using pip
pip install yt-dlp

# Using pip3
pip3 install yt-dlp

# Update to latest version
pip install -U yt-dlp
```

**Verify installation:**
```bash
yt-dlp --version
```

### ffmpeg Not Found

**Error:**
```
ffmpeg not found
ERROR: ffprobe/ffmpeg not found
```

**Solutions:**

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

**Verify installation:**
```bash
ffmpeg -version
```

### Python Version Issues

**Error:**
```
SyntaxError or module import errors
```

**Solution:**
- Ensure Python 3.8 or higher
```bash
python3 --version  # Should be 3.8+
```

---

## Download Errors

### HTTP Error 403: Forbidden

**Error:**
```
HTTP Error 403: Forbidden
```

**Cause:** YouTube and some sites block requests without proper authentication.

**Solutions:**

```bash
# Method 1: Use cookies (recommended)
make cookie-download URL="VIDEO_URL"

# Method 2: Specify browser
scripts/download.sh -c chrome "VIDEO_URL"

# Method 3: Try different browser
scripts/download.sh -c firefox "VIDEO_URL"
```

**Supported browsers:** `chrome`, `firefox`, `safari`, `edge`, `brave`, `opera`

### Video Unavailable

**Error:**
```
Video unavailable
This video is not available
```

**Causes:**
- Video deleted by uploader
- Private video
- Geo-restricted content
- Age-restricted content

**Solutions:**

```bash
# Try with cookies
make cookie-download URL="VIDEO_URL"

# Check if video exists in browser first
# List formats to verify availability
make list URL="VIDEO_URL"
```

### Sign In Required

**Error:**
```
Sign in to confirm you're not a bot
```

**Solution:**
```bash
# Use cookies from browser
make cookie-download URL="VIDEO_URL"
```

### Format Not Available

**Error:**
```
Requested format is not available
Requested format not available
```

**Solution:**
```bash
# List available formats first
make list URL="VIDEO_URL"

# Download specific format by ID
scripts/download.sh -f FORMAT_ID "VIDEO_URL"
```

### Connection Timeout

**Error:**
```
Connection timeout
Network unreachable
```

**Solutions:**

```bash
# Just retry - auto-resume is enabled
make download URL="VIDEO_URL"

# The download will continue from where it left off
```

**Note:** The script includes automatic retry with exponential backoff (5s → 10s → 20s).

### Rate Limiting

**Error:**
```
HTTP Error 429: Too Many Requests
```

**Solution:**
```bash
# Wait and retry - automatic retry will handle this
# The script uses exponential backoff for rate limits
```

---

## Quality/Format Issues

### Best Quality Not Available

**Symptom:** Downloaded video is lower quality than expected.

**Solutions:**

```bash
# List available formats
make list URL="VIDEO_URL"

# Check if higher quality exists
# Download specific format
scripts/download.sh -f FORMAT_ID "VIDEO_URL"
```

### Audio Missing from Video

**Error:** Video has no audio after download.

**Cause:** Downloaded video-only format without audio.

**Solution:**
```bash
# Use format that includes both video and audio
make download URL="VIDEO_URL"

# Or specify combined format
yt-dlp -f "bestvideo+bestaudio" "VIDEO_URL"
```

### Subtitles Not Downloading

**Error:** Subtitles not embedded or downloaded.

**Solutions:**

```bash
# Check if subtitles are available
make list URL="VIDEO_URL"

# Try specific language
scripts/download.sh -s --sub-langs en "VIDEO_URL"

# Download as separate file first
yt-dlp --write-subs --sub-langs en --skip-download "VIDEO_URL"
```

---

## Performance Issues

### Slow Download Speed

**Solutions:**

```bash
# Update yt-dlp to latest version
pip install -U yt-dlp

# Try different format (lower quality = faster)
make quality URL="VIDEO_URL" Q=720

# Limit speed if needed
yt-dlp --limit-rate 1M "VIDEO_URL"
```

### High CPU Usage

**Cause:** Video encoding/conversion (merging video+audio).

**Solutions:**

```bash
# Download pre-merged format if available
make list URL="VIDEO_URL"  # Look for formats with both video+audio

# Or be patient - encoding is CPU-intensive by design
```

### Large File Size

**Solutions:**

```bash
# Download lower quality
make quality URL="VIDEO_URL" Q=720

# Extract audio only (much smaller)
make audio URL="VIDEO_URL"
```

---

## Playlist Issues

### Playlist Not Detected

**Symptom:** Only first video downloads.

**Solutions:**

```bash
# Verify it's a playlist URL
make list URL="PLAYLIST_URL"

# Use explicit playlist command
make playlist URL="PLAYLIST_URL"
```

### Too Many Videos in Playlist

**Solutions:**

```bash
# Download specific range
make playlist-range URL="PLAYLIST_URL" RANGE="1-5"

# Download first 10 only
yt-dlp --playlist-end 10 "PLAYLIST_URL"
```

---

## File System Issues

### Permission Denied

**Error:**
```
Permission denied
Cannot write to directory
```

**Solutions:**

```bash
# Check download directory permissions
ls -la ~/Downloads/yt-dlp/

# Specify custom download path
make download URL="VIDEO_URL" DOWNLOAD_PATH="~/Videos"
```

### Disk Space Full

**Error:**
```
No space left on device
```

**Solutions:**

```bash
# Check disk space
df -h

# Clean up old downloads
rm ~/Downloads/yt-dlp/*.mp4

# Use external drive
make download URL="VIDEO_URL" DOWNLOAD_PATH="/Volumes/ExternalDrive/Videos"
```

### Filename Too Long

**Error:**
```
Filename too long
```

**Solution:**
```bash
# Use custom output template
yt-dlp -o "%(title).50s.%(ext)s" "VIDEO_URL"  # Truncate title to 50 chars
```

---

## Platform-Specific Issues

### YouTube Specific

| Issue | Solution |
|-------|----------|
| 403 Forbidden | Use `make cookie-download` |
| Age-restricted | Use cookies with logged-in browser |
| Private video | Need access to the video |
| Live stream | Use cookies, may not work for all streams |

### Bilibili Specific

| Issue | Solution |
|-------|----------|
| Region restricted | Try cookies or VPN |
| Quality limited | May require account/login |

### Twitch Specific

| Issue | Solution |
|-------|----------|
| Authentication required | Use cookies with login |
| Subscriber-only | Need subscription |

---

## Getting Help

If none of the solutions work:

1. **Check yt-dlp version:**
   ```bash
   yt-dlp --version
   pip install -U yt-dlp  # Update if old
   ```

2. **Enable verbose output:**
   ```bash
   yt-dlp -v "VIDEO_URL"
   ```

3. **Check GitHub issues:**
   - [yt-dlp Issues](https://github.com/yt-dlp/yt-dlp/issues)
   - [bingo-downloader Issues](https://github.com/jiangbingo/bingo-downloader-skill/issues)

4. **Provide debugging info:**
   - yt-dlp version
   - Full error message
   - URL (if public)
   - Command used

---

## Log Files

Check logs for more details:

```bash
# View recent download attempts
cat ~/.yt-dlp-download.log

# View download history
make history
```
