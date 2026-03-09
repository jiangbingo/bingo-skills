/**
 * Bingo Downloader Web - Main JavaScript
 */

// Toast notification system
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    const toastId = `toast-${Date.now()}`;

    const iconMap = {
        'success': 'bi-check-circle-fill',
        'error': 'bi-exclamation-circle-fill',
        'warning': 'bi-exclamation-triangle-fill',
        'info': 'bi-info-circle-fill'
    };

    const colorMap = {
        'success': 'text-success',
        'error': 'text-danger',
        'warning': 'text-warning',
        'info': 'text-info'
    };

    const toastHTML = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="bi ${iconMap[type] || iconMap['info']} ${colorMap[type] || colorMap['info']} me-2"></i>
                <strong class="me-auto">Bingo Downloader</strong>
                <small class="text-muted">刚刚</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHTML);

    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
    toast.show();

    // Clean up after toast is hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// Format file size for display
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (seconds < 60) return '刚刚';
    if (minutes < 60) return `${minutes} 分钟前`;
    if (hours < 24) return `${hours} 小时前`;
    if (days < 7) return `${days} 天前`;

    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Validate URL format
function isValidURL(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

// Detect platform from URL
function detectPlatform(url) {
    const patterns = {
        'YouTube': ['youtube.com', 'youtu.be'],
        'Bilibili': ['bilibili.com'],
        'Twitter/X': ['twitter.com', 'x.com'],
        'TikTok': ['tiktok.com', 'douyin.com'],
        'Vimeo': ['vimeo.com'],
        'Twitch': ['twitch.tv']
    };

    for (const [platform, domainList] of Object.entries(patterns)) {
        if (domainList.some(domain => url.includes(domain))) {
            return platform;
        }
    }
    return 'Unknown';
}

// Copy text to clipboard
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('已复制到剪贴板', 'success');
    } catch (err) {
        showToast('复制失败', 'error');
    }
}

// Download progress tracking
class DownloadProgressTracker {
    constructor() {
        this.activeTasks = new Map();
        this.pollInterval = 1000; // 1 second
    }

    startTracking(taskId, callback) {
        const interval = setInterval(async () => {
            try {
                const response = await fetch(`/api/download/progress/${taskId}`);
                const progress = await response.json();

                callback(progress);

                if (progress.status === 'completed' || progress.status === 'failed') {
                    this.stopTracking(taskId);
                }
            } catch (error) {
                console.error('Error fetching progress:', error);
            }
        }, this.pollInterval);

        this.activeTasks.set(taskId, interval);
    }

    stopTracking(taskId) {
        const interval = this.activeTasks.get(taskId);
        if (interval) {
            clearInterval(interval);
            this.activeTasks.delete(taskId);
        }
    }

    stopAll() {
        this.activeTasks.forEach(interval => clearInterval(interval));
        this.activeTasks.clear();
    }
}

// Global progress tracker instance
const progressTracker = new DownloadProgressTracker();

// Form validation
function validateDownloadForm() {
    const urlInput = document.getElementById('url');
    const submitBtn = document.getElementById('submit-btn');

    if (!urlInput || !submitBtn) return;

    urlInput.addEventListener('input', () => {
        const isValid = isValidURL(urlInput.value);
        submitBtn.disabled = !isValid;

        if (isValid) {
            urlInput.classList.remove('is-invalid');
            urlInput.classList.add('is-valid');
        } else {
            urlInput.classList.remove('is-valid');
            if (urlInput.value.length > 0) {
                urlInput.classList.add('is-invalid');
            }
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    validateDownloadForm();

    // Auto-hide loading indicators
    setTimeout(() => {
        document.querySelectorAll('.htmx-indicator').forEach(el => {
            if (!el.classList.contains('d-none')) {
                // Still loading, leave it
            }
        });
    }, 100);
});

// HTMX event handlers
document.body.addEventListener('htmx:beforeRequest', function(evt) {
    // Show loading state
    const target = evt.target;
    if (target) {
        target.style.opacity = '0.6';
    }
});

document.body.addEventListener('htmx:afterRequest', function(evt) {
    // Restore normal state
    const target = evt.target;
    if (target) {
        target.style.opacity = '1';
    }
});

document.body.addEventListener('htmx:responseError', function(evt) {
    // Show error toast
    showToast('请求失败，请稍后重试', 'error');
});

// Export functions for global use
window.BingoDownloader = {
    showToast,
    formatFileSize,
    formatDate,
    isValidURL,
    detectPlatform,
    copyToClipboard,
    progressTracker
};
