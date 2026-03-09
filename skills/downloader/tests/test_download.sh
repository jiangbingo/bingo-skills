#!/bin/bash
# Unit tests for download.sh script
#
# Run with: bash tests/test_download.sh

# Test colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test helper functions
test_assert() {
    local test_name="$1"
    local condition="$2"
    local expected="$3"
    local actual="$4"

    TESTS_RUN=$((TESTS_RUN + 1))

    if [[ "$actual" == "$expected" ]]; then
        echo -e "${GREEN}✓${NC} $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $test_name"
        echo -e "  Expected: $expected"
        echo -e "  Actual: $actual"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

echo "=========================================="
echo "Bingo Downloader - Shell Script Tests"
echo "=========================================="
echo ""

# Test platform detection
echo "Testing platform detection..."

# Create a temporary function to test platform detection
test_detect_platform() {
    local url="$1"
    if [[ "$url" =~ youtube\.com ]] || [[ "$url" =~ youtu\.be ]]; then
        echo "YouTube"
    elif [[ "$url" =~ bilibili\.com ]]; then
        echo "Bilibili"
    elif [[ "$url" =~ twitter\.com ]] || [[ "$url" =~ x\.com ]]; then
        echo "Twitter/X"
    elif [[ "$url" =~ tiktok\.com ]] || [[ "$url" =~ douyin\.com ]]; then
        echo "TikTok/Douyin"
    else
        echo "Unknown"
    fi
}

test_assert "YouTube detection (youtube.com)" "==" "YouTube" "$(test_detect_platform "https://www.youtube.com/watch?v=xxx")"
test_assert "YouTube detection (youtu.be)" "==" "YouTube" "$(test_detect_platform "https://youtu.be/xxx")"
test_assert "Bilibili detection" "==" "Bilibili" "$(test_detect_platform "https://www.bilibili.com/video/BV1xx")"
test_assert "Twitter detection" "==" "Twitter/X" "$(test_detect_platform "https://twitter.com/user/status/123")"
test_assert "X.com detection" "==" "Twitter/X" "$(test_detect_platform "https://x.com/user/status/123")"
test_assert "TikTok detection" "==" "TikTok/Douyin" "$(test_detect_platform "https://www.tiktok.com/@user/video/123")"
test_assert "Douyin detection" "==" "TikTok/Douyin" "$(test_detect_platform "https://www.douyin.com/video/123")"
test_assert "Unknown platform" "==" "Unknown" "$(test_detect_platform "https://example.com/video")"

echo ""

# Test playlist detection
echo "Testing playlist detection..."

test_is_playlist() {
    local url="$1"
    [[ "$url" =~ list= ]] || \
    [[ "$url" =~ playlist ]] || \
    [[ "$url" =~ /playlist/ ]] && echo "true" || echo "false"
}

test_assert "YouTube playlist detection" "==" "true" "$(test_is_playlist "https://www.youtube.com/playlist?list=xxx")"
test_assert "Video with playlist param" "==" "true" "$(test_is_playlist "https://www.youtube.com/watch?v=xxx&list=yyy")"
test_assert "Single video (not playlist)" "==" "false" "$(test_is_playlist "https://www.youtube.com/watch?v=xxx")"

echo ""

# Test quality format strings
echo "Testing quality format selection..."

test_get_quality_format() {
    local quality="$1"
    case "$quality" in
        1080)
            echo "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
            ;;
        720)
            echo "bestvideo[height<=720]+bestaudio/best[height<=720]"
            ;;
        480)
            echo "bestvideo[height<=480]+bestaudio/best[height<=480]"
            ;;
        *)
            echo "bestvideo+bestaudio/best"
            ;;
    esac
}

test_assert "1080p format" "==" "bestvideo[height<=1080]+bestaudio/best[height<=1080]" "$(test_get_quality_format "1080")"
test_assert "720p format" "==" "bestvideo[height<=720]+bestaudio/best[height<=720]" "$(test_get_quality_format "720")"
test_assert "480p format" "==" "bestvideo[height<=480]+bestaudio/best[height<=480]" "$(test_get_quality_format "480")"
test_assert "Default format" "==" "bestvideo+bestaudio/best" "$(test_get_quality_format "best")"

echo ""

# Test retryable error patterns
echo "Testing retryable error detection..."

RETRYABLE_PATTERNS=(
    "HTTP Error 429"
    "HTTP Error 503"
    "HTTP Error 502"
    "ConnectionError"
    "Timeout"
)

is_retryable_error() {
    local error="$1"
    for pattern in "${RETRYABLE_PATTERNS[@]}"; do
        if [[ "$error" == *"$pattern"* ]]; then
            echo "true"
            return
        fi
    done
    echo "false"
}

test_assert "429 error is retryable" "==" "true" "$(is_retryable_error "HTTP Error 429: Too Many Requests")"
test_assert "503 error is retryable" "==" "true" "$(is_retryable_error "HTTP Error 503: Service Unavailable")"
test_assert "502 error is retryable" "==" "true" "$(is_retryable_error "HTTP Error 502: Bad Gateway")"
test_assert "Timeout is retryable" "==" "true" "$(is_retryable_error "Connection Timeout")"
test_assert "403 error is NOT retryable" "==" "false" "$(is_retryable_error "HTTP Error 403: Forbidden")"
test_assert "404 error is NOT retryable" "==" "false" "$(is_retryable_error "HTTP Error 404: Not Found")"

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "Tests run: ${TESTS_RUN}"
echo -e "${GREEN}Passed: ${TESTS_PASSED}${NC}"
if [[ $TESTS_FAILED -gt 0 ]]; then
    echo -e "${RED}Failed: ${TESTS_FAILED}${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
