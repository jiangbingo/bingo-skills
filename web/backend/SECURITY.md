# Bingo Downloader Web - Security Guide

## 概述

本项目的 Web UI 已实现多项安全增强功能，以保护 API 端点和用户数据。

## 安全功能

### 1. API Key 认证（可选）

API Key 认证提供了一种简单的方式来保护 API 端点。**默认禁用**，以保持向后兼容性。

#### 配置

在 `.env` 文件中设置：

```bash
# 启用 API Key 认证
API_KEY_ENABLED=true

# 配置有效的 API Keys（逗号分隔）
API_KEYS=your-key-1,your-key-2,your-key-3

# 自定义 Header 名称（可选）
API_KEY_NAME=X-API-Key
```

#### 生成安全的 API Key

```bash
# 使用 OpenSSL 生成
openssl rand -hex 32

# 或使用 Python
python -c "import secrets; print(secrets.token_hex(32))"
```

#### 使用方法

启用后，所有 API 请求必须在 Header 中包含 API Key：

```bash
curl -X POST http://localhost:8000/api/download/start \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=xxx"}'
```

#### 公开端点

以下端点**不需要** API Key：
- `/` - 主页
- `/health` - 健康检查
- `/static/*` - 静态文件
- `/api/docs` - API 文档
- `/api/redoc` - ReDoc 文档

---

### 2. 速率限制

默认启用速率限制以防止 API 滥用。

#### 配置

```bash
# 启用/禁用速率限制
RATE_LIMIT_ENABLED=true

# 每分钟请求数限制
RATE_LIMIT_REQUESTS=60

# 时间窗口（秒）
RATE_LIMIT_WINDOW=60
```

#### 行为

- 超过限制后返回 `429 Too Many Requests`
- 响应头包含：
  - `X-RateLimit-Limit`: 限制总数
  - `X-RateLimit-Window`: 时间窗口
  - `Retry-After`: 重试等待时间

#### 排除路径

以下路径不受速率限制：
- `/` - 主页
- `/health` - 健康检查
- `/static/*` - 静态文件

---

### 3. Cookie 加密存储

浏览器 Cookie 现在默认使用 Fernet 对称加密存储，以提高安全性。

#### 功能

- **自动加密**: 新缓存的 Cookie 自动加密
- **更短的过期时间**: 默认 24 小时（可配置），之前的 7 天
- **密钥管理**: 支持环境变量或自动生成密钥

#### 配置

```bash
# 自定义加密密钥（可选，不提供则自动生成）
COOKIE_ENCRYPTION_KEY=your-32-byte-base64-key

# Cookie 过期时间（小时）
COOKIE_EXPIPTION_HOURS=24
```

#### 生成加密密钥

```bash
# 生成 Base64 编码的 32 字节密钥
openssl rand -base64 32
```

#### 加密状态检查

```bash
curl http://localhost:8000/api/download/encryption-status
```

响应示例：
```json
{
  "encryption_enabled": true,
  "key_from_env": false,
  "key_file_exists": true,
  "cookie_expiration_hours": 24
}
```

#### 安全警告

⚠️ **重要提示**：
- 加密密钥存储在 `~/.bingo-downloader/.encryption_key`
- 生产环境应使用专业的密钥管理服务
- 定期审计安全配置

---

### 4. CORS 配置

CORS 配置现在更加严格，默认只允许本地访问。

#### 配置

```bash
# 允许的来源（逗号分隔）
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# 允许凭据
CORS_ALLOW_CREDENTIALS=true

# 允许的 HTTP 方法
CORS_ALLOW_METHODS=GET,POST,OPTIONS

# 允许的 Headers
CORS_ALLOW_HEADERS=Content-Type,Authorization,X-API-Key
```

#### 生产环境示例

```bash
# 只允许特定域名
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# 禁用凭据（如果不需要）
CORS_ALLOW_CREDENTIALS=false
```

⚠️ **不要在生产环境使用 `*` 允许所有来源！**

---

## 安装说明

### 1. 安装依赖

```bash
cd web/backend
pip install -r requirements.txt
```

新增的安全依赖：
- `cryptography>=41.0.0` - Cookie 加密

### 2. 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置
nano .env
```

### 3. 生成 API Keys（可选）

如果启用 API Key 认证：

```bash
# 生成 API Key
API_KEY=$(openssl rand -hex 32)

# 添加到 .env
echo "API_KEY_ENABLED=true" >> .env
echo "API_KEYS=$API_KEY" >> .env
```

### 4. 启动服务

```bash
# 开发模式
python -m web.backend.main

# 或使用 uvicorn
uvicorn web.backend.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 测试安全功能

### 测试 API Key 认证

```bash
# 应该失败（无 API Key）
curl -X POST http://localhost:8000/api/download/start \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=xxx"}'

# 应该成功（有 API Key）
curl -X POST http://localhost:8000/api/download/start \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=xxx"}'
```

### 测试速率限制

```bash
# 快速发送多个请求
for i in {1..70}; do
  curl http://localhost:8000/health &
done
wait

# 应该收到 429 响应
```

### 测试 Cookie 加密

```bash
# 检查加密状态
curl http://localhost:8000/api/download/encryption-status

# 授权 cookies
curl -X POST "http://localhost:8000/api/download/authorize-cookies?browser=chrome"

# 检查加密的 cookie 文件
cat ~/.bingo-downloader/cookies/chrome_cookies.txt
# 应该看到 base64 编码的加密数据，而不是纯文本
```

---

## 最佳实践

### 开发环境

```bash
# .env
API_KEY_ENABLED=false
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
CORS_ORIGINS=http://localhost:8000,http://localhost:3000
COOKIE_ENCRYPTION_KEY=  # 留空，自动生成
```

### 生产环境

```bash
# .env
API_KEY_ENABLED=true
API_KEYS=<生成的安全密钥>
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=60
CORS_ORIGINS=https://yourdomain.com
COOKIE_ENCRYPTION_KEY=<生成的加密密钥>
COOKIE_EXPIRATION_HOURS=24
```

### 安全清单

- [ ] 启用 API Key 认证
- [ ] 配置速率限制
- [ ] 限制 CORS 来源
- [ ] 使用 HTTPS（生产环境）
- [ ] 定期轮换 API Keys
- [ ] 使用安全的密钥管理服务
- [ ] 审查和更新依赖项
- [ ] 启用日志监控
- [ ] 实施 WAF（Web 应用防火墙）

---

## 故障排除

### 问题：API Key 认证失败

**错误**：`401 Unauthorized` - API key is missing

**解决方案**：
1. 检查 `API_KEY_ENABLED=true`
2. 确保请求包含 `X-API-Key` header
3. 验证 API Key 在 `API_KEYS` 列表中

### 问题：速率限制过于严格

**错误**：`429 Too Many Requests`

**解决方案**：
1. 增加 `RATE_LIMIT_REQUESTS` 值
2. 或增加 `RATE_LIMIT_WINDOW` 时间
3. 或禁用速率限制（不推荐）

### 问题：Cookie 加密失败

**错误**：`cryptography module not available`

**解决方案**：
```bash
pip install cryptography>=41.0.0
```

### 问题：CORS 错误

**错误**：浏览器显示 CORS 策略错误

**解决方案**：
1. 检查 `CORS_ORIGINS` 包含前端域名
2. 确保使用正确的协议（http/https）
3. 检查 `CORS_ALLOW_CREDENTIALS` 设置

---

## 向后兼容性

所有安全功能都是**可选的**，默认配置保持向后兼容：

- API Key 认证：默认**禁用**
- 速率限制：默认**启用**，但限制宽松
- Cookie 加密：自动**启用**（如果 cryptography 已安装）
- CORS：默认允许 localhost

---

## 参考资料

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Cryptography Documentation](https://cryptography.io/)
