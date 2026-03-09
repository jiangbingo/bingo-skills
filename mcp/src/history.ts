import path from 'path';
import fs from 'fs/promises';
import { createLogger } from './logger.js';

const logger = createLogger('history');

interface DownloadRecord {
  id: number;
  url: string;
  title: string;
  platform: string;
  filePath: string;
  fileSize: number;
  success: boolean;
  timestamp: number;
}

interface Statistics {
  total: number;
  successful: number;
  failed: number;
  totalSize: number;
  platform?: string;
}

// Database file path
const DB_PATH = path.join(process.env.HOME || '', '.yt-dlp-history.db');
const DB_SQLITE_PATH = path.join(process.env.HOME || '', '.yt-dlp-downloads.json');

// Initialize database
async function initDB(): Promise<void> {
  try {
    await fs.access(DB_SQLITE_PATH);
  } catch {
    // Create empty database
    const jsonData = JSON.stringify({ downloads: [] });
    await fs.writeFile(DB_SQLITE_PATH, jsonData, 'utf-8');
  }
}

// Read all downloads
async function getDownloads(): Promise<DownloadRecord[]> {
  try {
    await initDB();
    const data = await fs.readFile(DB_SQLITE_PATH, 'utf-8');
    const db = JSON.parse(data);
    return db.downloads || [];
  } catch (error) {
    logger.error({ error }, 'Error reading downloads from database');
    return [];
  }
}

// Save downloads
async function saveDownloads(downloads: DownloadRecord[]): Promise<void> {
  try {
    const data = JSON.stringify({ downloads }, null, 2);
    await fs.writeFile(DB_SQLITE_PATH, data, 'utf-8');
  } catch (error) {
    logger.error({ error }, 'Error saving downloads to database');
  }
}

// Add download record
export async function addDownload(record: Omit<DownloadRecord, 'id' | 'timestamp'>): Promise<void> {
  const downloads = await getDownloads();
  
  const newRecord: DownloadRecord = {
    ...record,
    id: downloads.length > 0 ? Math.max(...downloads.map(d => d.id)) + 1 : 1,
    timestamp: Date.now(),
  };
  
  downloads.push(newRecord);
  await saveDownloads(downloads);
}

// Get download history
export async function getHistory(limit: number = 20, platform?: string): Promise<DownloadRecord[]> {
  let downloads = await getDownloads();
  
  // Filter by platform if specified
  if (platform) {
    downloads = downloads.filter(d => 
      d.platform.toLowerCase() === platform.toLowerCase()
    );
  }
  
  // Sort by timestamp (newest first)
  downloads.sort((a, b) => b.timestamp - a.timestamp);
  
  // Limit results
  return downloads.slice(0, limit);
}

// Get statistics
export async function getStats(platform?: string): Promise<Statistics> {
  const downloads = await getDownloads();
  
  let filteredDownloads = downloads;
  
  if (platform) {
    filteredDownloads = downloads.filter(d =>
      d.platform.toLowerCase() === platform.toLowerCase()
    );
  }
  
  const total = filteredDownloads.length;
  const successful = filteredDownloads.filter(d => d.success).length;
  const failed = total - successful;
  const totalSize = filteredDownloads
    .filter(d => d.success)
    .reduce((sum, d) => sum + (d.fileSize || 0), 0);
  
  return {
    total,
    successful,
    failed,
    totalSize,
    platform: platform || undefined,
  };
}

// Get recent downloads
export async function getRecentDownloads(hours: number = 24): Promise<DownloadRecord[]> {
  const downloads = await getDownloads();
  const cutoff = Date.now() - hours * 60 * 60 * 1000;
  
  return downloads
    .filter(d => d.timestamp >= cutoff)
    .sort((a, b) => b.timestamp - a.timestamp);
}

// Clear old downloads (older than specified days)
export async function clearOldDownloads(days: number = 30): Promise<number> {
  const downloads = await getDownloads();
  const cutoff = Date.now() - days * 24 * 60 * 60 * 1000;
  
  const filteredDownloads = downloads.filter(d => d.timestamp >= cutoff);
  const removedCount = downloads.length - filteredDownloads.length;
  
  if (removedCount > 0) {
    await saveDownloads(filteredDownloads);
  }
  
  return removedCount;
}

// Get platform breakdown
export async function getPlatformBreakdown(): Promise<Record<string, number>> {
  const downloads = await getDownloads();
  const breakdown: Record<string, number> = {};
  
  downloads.forEach(d => {
    const platform = d.platform || 'Unknown';
    breakdown[platform] = (breakdown[platform] || 0) + 1;
  });
  
  return breakdown;
}