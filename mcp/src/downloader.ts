import { spawn } from 'child_process';
import * as path from 'path';
import * as os from 'os';
import { createLogger, logDownloadStart, logDownloadSuccess, logDownloadError } from './logger.js';

const logger = createLogger('downloader');

interface DownloadResult {
  success: boolean;
  filePath?: string;
  fileSize?: string;
  duration?: string;
  platform?: string;
  error?: string;
  format?: string;
  quality?: string;
  subtitles?: string;
  formats?: string;
}

/**
 * 验证 URL 是否安全且格式正确
 * 使用严格的 URL 验证，防止命令注入和 SSRF 攻击
 */
function validateUrl(url: string): { valid: boolean; error?: string } {
  try {
    // 基本格式验证
    if (!url || typeof url !== 'string') {
      return { valid: false, error: 'URL must be a non-empty string' };
    }

    // 长度限制
    if (url.length > 2048) {
      return { valid: false, error: 'URL is too long (max 2048 characters)' };
    }

    // 检查危险字符
    const dangerousChars = ['\n', '\r', '\t', '\0', ';', '&', '|', '$', '`', '(', ')', '<', '>'];
    for (const char of dangerousChars) {
      if (url.includes(char)) {
        return { valid: false, error: `URL contains dangerous character: ${char}` };
      }
    }

    // URL 解析和验证
    const parsedUrl = new URL(url);

    // 只允许 HTTP/HTTPS 协议
    if (!['http:', 'https:'].includes(parsedUrl.protocol)) {
      return { valid: false, error: 'Only HTTP and HTTPS protocols are allowed' };
    }

    // 阻止访问本地地址
    const hostname = parsedUrl.hostname.toLowerCase();
    if (hostname === 'localhost' ||
        hostname === '127.0.0.1' ||
        hostname === '[::1]' ||
        hostname.startsWith('192.168.') ||
        hostname.startsWith('10.') ||
        hostname.startsWith('172.16.') ||
        hostname.endsWith('.local')) {
      return { valid: false, error: 'Access to local/private addresses is not allowed' };
    }

    return { valid: true };
  } catch (error) {
    return { valid: false, error: `Invalid URL format: ${error instanceof Error ? error.message : 'Unknown error'}` };
  }
}

/**
 * 验证并规范化下载路径
 * 防止路径遍历攻击，限制在用户主目录内
 */
function validateDownloadPath(downloadPath?: string): { valid: boolean; resolvedPath?: string; error?: string } {
  try {
    // 如果未提供路径，使用默认值
    if (!downloadPath) {
      const defaultPath = path.join(os.homedir(), 'Downloads', 'yt-dlp');
      return { valid: true, resolvedPath: defaultPath };
    }

    // 类型检查
    if (typeof downloadPath !== 'string') {
      return { valid: false, error: 'Download path must be a string' };
    }

    // 检查危险字符
    const dangerousChars = ['\n', '\r', '\t', '\0', ';', '&', '|', '$', '`', '(', ')', '<', '>'];
    for (const char of dangerousChars) {
      if (downloadPath.includes(char)) {
        return { valid: false, error: `Path contains dangerous character: ${char}` };
      }
    }

    // 展开波浪号 (~)
    let expandedPath = downloadPath;
    if (downloadPath.startsWith('~')) {
      expandedPath = path.join(os.homedir(), downloadPath.slice(1));
    }

    // 解析为绝对路径
    const resolvedPath = path.resolve(expandedPath);

    // 获取用户主目录
    const homeDir = os.homedir();

    // 确保路径在用户主目录内
    if (!resolvedPath.startsWith(homeDir)) {
      return { valid: false, error: `Download path must be within user home directory (${homeDir})` };
    }

    // 防止路径遍历
    const relativePath = path.relative(homeDir, resolvedPath);
    if (relativePath.startsWith('..')) {
      return { valid: false, error: 'Path traversal detected: path escapes home directory' };
    }

    return { valid: true, resolvedPath };
  } catch (error) {
    return { valid: false, error: `Path validation error: ${error instanceof Error ? error.message : 'Unknown error'}` };
  }
}

/**
 * 使用 spawn 安全地执行 yt-dlp 命令
 * 通过参数数组而非命令字符串，防止命令注入
 */
async function executeYtDlp(args: string[]): Promise<{ stdout: string; stderr: string }> {
  return new Promise((resolve, reject) => {
    let stdout = '';
    let stderr = '';

    const childProcess = spawn('yt-dlp', args, {
      stdio: ['ignore', 'pipe', 'pipe'] as const,
    });

    if (childProcess.stdout) {
      childProcess.stdout.on('data', (data: Buffer) => {
        stdout += data.toString();
      });
    }

    if (childProcess.stderr) {
      childProcess.stderr.on('data', (data: Buffer) => {
        stderr += data.toString();
      });
    }

    childProcess.on('close', (code: number | null) => {
      if (code === 0) {
        resolve({ stdout, stderr });
      } else {
        reject(new Error(stderr || `Command failed with exit code ${code}`));
      }
    });

    childProcess.on('error', (error: Error) => {
      reject(new Error(`Failed to start yt-dlp: ${error.message}`));
    });
  });
}

// Detect platform from URL
function detectPlatform(url: string): string {
  if (url.includes('youtube.com') || url.includes('youtu.be')) return 'YouTube';
  if (url.includes('bilibili.com')) return 'Bilibili';
  if (url.includes('twitter.com') || url.includes('x.com')) return 'Twitter/X';
  if (url.includes('tiktok.com') || url.includes('douyin.com')) return 'TikTok/Douyin';
  if (url.includes('vimeo.com')) return 'Vimeo';
  if (url.includes('twitch.tv')) return 'Twitch';
  if (url.includes('facebook.com')) return 'Facebook';
  if (url.includes('instagram.com')) return 'Instagram';
  return 'Unknown';
}

// Get quality format string
function getQualityFormat(quality: string): string {
  switch (quality) {
    case '1080':
      return 'bestvideo[height<=1080]+bestaudio/best[height<=1080]';
    case '720':
      return 'bestvideo[height<=720]+bestaudio/best[height<=720]';
    case '480':
      return 'bestvideo[height<=480]+bestaudio/best[height<=480]';
    case '360':
      return 'bestvideo[height<=360]+bestaudio/best[height<=360]';
    default:
      return 'bestvideo+bestaudio/best';
  }
}

/**
 * 构建 yt-dlp 参数数组
 * 返回参数数组而非命令字符串，防止命令注入
 */
function buildArgs(options: {
  url: string;
  format?: string;
  audio?: boolean;
  audioFormat?: string;
  audioQuality?: string;
  subs?: boolean;
  subLangs?: string;
  cookiesBrowser?: string;
  downloadPath?: string;
}): string[] {
  const {
    url,
    format,
    audio = false,
    audioFormat = 'mp3',
    audioQuality = 'best',
    subs = false,
    subLangs = 'all',
    cookiesBrowser = 'chrome',
    downloadPath,
  } = options;

  const args: string[] = [];

  // 验证并添加下载路径
  const pathValidation = validateDownloadPath(downloadPath);
  if (!pathValidation.valid || !pathValidation.resolvedPath) {
    throw new Error(pathValidation.error || 'Invalid download path');
  }
  args.push('-o', path.join(pathValidation.resolvedPath, '%(title)s.%(ext)s'));

  // 添加格式选项
  if (audio) {
    args.push('-x');
    if (audioFormat) {
      args.push('--audio-format', audioFormat);
    }
    if (audioQuality && audioQuality !== 'best') {
      args.push('--audio-quality', audioQuality);
    }
  } else if (format) {
    args.push('-f', format);
  }

  // 添加字幕选项
  if (subs) {
    args.push('--write-subs', '--sub-langs', subLangs, '--embed-subs');
  }

  // 添加 cookies 选项
  if (cookiesBrowser) {
    args.push('--cookies-from-browser', cookiesBrowser);
  }

  // 添加 URL (最后添加)
  args.push(url);

  return args;
}

// Download video
export async function downloadVideo(
  url: string,
  quality: string = 'best',
  cookiesBrowser: string = 'chrome',
  downloadPath?: string
): Promise<DownloadResult> {
  // 验证 URL
  const urlValidation = validateUrl(url);
  if (!urlValidation.valid) {
    return {
      success: false,
      error: urlValidation.error || 'Invalid URL',
    };
  }

  const platform = detectPlatform(url);
  const qualityFormat = getQualityFormat(quality);

  const startTime = Date.now();
  logDownloadStart(url, { platform, quality, cookiesBrowser });

  try {
    const args = buildArgs({
      url,
      format: qualityFormat,
      cookiesBrowser,
      downloadPath,
    });

    const { stdout, stderr } = await executeYtDlp(args);

    logger.debug({ url, platform, stdout: stdout.slice(0, 200) }, 'yt-dlp output received');

    // Parse output to extract file info
    const filePathMatch = stdout.match(/\[download\] Destination: (.+)/);
    const sizeMatch = stdout.match(/\[download\] (\d+\.?\d*% of \d+\.?\d*[A-Z]+)/);

    const duration = (Date.now() - startTime) / 1000;
    logDownloadSuccess(url, filePathMatch ? filePathMatch[1] : 'Download completed', duration);

    return {
      success: true,
      filePath: filePathMatch ? filePathMatch[1] : 'Download completed',
      fileSize: sizeMatch ? sizeMatch[1] : 'Unknown',
      platform,
    };
  } catch (error: any) {
    const duration = (Date.now() - startTime) / 1000;
    logDownloadError(url, error, duration);
    const errorMsg = error.message || 'Unknown error';

    // Check if yt-dlp is installed
    if (errorMsg.includes('command not found') ||
        errorMsg.includes('not recognized') ||
        errorMsg.includes('ENOTSUP') ||
        errorMsg.includes('spawn yt-dlp')) {
      return {
        success: false,
        error: 'yt-dlp is not installed. Install with: pip install yt-dlp',
      };
    }

    return {
      success: false,
      error: errorMsg,
    };
  }
}

// Extract audio
export async function extractAudio(
  url: string,
  format: string = 'mp3',
  quality: string = 'best',
  cookiesBrowser: string = 'chrome'
): Promise<DownloadResult> {
  // 验证 URL
  const urlValidation = validateUrl(url);
  if (!urlValidation.valid) {
    return {
      success: false,
      error: urlValidation.error || 'Invalid URL',
    };
  }

  const platform = detectPlatform(url);
  const startTime = Date.now();
  logger.info({ type: 'audio_extraction_start', url, platform, format, quality }, 'Starting audio extraction');

  try {
    const args = buildArgs({
      url,
      audio: true,
      audioFormat: format,
      audioQuality: quality,
      cookiesBrowser,
    });

    const { stdout, stderr } = await executeYtDlp(args);

    const filePathMatch = stdout.match(/\[download\] Destination: (.+)/);
    const sizeMatch = stdout.match(/\[download\] (\d+\.?\d*% of \d+\.?\d*[A-Z]+)/);

    const duration = (Date.now() - startTime) / 1000;
    logger.info({ type: 'audio_extraction_success', url, filePath: filePathMatch?.[1], format, duration }, 'Audio extraction completed');

    return {
      success: true,
      filePath: filePathMatch ? filePathMatch[1] : 'Extraction completed',
      fileSize: sizeMatch ? sizeMatch[1] : 'Unknown',
      format,
      platform,
    };
  } catch (error: any) {
    const duration = (Date.now() - startTime) / 1000;
    logger.error({ type: 'audio_extraction_error', url, error: error.message, duration }, 'Audio extraction failed');
    const errorMsg = error.message || 'Unknown error';

    // Check for ffmpeg
    if (errorMsg.includes('ffmpeg') || errorMsg.includes('FFmpeg') || errorMsg.includes('Audio conversion')) {
      return {
        success: false,
        error: 'ffmpeg is not installed. Install with: brew install ffmpeg (macOS) or sudo apt install ffmpeg (Linux)',
      };
    }

    return {
      success: false,
      error: errorMsg,
    };
  }
}

// Download with subtitles
export async function downloadWithSubs(
  url: string,
  quality: string = 'best',
  subLangs: string = 'all',
  cookiesBrowser: string = 'chrome'
): Promise<DownloadResult & { subtitles?: string }> {
  // 验证 URL
  const urlValidation = validateUrl(url);
  if (!urlValidation.valid) {
    return {
      success: false,
      error: urlValidation.error || 'Invalid URL',
    };
  }

  const platform = detectPlatform(url);
  const qualityFormat = getQualityFormat(quality);

  try {
    const args = buildArgs({
      url,
      format: qualityFormat,
      subs: true,
      subLangs,
      cookiesBrowser,
    });

    const { stdout, stderr } = await executeYtDlp(args);

    const filePathMatch = stdout.match(/\[download\] Destination: (.+)/);
    const subsMatch = stdout.match(/\[download\] Downloading video subtitles (.+)/);

    return {
      success: true,
      filePath: filePathMatch ? filePathMatch[1] : 'Download completed',
      subtitles: subsMatch ? subsMatch[1] : 'Embedded subtitles',
      quality,
      platform,
    };
  } catch (error: any) {
    return {
      success: false,
      error: error.message || 'Unknown error',
    };
  }
}

// List formats
export async function listFormats(
  url: string,
  cookiesBrowser: string = 'chrome'
): Promise<DownloadResult & { formats?: string }> {
  // 验证 URL
  const urlValidation = validateUrl(url);
  if (!urlValidation.valid) {
    return {
      success: false,
      error: urlValidation.error || 'Invalid URL',
    };
  }

  try {
    // 构建列出格式的参数
    const args = buildArgs({
      url,
      cookiesBrowser,
    });

    // 移除格式选项，添加 -F 列出格式
    const filteredArgs = args.filter(arg => arg !== '-f' && !arg.startsWith('bestvideo') && !arg.startsWith('best['));
    filteredArgs.push('-F');

    const { stdout } = await executeYtDlp(filteredArgs);

    // Parse and format the output
    const lines = stdout.split('\n');
    let formattedFormats = '';

    lines.forEach((line: string) => {
      if (line.match(/^\s*\d+/)) {
        formattedFormats += line + '\n';
      }
    });

    return {
      success: true,
      formats: formattedFormats || stdout,
    };
  } catch (error: any) {
    return {
      success: false,
      error: error.message || 'Unknown error',
    };
  }
}