# Platform Support Guide

Complete list of supported sites and platform-specific notes.

## Quick Overview

yt-dlp supports **1000+ websites**. This guide covers the most popular platforms and their specific handling.

---

## Major Video Platforms

### YouTube

**URL Patterns:**
- `youtube.com/watch?v=*`
- `youtu.be/*`
- `youtube.com/shorts/*`
- `youtube.com/playlist?list=*`

**Special Notes:**
- ⚠️ **Always use cookies** to avoid 403 Forbidden errors
- Supports 4K, 8K resolutions
- Live streams supported
- Premium content may require authentication

**Best Practice:**
```bash
make cookie-download URL="YOUTUBE_URL"
```

### YouTube Music

**URL Patterns:**
- `music.youtube.com/watch?v=*`

**Notes:**
- Requires cookies for most content
- Audio-only recommended

### Bilibili (B站)

**URL Patterns:**
- `bilibili.com/video/BV*`
- `bilibili.com/video/av*`

**Special Notes:**
- Most content works without cookies
- Some restricted content requires cookies
- Supports high-quality downloads

**Best Practice:**
```bash
make download URL="BILIBILI_URL"
# If restricted:
make cookie-download URL="BILIBILI_URL"
```

### Vimeo

**URL Patterns:**
- `vimeo.com/*`

**Notes:**
- Works directly
- Some private videos require authentication

---

## Social Media Platforms

### Twitter/X

**URL Patterns:**
- `twitter.com/*/status/*`
- `x.com/*/status/*`

**Special Notes:**
- Works directly without cookies
- Supports GIFs and videos
- Limited quality options

### TikTok / Douyin

**URL Patterns:**
- `tiktok.com/@*/video/*`
- `douyin.com/video/*`

**Special Notes:**
- TikTok: Works directly
- Douyin: May require cookies for some content
- Watermarked and non-watermarked options available

### Facebook

**URL Patterns:**
- `facebook.com/*/videos/*`
- `fb.watch/*`

**Notes:**
- Private videos require authentication
- Public videos work directly

### Instagram

**URL Patterns:**
- `instagram.com/p/*` (Posts)
- `instagram.com/reel/*` (Reels)
- `instagram.com/tv/*` (IGTV)

**Notes:**
- Requires cookies for most content
- Quality limited by platform

### Reddit

**URL Patterns:**
- `reddit.com/r/*/comments/*`

**Notes:**
- Supports Reddit-hosted videos
- Supports external video links

---

## Live Streaming Platforms

### Twitch

**URL Patterns:**
- `twitch.tv/videos/*` (VODs)
- `twitch.tv/*/clip/*` (Clips)

**Special Notes:**
- VODs: Requires authentication for most content
- Clips: Work directly
- Live streams: Requires authentication

**Best Practice:**
```bash
# For VODs
make cookie-download URL="TWITCH_VOD_URL"
```

### YouTube Live

**URL Patterns:**
- `youtube.com/watch?v=*` (live streams)

**Notes:**
- Requires cookies for most live streams
- Live recording may be available after stream ends

---

## Chinese Platforms

### Youku (优酷)

**URL Patterns:**
- `v.youku.com/v_show/*`

**Notes:**
- Some content requires cookies
- Quality options limited

### iQIYI (爱奇艺)

**URL Patterns:**
- `iqiyi.com/v_*`

**Notes:**
- Premium content requires authentication
- Free content works directly

### Tencent Video (腾讯视频)

**URL Patterns:**
- `v.qq.com/x/*`

**Notes:**
- VIP content requires authentication
- Free content limited quality

---

## Other Supported Platforms

### Dailymotion

**URL Patterns:**
- `dailymotion.com/video/*`

### Telegram

**URL Patterns:**
- `t.me/*`

**Notes:**
- Public channels work directly
- Private content requires access

### VK (VKontakte)

**URL Patterns:**
- `vk.com/video*`

**Notes:**
- May require cookies for some content

---

## Platform-Specific Error Handling

| Platform | Common Error | Solution |
|----------|-------------|----------|
| YouTube | 403 Forbidden | Use cookies |
| Bilibili | Region restricted | Use cookies or VPN |
| Twitch | Authentication required | Use cookies with login |
| TikTok | Rate limit | Wait and retry |
| Twitter | GIF format | Download as video |
| Instagram | Private content | Requires authentication |

---

## Regional Restrictions

Some content may be geo-restricted. Solutions:

```bash
# Try with cookies
make cookie-download URL="VIDEO_URL"

# List formats first to see availability
make list URL="VIDEO_URL"
```

---

## Full Supported Sites List

For the complete list of 1000+ supported sites, visit:
[https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

---

## Testing New Platforms

If unsure if a platform is supported:

```bash
# Try to list formats
make list URL="UNKNOWN_PLATFORM_URL"

# If supported, you'll see format options
# If not supported, you'll get "Unsupported URL" error
```
