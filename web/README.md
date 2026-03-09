# Bingo Downloader Web

基于 FastAPI + HTMX 的视频下载 Web 界面，支持 1000+ 网站。

## 功能特性

- 🎬 **视频下载** - 支持 YouTube、Bilibili、Twitter、TikTok 等 1000+ 网站
- 🎵 **音频提取** - 从视频中提取音频（MP3、WAV、M4A、FLAC、AAC）
- 📝 **字幕处理** - 下载并嵌入多语言字幕
- 📊 **历史记录** - 查看下载历史和统计信息
- 🔄 **实时进度** - WebSocket 实时下载进度显示
- 🎨 **现代界面** - 基于 Bootstrap 5 的响应式设计
- 🌐 **公开访问** - 无需登录，适合家庭内网使用

## 快速开始

### 1. 安装依赖

```bash
make install-web
```

或手动安装：

```bash
cd web/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 启动服务

```bash
make run-web
```

或手动启动：

```bash
cd web/backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. 访问界面

打开浏览器访问：http://localhost:8000

## 项目结构

```
web/
├── backend/                # FastAPI 后端
│   ├── main.py            # 应用入口
│   ├── config.py          # 配置管理
│   ├── api/               # API 路由
│   │   ├── download.py    # 下载 API
│   │   ├── history.py     # 历史 API
│   │   ├── stats.py       # 统计 API
│   │   └── formats.py     # 格式 API
│   ├── models/            # 数据模型
│   ├── core/              # 核心逻辑（复用 skill 脚本）
│   └── requirements.txt   # Python 依赖
│
├── frontend/              # 前端模板
│   ├── templates/         # Jinja2 模板
│   │   ├── base.html      # 基础模板
│   │   ├── index.html     # 主页
│   │   ├── history.html   # 历史页面
│   │   └── stats.html     # 统计页面
│   └── static/            # 静态资源
│       ├── css/main.css   # 自定义样式
│       └── js/main.js     # 自定义脚本
│
└── tests/                 # 测试文件
```

## API 端点

### 下载相关

- `POST /api/download/start` - 开始下载
- `GET /api/download/progress/{task_id}` - 获取下载进度
- `POST /api/download/cancel/{task_id}` - 取消下载
- `GET /api/download/tasks` - 列出所有任务

### 历史记录

- `GET /api/history/` - 获取下载历史
- `DELETE /api/history/clear` - 清空历史
- `DELETE /api/history/{record_id}` - 删除单条记录

### 统计信息

- `GET /api/stats/` - 获取统计信息
- `GET /api/stats/by-platform` - 按平台统计

### 格式查询

- `GET /api/formats/list?url={url}` - 列出可用格式

## 配置

环境变量：

```bash
# 服务器配置
HOST=0.0.0.0                # 监听地址
PORT=8000                    # 监听端口
RELOAD=true                  # 开发模式热重载

# 下载配置
DEFAULT_QUALITY=1080         # 默认质量
DEFAULT_COOKIES_BROWSER=chrome  # 默认 Cookie 浏览器
MAX_FILE_SIZE_WARNING=2147483648  # 最大文件大小警告（2GB）

# CORS
CORS_ORIGINS=http://localhost:8000,http://localhost:3000
```

## 开发

### 运行开发服务器

```bash
make dev-web
```

### 运行测试

```bash
make test-web
```

### 清理

```bash
make clean
```

## 技术栈

- **后端**: FastAPI + uvicorn
- **前端**: HTMX + Bootstrap 5 + Jinja2
- **核心引擎**: yt-dlp
- **数据库**: SQLite
- **样式**: Bootstrap 5 + 自定义 CSS

## 与主项目的关系

Web UI 作为 Monorepo 的一部分，与 MCP Server 和 Skills 共享核心下载逻辑：

```
skill/scripts/download.py  ← 核心类定义
        ↓
web/backend/core/          ← 复用核心类
        ↓
FastAPI API 端点
```

## 故障排除

### 端口被占用

修改端口：
```bash
PORT=8888 make run-web
```

### yt-dlp 未安装

```bash
pip install yt-dlp
```

### ffmpeg 未安装

macOS:
```bash
brew install ffmpeg
```

Linux:
```bash
sudo apt install ffmpeg
```

## 许可证

MIT License - 与主项目相同
