#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { downloadVideo, extractAudio, downloadWithSubs, listFormats } from './downloader.js';
import { getHistory, getStats } from './history.js';
import { logger } from './logger.js';

/**
 * 验证 URL 参数的基本安全检查
 */
function validateUrlInput(url: any): { valid: boolean; error?: string } {
  if (!url || typeof url !== 'string') {
    return { valid: false, error: 'URL parameter is required and must be a string' };
  }

  if (url.trim().length === 0) {
    return { valid: false, error: 'URL cannot be empty' };
  }

  if (url.length > 2048) {
    return { valid: false, error: 'URL exceeds maximum length of 2048 characters' };
  }

  return { valid: true };
}

/**
 * 验证路径参数的基本安全检查
 */
function validatePathInput(path: any): { valid: boolean; error?: string } {
  if (path && typeof path !== 'string') {
    return { valid: false, error: 'Path parameter must be a string' };
  }

  if (path && path.length > 512) {
    return { valid: false, error: 'Path exceeds maximum length of 512 characters' };
  }

  return { valid: true };
}

// Create MCP Server
const server = new Server(
  {
    name: 'bingo-downloader',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Register available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'download_video',
        description: 'Download video from URL. Supports YouTube, Bilibili, Twitter, TikTok and 1000+ other sites.',
        inputSchema: {
          type: 'object',
          properties: {
            url: {
              type: 'string',
              description: 'Video URL to download',
            },
            quality: {
              type: 'string',
              description: 'Video quality preference',
              enum: ['best', '1080', '720', '480', '360'],
              default: 'best',
            },
            cookies_browser: {
              type: 'string',
              description: 'Browser to extract cookies from (helps with 403 errors on YouTube)',
              enum: ['chrome', 'firefox', 'safari', 'edge', 'brave', 'opera'],
              default: 'chrome',
            },
            download_path: {
              type: 'string',
              description: 'Custom download path (optional, defaults to ~/Downloads/yt-dlp)',
            },
          },
          required: ['url'],
        },
      },
      {
        name: 'extract_audio',
        description: 'Extract audio from video and convert to MP3/WAV/M4A',
        inputSchema: {
          type: 'object',
          properties: {
            url: {
              type: 'string',
              description: 'Video URL',
            },
            format: {
              type: 'string',
              description: 'Audio format',
              enum: ['mp3', 'wav', 'm4a', 'flac', 'aac'],
              default: 'mp3',
            },
            quality: {
              type: 'string',
              description: 'Audio quality',
              enum: ['best', '320', '256', '192', '128'],
              default: 'best',
            },
            cookies_browser: {
              type: 'string',
              description: 'Browser for cookies',
              enum: ['chrome', 'firefox', 'safari', 'edge', 'brave', 'opera'],
              default: 'chrome',
            },
          },
          required: ['url'],
        },
      },
      {
        name: 'download_with_subs',
        description: 'Download video with subtitles embedded',
        inputSchema: {
          type: 'object',
          properties: {
            url: {
              type: 'string',
              description: 'Video URL',
            },
            quality: {
              type: 'string',
              description: 'Video quality',
              enum: ['best', '1080', '720', '480'],
              default: 'best',
            },
            sub_langs: {
              type: 'string',
              description: 'Subtitle languages (comma-separated, e.g., "en,zh,ja")',
              default: 'all',
            },
            cookies_browser: {
              type: 'string',
              description: 'Browser for cookies',
              enum: ['chrome', 'firefox', 'safari', 'edge', 'brave', 'opera'],
              default: 'chrome',
            },
          },
          required: ['url'],
        },
      },
      {
        name: 'list_formats',
        description: 'List all available video and audio formats for a given URL',
        inputSchema: {
          type: 'object',
          properties: {
            url: {
              type: 'string',
              description: 'Video URL',
            },
            cookies_browser: {
              type: 'string',
              description: 'Browser for cookies (needed for some sites)',
              enum: ['chrome', 'firefox', 'safari', 'edge', 'brave', 'opera'],
              default: 'chrome',
            },
          },
          required: ['url'],
        },
      },
      {
        name: 'get_history',
        description: 'Get download history from local database',
        inputSchema: {
          type: 'object',
          properties: {
            limit: {
              type: 'number',
              description: 'Number of recent downloads to show',
              default: 20,
              minimum: 1,
              maximum: 100,
            },
            platform: {
              type: 'string',
              description: 'Filter by platform (YouTube, Bilibili, etc.)',
            },
          },
        },
      },
      {
        name: 'get_stats',
        description: 'Get download statistics (total downloads, success rate, etc.)',
        inputSchema: {
          type: 'object',
          properties: {
            platform: {
              type: 'string',
              description: 'Filter by platform',
            },
          },
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'download_video': {
        // 输入验证
        const urlValidation = validateUrlInput(args?.url);
        if (!urlValidation.valid) {
          return {
            content: [
              {
                type: 'text',
                text: `Validation error: ${urlValidation.error}`,
              },
            ],
            isError: true,
          };
        }

        const pathValidation = validatePathInput(args?.download_path);
        if (!pathValidation.valid) {
          return {
            content: [
              {
                type: 'text',
                text: `Validation error: ${pathValidation.error}`,
              },
            ],
            isError: true,
          };
        }

        const result = await downloadVideo(
          args?.url as string,
          args?.quality as string,
          args?.cookies_browser as string,
          args?.download_path as string
        );
        return {
          content: [
            {
              type: 'text',
              text: result.success
                ? `✓ Download completed!\n\nFile: ${result.filePath}\nSize: ${result.fileSize}\nDuration: ${result.duration}\nPlatform: ${result.platform}`
                : `✗ Download failed: ${result.error}`,
            },
          ],
          isError: !result.success,
        };
      }

      case 'extract_audio': {
        // 输入验证
        const urlValidation = validateUrlInput(args?.url);
        if (!urlValidation.valid) {
          return {
            content: [
              {
                type: 'text',
                text: `Validation error: ${urlValidation.error}`,
              },
            ],
            isError: true,
          };
        }

        const result = await extractAudio(
          args?.url as string,
          args?.format as string,
          args?.quality as string,
          args?.cookies_browser as string
        );
        return {
          content: [
            {
              type: 'text',
              text: result.success
                ? `✓ Audio extraction completed!\n\nFile: ${result.filePath}\nFormat: ${result.format}\nSize: ${result.fileSize}`
                : `✗ Extraction failed: ${result.error}`,
            },
          ],
          isError: !result.success,
        };
      }

      case 'download_with_subs': {
        // 输入验证
        const urlValidation = validateUrlInput(args?.url);
        if (!urlValidation.valid) {
          return {
            content: [
              {
                type: 'text',
                text: `Validation error: ${urlValidation.error}`,
              },
            ],
            isError: true,
          };
        }

        const result = await downloadWithSubs(
          args?.url as string,
          args?.quality as string,
          args?.sub_langs as string,
          args?.cookies_browser as string
        );
        return {
          content: [
            {
              type: 'text',
              text: result.success
                ? `✓ Download with subtitles completed!\n\nFile: ${result.filePath}\nSubtitles: ${result.subtitles}\nQuality: ${result.quality}`
                : `✗ Download failed: ${result.error}`,
            },
          ],
          isError: !result.success,
        };
      }

      case 'list_formats': {
        // 输入验证
        const urlValidation = validateUrlInput(args?.url);
        if (!urlValidation.valid) {
          return {
            content: [
              {
                type: 'text',
                text: `Validation error: ${urlValidation.error}`,
              },
            ],
            isError: true,
          };
        }

        const result = await listFormats(args?.url as string, args?.cookies_browser as string);
        return {
          content: [
            {
              type: 'text',
              text: result.success
                ? `Available formats:\n\n${result.formats}`
                : `✗ Failed to list formats: ${result.error}`,
            },
          ],
          isError: !result.success,
        };
      }

      case 'get_history': {
        const history = await getHistory(args?.limit as number, args?.platform as string);
        if (history.length === 0) {
          return {
            content: [
              {
                type: 'text',
                text: 'No download history found. Start downloading to build history!',
              },
            ],
          };
        }
        let historyText = '📊 Download History\n\n';
        history.forEach((item, index) => {
          historyText += `${index + 1}. ${item.title}\n`;
          historyText += `   URL: ${item.url}\n`;
          historyText += `   Platform: ${item.platform}\n`;
          historyText += `   Status: ${item.success ? '✓' : '✗'}\n`;
          historyText += `   Date: ${new Date(item.timestamp).toLocaleString()}\n\n`;
        });
        return {
          content: [{ type: 'text', text: historyText }],
        };
      }

      case 'get_stats': {
        const stats = await getStats(args?.platform as string);
        const successRate = stats.total > 0 ? ((stats.successful / stats.total) * 100).toFixed(1) : '0';
        let statsText = `📈 Download Statistics\n\n`;
        statsText += `Total Downloads: ${stats.total}\n`;
        statsText += `Successful: ${stats.successful} ✓\n`;
        statsText += `Failed: ${stats.failed} ✗\n`;
        statsText += `Success Rate: ${successRate}%\n`;
        if (stats.totalSize) {
          statsText += `Total Data Downloaded: ${formatBytes(stats.totalSize)}\n`;
        }
        if (stats.platform) {
          statsText += `Platform: ${stats.platform}\n`;
        }
        return {
          content: [{ type: 'text', text: statsText }],
        };
      }

      default:
        return {
          content: [
            {
              type: 'text',
              text: `Unknown tool: ${name}`,
            },
          ],
          isError: true,
        };
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
      isError: true,
    };
  }
});

// Utility function to format bytes
function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  logger.info('Bingo Downloader MCP Server running on stdio');
}

main().catch((error) => {
  logger.fatal({ error }, 'Fatal error in MCP Server');
  process.exit(1);
});