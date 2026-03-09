/**
 * Unit tests for Bingo Downloader MCP Server
 *
 * Tests for downloader.ts functionality:
 * - URL validation
 * - Platform detection
 * - Error handling
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

// Mock child_process before importing downloader
const mockSpawn = vi.fn();
vi.mock('child_process', () => ({
  spawn: (...args: any[]) => mockSpawn(...args),
}));

// Import after mocking
import {
  downloadVideo,
  extractAudio,
  downloadWithSubs,
  listFormats,
} from './downloader';

describe('Platform Detection', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should detect YouTube URLs', async () => {
    // Setup mock for successful download
    mockSpawn.mockReturnValue({
      stdout: { on: vi.fn(), pipe: vi.fn() },
      stderr: { on: vi.fn() },
      on: vi.fn((event, callback) => {
        if (event === 'close') callback(0);
      }),
    });

    const testUrls = [
      'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
      'https://youtu.be/dQw4w9WgXcQ',
      'https://youtube.com/shorts/dQw4w9WgXcQ',
    ];

    for (const url of testUrls) {
      const result = await downloadVideo(url);
      expect(result.platform).toBe('YouTube');
    }
  });

  it('should detect Bilibili URLs', async () => {
    mockSpawn.mockReturnValue({
      stdout: { on: vi.fn(), pipe: vi.fn() },
      stderr: { on: vi.fn() },
      on: vi.fn((event, callback) => {
        if (event === 'close') callback(0);
      }),
    });

    const testUrls = [
      'https://www.bilibili.com/video/BV1xx411c7mD',
      'https://bilibili.com/video/BV1xx411c7mD',
    ];

    for (const url of testUrls) {
      const result = await downloadVideo(url);
      expect(result.platform).toBe('Bilibili');
    }
  });

  it('should detect Twitter/X URLs', async () => {
    mockSpawn.mockReturnValue({
      stdout: { on: vi.fn(), pipe: vi.fn() },
      stderr: { on: vi.fn() },
      on: vi.fn((event, callback) => {
        if (event === 'close') callback(0);
      }),
    });

    const testUrls = [
      'https://twitter.com/user/status/123456',
      'https://x.com/user/status/123456',
    ];

    for (const url of testUrls) {
      const result = await downloadVideo(url);
      expect(result.platform).toBe('Twitter/X');
    }
  });

  it('should detect TikTok/Douyin URLs', async () => {
    mockSpawn.mockReturnValue({
      stdout: { on: vi.fn(), pipe: vi.fn() },
      stderr: { on: vi.fn() },
      on: vi.fn((event, callback) => {
        if (event === 'close') callback(0);
      }),
    });

    const testUrls = [
      'https://www.tiktok.com/@user/video/123456',
      'https://www.douyin.com/video/123456',
    ];

    for (const url of testUrls) {
      const result = await downloadVideo(url);
      expect(result.platform).toBe('TikTok/Douyin');
    }
  });

  it('should detect Vimeo URLs', async () => {
    mockSpawn.mockReturnValue({
      stdout: { on: vi.fn(), pipe: vi.fn() },
      stderr: { on: vi.fn() },
      on: vi.fn((event, callback) => {
        if (event === 'close') callback(0);
      }),
    });

    const result = await downloadVideo('https://vimeo.com/123456789');
    expect(result.platform).toBe('Vimeo');
  });

  it('should return Unknown for unrecognized URLs', async () => {
    mockSpawn.mockReturnValue({
      stdout: { on: vi.fn(), pipe: vi.fn() },
      stderr: { on: vi.fn() },
      on: vi.fn((event, callback) => {
        if (event === 'close') callback(0);
      }),
    });

    const result = await downloadVideo('https://example.com/video/123');
    expect(result.platform).toBe('Unknown');
  });
});

describe('URL Validation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should reject empty URLs', async () => {
    const result = await downloadVideo('');
    expect(result.success).toBe(false);
    expect(result.error).toBeDefined();
  });

  it('should reject URLs with dangerous characters', async () => {
    const dangerousUrls = [
      'https://youtube.com/watch?v=test;rm -rf /',
      'https://youtube.com/watch?v=test&malicious=true',
      'https://youtube.com/watch?v=test`whoami`',
      'https://youtube.com/watch?v=test$(evil)',
    ];

    for (const url of dangerousUrls) {
      const result = await downloadVideo(url);
      expect(result.success).toBe(false);
      expect(result.error).toContain('dangerous character');
    }
  });

  it('should reject non-HTTP protocols', async () => {
    const invalidUrls = [
      'javascript:alert(1)',
      'file:///etc/passwd',
      'ftp://example.com/file',
    ];

    for (const url of invalidUrls) {
      const result = await downloadVideo(url);
      expect(result.success).toBe(false);
    }
  });

  it('should accept valid HTTP/HTTPS URLs', async () => {
    mockSpawn.mockReturnValue({
      stdout: { on: vi.fn(), pipe: vi.fn() },
      stderr: { on: vi.fn() },
      on: vi.fn((event, callback) => {
        if (event === 'close') callback(0);
      }),
    });

    const validUrls = [
      'https://www.youtube.com/watch?v=test',
      'http://youtu.be/test',
    ];

    for (const url of validUrls) {
      const result = await downloadVideo(url);
      expect(result.success).toBe(true);
    }
  });
});

describe('Path Validation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should use default download path when not specified', async () => {
    mockSpawn.mockImplementation((cmd, args) => {
      // Check if default path is used
      const argsStr = args.join(' ');
      expect(argsStr).toContain('~/Downloads');

      return {
        stdout: { on: vi.fn(), pipe: vi.fn() },
        stderr: { on: vi.fn() },
        on: vi.fn((event, callback) => {
          if (event === 'close') callback(0);
        }),
      };
    });

    await downloadVideo('https://www.youtube.com/watch?v=test', 'best', 'chrome');
  });

  it('should use custom download path when specified', async () => {
    const customPath = '/tmp/custom-downloads';

    mockSpawn.mockImplementation((cmd, args) => {
      // Check if custom path is used
      const argsStr = args.join(' ');
      expect(argsStr).toContain(customPath);

      return {
        stdout: { on: vi.fn(), pipe: vi.fn() },
        stderr: { on: vi.fn() },
        on: vi.fn((event, callback) => {
          if (event === 'close') callback(0);
        }),
      };
    });

    await downloadVideo('https://www.youtube.com/watch?v=test', 'best', 'chrome', customPath);
  });
});

describe('Quality Selection', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should select correct format for 1080p quality', async () => {
    mockSpawn.mockImplementation((cmd, args) => {
      const argsStr = args.join(' ');
      expect(argsStr).toContain('1080');

      return {
        stdout: { on: vi.fn(), pipe: vi.fn() },
        stderr: { on: vi.fn() },
        on: vi.fn((event, callback) => {
          if (event === 'close') callback(0);
        }),
      };
    });

    await downloadVideo('https://www.youtube.com/watch?v=test', '1080', 'chrome');
  });

  it('should select correct format for 720p quality', async () => {
    mockSpawn.mockImplementation((cmd, args) => {
      const argsStr = args.join(' ');
      expect(argsStr).toContain('720');

      return {
        stdout: { on: vi.fn(), pipe: vi.fn() },
        stderr: { on: vi.fn() },
        on: vi.fn((event, callback) => {
          if (event === 'close') callback(0);
        }),
      };
    });

    await downloadVideo('https://www.youtube.com/watch?v=test', '720', 'chrome');
  });
});

describe('Audio Extraction', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should extract audio with correct format', async () => {
    mockSpawn.mockReturnValue({
      stdout: { on: vi.fn(), pipe: vi.fn() },
      stderr: { on: vi.fn() },
      on: vi.fn((event, callback) => {
        if (event === 'close') callback(0);
      }),
    });

    const result = await extractAudio('https://www.youtube.com/watch?v=test', 'mp3', 'best', 'chrome');
    expect(result.success).toBe(true);
    expect(result.format).toBe('mp3');
  });

  it('should extract audio with different formats', async () => {
    const formats = ['mp3', 'm4a', 'wav', 'flac'];

    for (const format of formats) {
      mockSpawn.mockReturnValue({
        stdout: { on: vi.fn(), pipe: vi.fn() },
        stderr: { on: vi.fn() },
        on: vi.fn((event, callback) => {
          if (event === 'close') callback(0);
        }),
      });

      const result = await extractAudio('https://www.youtube.com/watch?v=test', format, 'best', 'chrome');
      expect(result.success).toBe(true);
      expect(result.format).toBe(format);
    }
  });
});

describe('Subtitle Download', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should download with subtitles enabled', async () => {
    mockSpawn.mockImplementation((cmd, args) => {
      const argsStr = args.join(' ');
      expect(argsStr).toContain('--write-subs');
      expect(argsStr).toContain('--embed-subs');

      return {
        stdout: { on: vi.fn(), pipe: vi.fn() },
        stderr: { on: vi.fn() },
        on: vi.fn((event, callback) => {
          if (event === 'close') callback(0);
        }),
      };
    });

    const result = await downloadWithSubs('https://www.youtube.com/watch?v=test', '1080', 'all', 'chrome');
    expect(result.success).toBe(true);
    expect(result.subtitles).toBeDefined();
  });

  it('should handle custom subtitle languages', async () => {
    mockSpawn.mockImplementation((cmd, args) => {
      const argsStr = args.join(' ');
      expect(argsStr).toContain('en,zh');

      return {
        stdout: { on: vi.fn(), pipe: vi.fn() },
        stderr: { on: vi.fn() },
        on: vi.fn((event, callback) => {
          if (event === 'close') callback(0);
        }),
      };
    });

    await downloadWithSubs('https://www.youtube.com/watch?v=test', '1080', 'en,zh', 'chrome');
  });
});

describe('Format Listing', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should list available formats', async () => {
    mockSpawn.mockReturnValue({
      stdout: { on: vi.fn(), pipe: vi.fn() },
      stderr: { on: vi.fn() },
      on: vi.fn((event, callback) => {
        if (event === 'close') callback(0);
      }),
    });

    const result = await listFormats('https://www.youtube.com/watch?v=test', 'chrome');
    expect(result.success).toBe(true);
    expect(result.formats).toBeDefined();
  });
});

describe('Cookie Handling', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should use default chrome cookies', async () => {
    mockSpawn.mockImplementation((cmd, args) => {
      const argsStr = args.join(' ');
      expect(argsStr).toContain('--cookies-from-browser');
      expect(argsStr).toContain('chrome');

      return {
        stdout: { on: vi.fn(), pipe: vi.fn() },
        stderr: { on: vi.fn() },
        on: vi.fn((event, callback) => {
          if (event === 'close') callback(0);
        }),
      };
    });

    await downloadVideo('https://www.youtube.com/watch?v=test', 'best', 'chrome');
  });

  it('should use different browser cookies', async () => {
    mockSpawn.mockImplementation((cmd, args) => {
      const argsStr = args.join(' ');
      expect(argsStr).toContain('firefox');

      return {
        stdout: { on: vi.fn(), pipe: vi.fn() },
        stderr: { on: vi.fn() },
        on: vi.fn((event, callback) => {
          if (event === 'close') callback(0);
        }),
      };
    });

    await downloadVideo('https://www.youtube.com/watch?v=test', 'best', 'firefox');
  });
});
