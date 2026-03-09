/**
 * Logger Configuration for Bingo Downloader MCP Server
 * Using Pino for high-performance structured logging
 */

import pino from 'pino';

// Log levels
export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error',
  SILENT = 'silent'
}

// Get log level from environment variable
const getLogLevel = (): LogLevel => {
  const envLevel = process.env.LOG_LEVEL?.toUpperCase();
  const isDevelopment = process.env.NODE_ENV === 'development';

  if (envLevel && Object.values(LogLevel).includes(envLevel.toLowerCase() as LogLevel)) {
    return envLevel.toLowerCase() as LogLevel;
  }

  // Default to debug in development, info in production
  return isDevelopment ? LogLevel.DEBUG : LogLevel.INFO;
};

// Base logger configuration
const baseConfig: pino.LoggerOptions = {
  level: getLogLevel(),
  formatters: {
    level: (label) => {
      return { level: label };
    },
  },
  timestamp: pino.stdTimeFunctions.isoTime,
  serializers: {
    err: pino.stdSerializers.err,
    error: pino.stdSerializers.err,
  },
};

// Development configuration with pretty print
const developmentConfig: pino.LoggerOptions = {
  ...baseConfig,
  transport: {
    target: 'pino-pretty',
    options: {
      colorize: true,
      translateTime: 'SYS:standard',
      ignore: 'pid,hostname',
      messageFormat: '[{label}] {msg}',
    },
  },
};

// Production configuration with JSON output
const productionConfig: pino.LoggerOptions = {
  ...baseConfig,
  // Add file output in production
  ...(process.env.LOG_FILE && {
    targets: [
      {
        level: 'error',
        target: 'pino/file',
        options: {
          destination: process.env.LOG_FILE.replace('.log', '-error.log'),
          mkdir: true,
        },
      },
      {
        level: 'info',
        target: 'pino/file',
        options: {
          destination: process.env.LOG_FILE,
          mkdir: true,
        },
      },
    ],
  }),
};

// Create logger instance
const isDevelopment = process.env.NODE_ENV === 'development';
const config = isDevelopment ? developmentConfig : productionConfig;

export const logger = pino(config);

// Create child logger with context
export const createLogger = (context: string): pino.Logger => {
  return logger.child({ context });
};

// Convenience methods for common log patterns
export const logDownloadStart = (url: string, options?: Record<string, unknown>): void => {
  logger.info({
    type: 'download_start',
    url,
    ...options,
  }, 'Starting download');
};

export const logDownloadSuccess = (url: string, filePath: string, duration?: number): void => {
  logger.info({
    type: 'download_success',
    url,
    filePath,
    duration,
  }, 'Download completed successfully');
};

export const logDownloadError = (url: string, error: Error | string, duration?: number): void => {
  logger.error({
    type: 'download_error',
    url,
    error: error instanceof Error ? error.message : error,
    stack: error instanceof Error ? error.stack : undefined,
    duration,
  }, 'Download failed');
};

export const logApiCall = (method: string, path: string, statusCode?: number): void => {
  const level = statusCode && statusCode >= 400 ? 'warn' : 'debug';
  logger[level]({
    type: 'api_call',
    method,
    path,
    statusCode,
  }, `API ${method} ${path}`);
};

export default logger;
