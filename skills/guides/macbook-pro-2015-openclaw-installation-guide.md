# MacBook Pro 2015 OpenClaw 安装指南

版本：5.0.0 | 更新：2026-02-09

适用设备：MacBook Pro 2015 (Intel)
适用系统：macOS 10.15 - macOS 12 (Monterey)

---

## 快速导航

| 章节 | 内容 |
|------|------|
| [系统要求](#系统要求) | 硬件配置、系统版本 |
| [环境准备](#环境准备) | Node.js、Oh My Zsh |
| [安装方式](#安装方式) | 一键脚本、pnpm、源码编译 |
| [基础配置](#基础配置) | 模型 API Key 配置 |
| [故障排除](#故障排除) | 常见问题解决方案 |
| [性能优化](#性能优化) | 2015款Mac专属优化 |
| [命令速查](#命令速查) | 常用命令参考 |

---

## 系统要求

### 硬件配置

| 项目 | 最低配置 | 推荐配置 |
|------|----------|----------|
| 内存 | 4GB | 8GB |
| 硬盘 | 20GB 可用空间 | 50GB+ SSD |
| CPU | Intel Core i5 | Intel Core i7 |

### 软件要求

- 操作系统：macOS 10.15 (Catalina) 及以上
- Node.js：20.x LTS（推荐）或 18.x
- 包管理器：pnpm 8+ 或 npm 9+
- 终端：zsh (系统默认)

> 注意：2015款Mac通常最高支持到 macOS 12 (Monterey)，Node.js 22+ 可能存在兼容性问题，建议使用 Node.js 20.x LTS 版本。

---

## 环境准备

### 安装 nvm（Node 版本管理）

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.zshrc
nvm --version
```

### 安装 Node.js 20.x

```bash
nvm install 20
nvm alias default 20
node -v  # 应输出 v20.x.x
npm -v
```

### 配置 Oh My Zsh（可选）

```bash
# 检查是否已安装
ls ~/.oh-my-zsh

# 如未安装
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# 编辑配置
vim ~/.zshrc

# 添加插件
plugins=(git zsh-syntax-highlighting zsh-autosuggestions)

# 刷新
source ~/.zshrc
```

---

## 安装方式

### 方式一：一键安装脚本

已包含2015款Mac专属优化：

```bash
#!/bin/zsh
echo "=== 开始安装 OpenClaw ==="

# 安装 nvm 和 Node.js 20.x
if ! command -v nvm &> /dev/null; then
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    source ~/.zshrc
fi
nvm install 20
nvm alias default 20

# 安装 pnpm 并配置国内镜像
npm install -g pnpm --registry=https://registry.npmmirror.com
mkdir -p ~/.pnpm-global/bin
pnpm config set global-bin-dir ~/.pnpm-global/bin
pnpm config set registry https://registry.npmmirror.com
echo 'export PATH="$HOME/.pnpm-global/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 克隆源码并编译（内存优化）
mkdir -p ~/Dev/openclaw
cd ~/Dev/openclaw
git clone https://github.com/openclaw/openclaw.git
cd openclaw
export NODE_OPTIONS="--max-old-space-size=4096"
pnpm install
pnpm build
pnpm link --global

# 基础配置
echo 'export NODE_NO_WARNINGS=1' >> ~/.zshrc
pnpm config set store-path ~/.pnpm-store
source ~/.zshrc

# 验证安装
echo "=== 安装验证 ==="
which openclaw
openclaw -v
node -v
echo "=== 安装完成，请执行 openclaw wizard 配置API Key ==="
```

保存为 `install-openclaw.sh` 后执行：

```bash
chmod +x install-openclaw.sh
./install-openclaw.sh
```

---

### 方式二：pnpm 全局安装

```bash
# 安装 pnpm
npm install -g pnpm --registry=https://registry.npmmirror.com

# 配置全局 bin 目录
mkdir -p ~/.pnpm-global/bin
pnpm config set global-bin-dir ~/.pnpm-global/bin

# 添加到 PATH
echo 'export PATH="$HOME/.pnpm-global/bin:$PATH"' >> ~/.zshrc
echo 'export PNPM_HOME="$HOME/.pnpm-global"' >> ~/.zshrc
echo 'eval "$(pnpm env --shell zsh)"' >> ~/.zshrc
source ~/.zshrc

# 全局安装 OpenClaw
pnpm add -g openclaw --registry=https://registry.npmmirror.com

# 验证
which openclaw
openclaw -v
```

---

### 方式三：源码编译

```bash
# 克隆仓库
mkdir -p ~/Dev/openclaw
cd ~/Dev/openclaw
git clone https://github.com/openclaw/openclaw.git
cd openclaw

# 内存优化设置（2015款Mac关键步骤）
export NODE_OPTIONS="--max-old-space-size=4096"

# 安装依赖并编译
pnpm install
pnpm build
pnpm link --global

# 验证
openclaw -v
```

编译时如果内存不足，尝试分步编译：

```bash
pnpm run build:cli    # 先编译CLI核心
pnpm run build:gateway # 再编译Gateway
```

---

## 基础配置

### 添加 Z.AI / GLM 模型

```bash
openclaw auth add bigmodel
openclaw auth add bigmodel --api-key YOUR_API_KEY
openclaw config get providers.bigmodel.apiKey
```

### 添加 Anthropic / Claude 模型

```bash
openclaw auth add anthropic
openclaw config set providers.anthropic.apiKey YOUR_API_KEY
openclaw config get providers.anthropic
```

### 启动 Gateway

```bash
# 轻量模式启动，适合2015款Mac
openclaw gateway start --no-watch --log-level warn

# 检查状态
openclaw gateway status

# 查看日志
openclaw logs --follow
```

### 配置向导

```bash
openclaw wizard
```

### 启动 Web UI

OpenClaw 提供了可视化的 Web UI 界面，支持在浏览器中进行对话和管理：

#### 方式一：使用 CLI 启动

```bash
# 启动 Gateway 和 Web UI
openclaw server --port 3000

# 或指定不同端口
openclaw server --port 8080
```

启动后，自动在默认浏览器打开 Web UI，或手动访问：

```
http://localhost:3000
```

#### 方式二：Gateway + Web Server 分别启动

```bash
# 终端1：启动 Gateway
openclaw gateway start

# 终端2：启动 Web UI 服务器
openclaw web --port 3000
```

#### 方式三：对话界面

```bash
# 启动交互式对话（终端内）
openclaw chat

# 或指定模型进行对话
openclaw chat --model glm-4-flash
```

#### Web UI 访问地址

| 环境 | 地址 | 用途 |
|------|------|------|
| 本地开发 | `http://localhost:3000` | Web 界面对话 |
| 远程访问 | `http://<你的IP>:3000` | 网络访问（需配置认证） |
| WebSocket | `ws://localhost:3000/ws` | 实时通信 |

#### Web UI 常见操作

```bash
# 查看 Web UI 的日志
openclaw logs --service web --follow

# 重启 Web UI
openclaw web restart --port 3000

# 关闭 Web UI
openclaw web stop
```

> 注意：在 2015 款 Mac 上运行 Web UI 需要充足内存，建议关闭其他应用以确保流畅运行。

---

## 故障排除

### Token 认证失败

错误信息：
```
unauthorized: gateway token missing
```

解决：

```bash
openclaw config get gateway.auth.token
openssl rand -base64 32
openclaw config set gateway.auth.token "YOUR_NEW_TOKEN"
openclaw gateway restart
```

---

### 端口占用

错误信息：
```
Error: bind EADDRINUSE - address already in use :::18789
```

解决：

```bash
lsof -i :18789
kill -9 <PID>
openclaw gateway start
```

---

### CLI 命令未找到

错误信息：
```
zsh: command not found: openclaw
```

解决：

```bash
pnpm setup
echo 'export PATH="$HOME/.pnpm-global/bin:$PATH"' >> ~/.zshrc
echo 'export PNPM_HOME="$HOME/.pnpm-global"' >> ~/.zshrc
echo 'eval "$(pnpm env --shell zsh)"' >> ~/.zshrc
source ~/.zshrc
which openclaw
```

---

### 编译内存不足

错误信息：
```
Error: ENOMEM: not enough memory
```

解决：

```bash
purge
killall -9 node
export NODE_OPTIONS="--max-old-space-size=4096"
cd ~/Dev/openclaw/openclaw
pnpm install
pnpm build
```

---

### pnpm 安装权限错误

错误信息：
```
EACCES: permission denied
```

解决：

```bash
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
pnpm config set registry https://registry.npmmirror.com
pnpm config set electron_mirror https://npmmirror.com/mirrors/electron/
```

---

## 性能优化

### Node.js 运行时

```bash
# 添加到 ~/.zshrc
export NODE_NO_WARNINGS=1
export NODE_OPTIONS="--max-old-space-size=4096"

source ~/.zshrc
```

### pnpm 性能

```bash
pnpm config set store-path ~/.pnpm-store
pnpm config set update-notifier false
pnpm config set registry https://registry.npmmirror.com
```

### Gateway 轻量运行

```bash
openclaw gateway start --no-watch --log-level warn
openclaw config set agent.concurrency 1
openclaw config set agent.autoUpdate false
```

### 模型选择

轻量级模型减少资源占用：

| 模型 | 特点 | 推荐场景 |
|------|------|----------|
| glm-4-flash | 轻量快速 | 日常对话、简单任务 |
| qwen-turbo | 低延迟 | 代码补全、翻译 |
| claude-haiku | 成本低 | 文本处理、分析 |

### 清理缓存

```bash
rm -rf ~/.openclaw/cache
pnpm store prune
npm cache clean --force
```

---

## 命令速查

### 系统管理

```bash
openclaw -v              # 查看版本
openclaw doctor          # 系统诊断
openclaw logs --follow   # 实时日志
```

### Gateway 操作

```bash
openclaw gateway start   # 启动
openclaw gateway stop    # 停止
openclaw gateway restart # 重启
openclaw gateway status  # 状态
```

### 认证配置

```bash
openclaw auth list               # 列出认证
openclaw auth add <provider>     # 添加
openclaw auth remove <provider>  # 移除
```

### 配置管理

```bash
openclaw config              # 查看所有配置
openclaw config get <path>   # 查看特定配置
openclaw config set <path> <value>  # 设置
openclaw wizard              # 配置向导
```

### Agent 操作

```bash
openclaw agent --message "你好"
openclaw sessions list
openclaw sessions history agent:main:main
```

### Web UI & 对话

```bash
openclaw server --port 3000          # 启动完整服务（Gateway + Web UI）
openclaw server --port 8080          # 指定端口启动
openclaw web --port 3000             # 仅启动 Web UI
openclaw chat                        # 启动终端对话模式
openclaw chat --model glm-4-flash    # 指定模型进行对话
openclaw web restart                 # 重启 Web UI
openclaw web stop                    # 停止 Web UI
openclaw logs --service web --follow # 查看 Web UI 日志
```

---

## 安装验证清单

### 环境检查

- [ ] Node.js 版本为 20.x（`node -v`）
- [ ] pnpm 命令可用（`which pnpm`）
- [ ] openclaw 命令可用（`which openclaw`）
- [ ] PATH 包含 pnpm bin 目录

### Gateway 检查

- [ ] Token 已配置
- [ ] Gateway 正在运行（`openclaw gateway status`）
- [ ] 端口 18789 可用（`lsof -i :18789`）

### Agent 检查

- [ ] 模型 API Key 已添加
- [ ] 默认模型已设置
- [ ] 可发送测试消息（`openclaw agent --message "测试"`）

### 性能检查（2015款Mac）

- [ ] 剩余内存 ≥ 2GB（活动监视器）
- [ ] Node 进程 CPU 占用 < 50%
- [ ] Gateway 启动时间 < 10秒

---

## 数据位置

```
~/.openclaw/              # 配置和工作区
├── agents/               # Agent 数据
├── sessions/             # 会话历史
├── cache/                # 缓存文件
└── config.json           # 主配置文件

~/.pnpm-global/           # 全局包目录
├── bin/                  # 可执行文件
└── node_modules/         # 依赖包

~/Dev/openclaw/           # 源码目录
```

---

## 参考资源

| 资源类型 | 链接 |
|----------|------|
| 官方文档 | https://docs.openclaw.ai |
| GitHub 仓库 | https://github.com/openclaw/openclaw |
| 故障排除 | https://docs.openclaw.ai/troubleshooting |
| 社区讨论 | https://discord.gg/clawd |

---

## 附录

### 卸载 OpenClaw

```bash
openclaw gateway stop
pnpm remove -g openclaw
rm -rf ~/.openclaw
```

然后编辑 `~/.zshrc`，删除以下行：

```bash
export PATH="$HOME/.pnpm-global/bin:$PATH"
export PNPM_HOME="$HOME/.pnpm-global"
eval "$(pnpm env --shell zsh)"
```

### 常用端口

| 端口 | 用途 |
|------|------|
| 18789 | Gateway 主服务 |
| 18790 | Gateway WebSocket |

### 日志级别

| 级别 | 用途 |
|------|------|
| debug | 详细调试信息 |
| info | 常规信息（默认） |
| warn | 警告信息 |
| error | 仅错误信息 |
