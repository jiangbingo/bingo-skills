#!/bin/bash
# yt-dlp download helper script
# Enhanced version with colored output and better error handling
#
# Usage: ./download.sh [options] URL
#
# Options:
#   -p, --path PATH      Download path (default: ~/Downloads/yt-dlp)
#   -a, --audio          Extract audio only (MP3)
#   -s, --subs           Download subtitles
#   -q, --quality NUM    Max video height (720, 1080, etc.)
#   -f, --format ID      Specific format ID
#   -l, --list           List available formats
#   -c, --cookies BROWSER Use cookies from browser (chrome, firefox, safari, etc.)
#   -b, --batch FILE     Batch download from file (one URL per line)
#   -h, --help           Show this help

set -e

# ============================================
# Colors and formatting
# ============================================
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color
readonly BOLD='\033[1m'

# ============================================
# Default values
# ============================================
DOWNLOAD_PATH="${HOME}/Downloads/yt-dlp"
AUDIO_ONLY=false
DOWNLOAD_SUBS=false
QUALITY=""
FORMAT_ID=""
LIST_FORMATS=false
COOKIES_BROWSER=""
BATCH_FILE=""
URL=""
PLAYLIST_ITEMS=""
WRITE_THUMBNAIL=false

# ============================================
# Retry configuration
# ============================================
MAX_RETRY_ATTEMPTS=3
INITIAL_RETRY_DELAY=5  # seconds
RETRY_BACKOFF_MULTIPLIER=2

# 可重试的错误类型
RETRYABLE_PATTERNS=(
    "HTTP Error 429"
    "HTTP Error 503"
    "HTTP Error 502"
    "ConnectionError"
    "Timeout"
    "network"
    "unable to download"
)

# Configuration file support
CONFIG_FILE="${HOME}/.yt-dlp.conf"

# Log file
LOG_FILE="${HOME}/.yt-dlp-download.log"
LOG_DIR="$(dirname "$LOG_FILE")"
mkdir -p "$LOG_DIR"

# Load config file if exists
if [[ -f "$CONFIG_FILE" ]]; then
    # shellcheck source=/dev/null
    source "$CONFIG_FILE"
fi

# ============================================
# Helper functions
# ============================================

# Logging functions
log_message() {
    local level="$1"
    shift
    local message="$*"
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

log_info() {
    log_message "INFO" "$@"
}

log_success() {
    log_message "SUCCESS" "$@"
}

log_warning() {
    log_message "WARNING" "$@"
}

log_error() {
    log_message "ERROR" "$@"
}

log_download_start() {
    local url="$1"
    local options="$2"
    log_info "Download started: URL=$url Options=$options"
}

log_download_success() {
    local url="$1"
    local output="$2"
    log_success "Download completed: URL=$url Output=$output"
}

log_download_failed() {
    local url="$1"
    local error="$2"
    log_error "Download failed: URL=$url Error=$error"
}

print_header() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${BLUE}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ Error: $1${NC}" >&2
}

print_warning() {
    echo -e "${YELLOW}⚠ Warning: $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

show_help() {
    cat << EOF
${BOLD}${PURPLE}yt-dlp Download Helper${NC}

${BOLD}Usage:${NC}
  $0 [options] URL

${BOLD}Options:${NC}
  -p, --path PATH       Download path (default: ~/Downloads/yt-dlp)
  -a, --audio           Extract audio only (MP3)
  -s, --subs            Download subtitles
  -q, --quality NUM     Max video height (720, 1080, etc.)
  -f, --format ID       Specific format ID
  -l, --list            List available formats
  -c, --cookies BRWSR   Use cookies from browser (chrome, firefox, safari, etc.)
  -b, --batch FILE      Batch download from file (one URL per line)
  -h, --help            Show this help

${BOLD}Examples:${NC}
  $0 "https://www.youtube.com/watch?v=xxx"
  $0 -a "https://www.youtube.com/watch?v=xxx"
  $0 -q 720 -s "https://www.youtube.com/watch?v=xxx"
  $0 -c chrome "https://www.youtube.com/watch?v=xxx"
  $0 -l "https://www.youtube.com/watch?v=xxx"

${BOLD}Supported browsers for cookies:${NC}
  chrome, firefox, safari, edge, brave, opera

${BOLD}Configuration:${NC}
  Create ~/.yt-dlp.conf to set default options:
    DOWNLOAD_PATH="/path/to/downloads"
    COOKIES_BROWSER="chrome"
EOF
}

# Detect available package managers
detect_package_manager() {
    if command -v uv &> /dev/null; then
        echo "uv"
    elif command -v pip &> /dev/null; then
        echo "pip"
    elif command -v pip3 &> /dev/null; then
        echo "pip3"
    else
        echo "none"
    fi
}

# Auto-install yt-dlp using available package manager
install_yt_dlp() {
    local pm=$(detect_package_manager)

    print_header "Installing yt-dlp"

    case $pm in
        uv)
            print_info "Using uv to install yt-dlp..."
            uv pip install yt-dlp
            ;;
        pip)
            print_info "Using pip to install yt-dlp..."
            pip install yt-dlp --user
            ;;
        pip3)
            print_info "Using pip3 to install yt-dlp..."
            pip3 install yt-dlp --user
            ;;
        *)
            print_error "No Python package manager found"
            echo ""
            print_info "Please install one of the following:"
            echo "  • uv:    curl -LsSf https://astral.sh/uv/install.sh | sh"
            echo "  • pip:   python -m ensurepip --upgrade"
            echo ""
            print_info "Then run this script again."
            exit 1
            ;;
    esac

    # Verify installation
    if command -v yt-dlp &> /dev/null; then
        print_success "yt-dlp installed successfully"
    else
        # Check if it's in standard locations but not in PATH
        local possible_paths=(
            "$HOME/.local/bin/yt-dlp"
            "$HOME/.venv/bin/yt-dlp"
            "/usr/local/bin/yt-dlp"
            "/opt/homebrew/bin/yt-dlp"
        )

        for path in "${possible_paths[@]}"; do
            if [[ -x "$path" ]]; then
                print_warning "yt-dlp found at $path but not in PATH"
                print_info "Add to PATH: export PATH=\"$(dirname $path):\$PATH\""
                export PATH="$(dirname $path):$PATH"
                return 0
            fi
        done

        print_error "yt-dlp installation failed"
        exit 1
    fi
}

# Auto-install ffmpeg using available package manager
install_ffmpeg() {
    local os=$(uname -s)

    print_header "Installing ffmpeg"

    case $os in
        Darwin)
            if command -v brew &> /dev/null; then
                print_info "Using Homebrew to install ffmpeg..."
                brew install ffmpeg
            else
                print_error "Homebrew not found"
                print_info "Install Homebrew first:"
                echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                exit 1
            fi
            ;;
        Linux)
            if command -v apt-get &> /dev/null; then
                print_info "Using apt to install ffmpeg..."
                sudo apt-get update && sudo apt-get install -y ffmpeg
            elif command -v yum &> /dev/null; then
                print_info "Using yum to install ffmpeg..."
                sudo yum install -y ffmpeg
            elif command -v dnf &> /dev/null; then
                print_info "Using dnf to install ffmpeg..."
                sudo dnf install -y ffmpeg
            else
                print_error "No supported package manager found"
                print_info "Please install ffmpeg manually:"
                echo "  • Ubuntu/Debian: sudo apt install ffmpeg"
                echo "  • Fedora: sudo dnf install ffmpeg"
                exit 1
            fi
            ;;
        *)
            print_error "Unsupported operating system: $os"
            exit 1
            ;;
    esac

    if command -v ffmpeg &> /dev/null; then
        print_success "ffmpeg installed successfully"
    else
        print_error "ffmpeg installation failed"
        exit 1
    fi
}

check_dependencies() {
    local missing=()
    local need_install=false

    if ! command -v yt-dlp &> /dev/null; then
        missing+=("yt-dlp")
        need_install=true
    fi

    if [[ "$AUDIO_ONLY" == true ]] && ! command -v ffmpeg &> /dev/null; then
        missing+=("ffmpeg")
        need_install=true
    fi

    if [[ $need_install == true ]]; then
        print_header "Missing Dependencies"
        print_warning "Missing: ${missing[*]}"
        echo ""

        # Try to auto-install
        for dep in "${missing[@]}"; do
            case $dep in
                yt-dlp)
                    install_yt_dlp
                    ;;
                ffmpeg)
                    install_ffmpeg
                    ;;
            esac
        done
        echo ""
    fi

    print_success "All dependencies satisfied"
}

# ============================================
# Smart retry with exponential backoff
# ============================================
is_retryable_error() {
    local error_msg="$1"
    for pattern in "${RETRYABLE_PATTERNS[@]}"; do
        if [[ "$error_msg" =~ $pattern ]]; then
            return 0
        fi
    done
    return 1
}

execute_with_retry() {
    local cmd="$1"
    local attempt=0
    local last_error=""

    while [ $attempt -lt $MAX_RETRY_ATTEMPTS ]; do
        if eval "$cmd"; then
            return 0
        fi

        last_error=$(eval "$cmd" 2>&1) || true

        # 检查是否可重试
        if ! is_retryable_error "$last_error"; then
            print_error "Non-retryable error: $last_error"
            return 1
        fi

        # 如果是最后一次尝试，不再等待
        if [ $attempt -eq $((MAX_RETRY_ATTEMPTS - 1)) ]; then
            break
        fi

        # 计算退避时间
        local delay=$((INITIAL_RETRY_DELAY * (RETRY_BACKOFF_MULTIPLIER ** attempt)))
        print_warning "Attempt $((attempt + 1))/$MAX_RETRY_ATTEMPTS failed: ${last_error:0:100}"
        print_warning "Retrying in ${delay} seconds..."
        sleep "$delay"
        attempt=$((attempt + 1))
    done

    print_error "All $MAX_RETRY_ATTEMPTS attempts failed"
    print_error "Last error: $last_error"
    return 1
}

detect_platform() {
    local url="$1"

    if [[ "$url" =~ youtube\.com ]] || [[ "$url" =~ youtu\.be ]]; then
        echo "youtube"
    elif [[ "$url" =~ bilibili\.com ]]; then
        echo "bilibili"
    elif [[ "$url" =~ (twitter\.com|x\.com) ]]; then
        echo "twitter"
    elif [[ "$url" =~ (tiktok\.com|douyin\.com) ]]; then
        echo "tiktok"
    else
        echo "unknown"
    fi
}

# ============================================
# Parse arguments
# ============================================
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--path)
            DOWNLOAD_PATH="$2"
            shift 2
            ;;
        -a|--audio)
            AUDIO_ONLY=true
            shift
            ;;
        -s|--subs)
            DOWNLOAD_SUBS=true
            shift
            ;;
        -q|--quality)
            QUALITY="$2"
            shift 2
            ;;
        -f|--format)
            FORMAT_ID="$2"
            shift 2
            ;;
        -l|--list)
            LIST_FORMATS=true
            shift
            ;;
        -c|--cookies)
            COOKIES_BROWSER="$2"
            shift 2
            ;;
        -b|--batch)
            BATCH_FILE="$2"
            shift 2
            ;;
        --playlist-items)
            PLAYLIST_ITEMS="$2"
            shift 2
            ;;
        --thumbnail|--thumb)
            WRITE_THUMBNAIL=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -*)
            print_error "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
        *)
            if [[ -z "$URL" ]]; then
                URL="$1"
            fi
            shift
            ;;
    esac
done

# ============================================
# Batch download mode
# ============================================
if [[ -n "$BATCH_FILE" ]]; then
    if [[ ! -f "$BATCH_FILE" ]]; then
        print_error "Batch file not found: $BATCH_FILE"
        exit 1
    fi

    print_header "Batch Download Mode"
    print_info "Processing URLs from: $BATCH_FILE"
    echo ""

    # Count total URLs
    total_urls=0
    while IFS= read -r line || [[ -n "$line" ]]; do
        [[ -z "$line" ]] || [[ "$line" =~ ^[[:space:]]*# ]] && continue
        ((total_urls++))
    done < "$BATCH_FILE"

    print_info "Found $total_urls URLs to process"
    echo ""

    # Process each URL with statistics
    success_count=0
    failed_count=0
    current=0

    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip empty lines and comments
        [[ -z "$line" ]] || [[ "$line" =~ ^[[:space:]]*# ]] && continue

        ((current++))
        echo ""
        print_info "[$current/$total_urls] Processing: ${line:0:70}"

        # Create a temporary script for single URL with all options except batch
        temp_args=()
        [[ "$AUDIO_ONLY" == true ]] && temp_args+=("-a")
        [[ "$DOWNLOAD_SUBS" == true ]] && temp_args+=("-s")
        [[ -n "$QUALITY" ]] && temp_args+=("-q" "$QUALITY")
        [[ -n "$FORMAT_ID" ]] && temp_args+=("-f" "$FORMAT_ID")
        [[ -n "$COOKIES_BROWSER" ]] && temp_args+=("-c" "$COOKIES_BROWSER")
        [[ -n "$DOWNLOAD_PATH" ]] && temp_args+=("-p" "$DOWNLOAD_PATH")
        temp_args+=("$line")

        # Run download and capture result
        if "$0" "${temp_args[@]}" > /dev/null 2>&1; then
            ((success_count++))
            print_success "✓ Success"
        else
            ((failed_count++))
            print_error "✗ Failed"
        fi
    done < "$BATCH_FILE"

    # Print summary
    echo ""
    print_header "Batch Download Summary"
    echo -e "${GREEN}✓ Success:${NC}   $success_count"
    echo -e "${RED}✗ Failed:${NC}    $failed_count"
    echo -e "${BOLD}Total:${NC}       $total_urls"
    echo ""

    if [[ $failed_count -gt 0 ]]; then
        exit 1
    fi

    exit 0
fi

# ============================================
# Validation
# ============================================
if [[ -z "$URL" ]]; then
    print_error "No URL provided"
    echo ""
    echo "Usage: $0 [options] URL"
    echo "Use -h or --help for usage information"
    exit 1
fi

# ============================================
# Check dependencies
# ============================================
print_header "Checking Dependencies"
check_dependencies

# ============================================
# List formats only
# ============================================
if [[ "$LIST_FORMATS" == true ]]; then
    print_header "Available Formats"
    yt-dlp -F "$URL"
    exit 0
fi

# ============================================
# Detect platform and apply defaults
# ============================================
PLATFORM=$(detect_platform "$URL")

if [[ "$PLATFORM" == "youtube" ]] && [[ -z "$COOKIES_BROWSER" ]]; then
    COOKIES_BROWSER="chrome"
    print_info "YouTube detected - using cookies from $COOKIES_BROWSER"
fi

# ============================================
# Detect playlist
# ============================================
is_playlist_url() {
    local url="$1"
    [[ "$url" =~ list= ]] || \
    [[ "$url" =~ playlist ]] || \
    [[ "$url" =~ /playlist/ ]] || \
    [[ "$url" =~ fid= ]] || \
    [[ "$url" =~ /fav/ ]]
}

IS_PLAYLIST=false
if is_playlist_url "$URL"; then
    IS_PLAYLIST=true
    print_info "📋 Playlist detected"
fi

# ============================================
# Create download directory
# ============================================
mkdir -p "$DOWNLOAD_PATH"

# ============================================
# Build command
# ============================================
CMD="yt-dlp -P \"$DOWNLOAD_PATH\""

# Add cookies if specified
if [[ -n "$COOKIES_BROWSER" ]]; then
    CMD="$CMD --cookies-from-browser $COOKIES_BROWSER"
fi

# Add format selection
if [[ -n "$FORMAT_ID" ]]; then
    CMD="$CMD -f \"$FORMAT_ID\""
elif [[ -n "$QUALITY" ]]; then
    CMD="$CMD -f \"bestvideo[height<=$QUALITY]+bestaudio/best[height<=$QUALITY]\""
fi

# Audio extraction
if [[ "$AUDIO_ONLY" == true ]]; then
    CMD="$CMD -x --audio-format mp3"
fi

# Subtitles
if [[ "$DOWNLOAD_SUBS" == true ]]; then
    CMD="$CMD --write-subs --sub-langs all --embed-subs"
fi

# Thumbnail
if [[ "$WRITE_THUMBNAIL" == true ]]; then
    CMD="$CMD --write-thumbnail --convert-thumbnails png"
fi

# Playlist handling
if [[ "$IS_PLAYLIST" == true ]]; then
    # Use playlist output template
    CMD="$CMD -o \"%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s\""

    # Add playlist items if specified
    if [[ -n "$PLAYLIST_ITEMS" ]]; then
        CMD="$CMD --playlist-items $PLAYLIST_ITEMS"
        print_info "Downloading playlist items: $PLAYLIST_ITEMS"
    fi
else
    CMD="$CMD --no-playlist"
fi

# Add progress and other useful options
CMD="$CMD --progress --newline"

# Add URL
CMD="$CMD \"$URL\""

# ============================================
# Display download info
# ============================================
print_header "Download Configuration"
echo -e "${BOLD}Platform:${NC}     $PLATFORM"
echo -e "${BOLD}Download Path:${NC} $DOWNLOAD_PATH"
echo -e "${BOLD}Audio Only:${NC}   $AUDIO_ONLY"
echo -e "${BOLD}Subtitles:${NC}    $DOWNLOAD_SUBS"
echo -e "${BOLD}Thumbnail:${NC}    $WRITE_THUMBNAIL"
echo -e "${BOLD}Quality:${NC}      ${QUALITY:-Best available}"
echo -e "${BOLD}Cookies:${NC}      ${COOKIES_BROWSER:-None}"

# ============================================
# Execute download with smart retry
# ============================================
echo ""
print_header "Starting Download"
print_info "Command: $CMD"
echo ""

# Log download start
log_download_start "$URL" "Quality=${QUALITY:-Best} Audio=${AUDIO_ONLY} Subs=${DOWNLOAD_SUBS}"

if execute_with_retry "$CMD"; then
    echo ""
    print_header "Download Complete!"
    print_success "Files saved to: ${GREEN}$DOWNLOAD_PATH${NC}"
    echo ""

    # Log success
    log_download_success "$URL" "$DOWNLOAD_PATH"

    # Show downloaded files
    print_info "Downloaded files:"
    ls -lh "$DOWNLOAD_PATH" | tail -n +2 | awk '{print "  " $9 " (" $5 ")"}'
else
    exit_code=$?
    echo ""
    print_header "Download Failed"
    print_error "Exit code: $exit_code"

    # Log failure
    log_download_failed "$URL" "Exit code: $exit_code"

    # Provide troubleshooting hints
    echo ""
    print_info "Troubleshooting tips:"
    echo "  • Try updating yt-dlp: pip install -U yt-dlp"
    echo "  • Try with cookies: -c chrome"
    echo "  • Check the URL is valid"
    echo "  • List available formats: -l"
    echo "  • Check log file: $LOG_FILE"

    exit $exit_code
fi
