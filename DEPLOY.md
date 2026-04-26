# 部署指南

## 环境说明

本项目支持两种部署环境，通过环境变量和配置文件实现完全隔离：

| 环境 | 前端地址 | 后端地址 | 配置文件 | 用途 |
|------|---------|---------|---------|------|
| 本地开发 | http://localhost:3000/ | http://127.0.0.1:8000 | `.env.development` | 开发调试 |
| 远程服务器 | http://117.72.196.45/accountig/ | http://117.72.196.45:8000 | `.env.production` | 生产环境 |

> **环境隔离机制**：本地开发环境自动连接本地数据库和服务，不会产生对远程服务器的任何网络请求。远程服务器作为独立系统运行，使用自身配置和资源。

---

## 本地开发环境

### 快速启动

**Windows:**
```bash
# 双击运行
start-local.bat

# 或命令行运行
.\start-local.bat
```

**macOS/Linux:**
```bash
chmod +x start-local.sh
./start-local.sh
```

### 手动启动

**1. 启动后端**
```bash
cd server
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

**2. 启动前端**
```bash
cd web
npm install
npm run dev
```

### 访问地址
- 前端: http://localhost:3000/
- 后端: http://127.0.0.1:8000
- API文档: http://127.0.0.1:8000/docs
- 健康检查: http://127.0.0.1:8000/health

---

## 远程服务器部署

### 前置条件

服务器需要安装：
- Python 3.10+
- Node.js 18+ (仅构建时需要)
- Nginx
- systemd

### 一键部署

**Windows:**
```powershell
.\deploy.ps1
```

**Linux/macOS:**
```bash
chmod +x deploy.sh
./deploy.sh
```

### 部署流程

1. 构建前端生产版本
2. 同步后端代码到服务器
3. 安装 Python 依赖
4. 重启后端服务
5. 部署前端静态文件
6. 配置 Nginx

### 访问地址
- 前端: http://117.72.196.45/accountig/
- 后端: http://117.72.196.45:8000
- 健康检查: http://117.72.196.45:8000/health

---

## 环境配置隔离

### 环境切换机制

通过 `APP_ENV` 环境变量或 `.env.*` 文件控制运行环境：

| 配置项 | 本地开发 | 远程服务器 |
|--------|---------|-----------|
| `APP_ENV` | `development` | `production` |
| 数据库 | 本地 SQLite (`server/data/accounting.db`) | 服务器本地 SQLite |
| CORS 来源 | `http://localhost:3000` | 生产域名 |
| API 文档 | 启用 (`/docs`) | 禁用 |
| 前端 API 代理 | Vite 代理到 `127.0.0.1:8000` | Nginx 反向代理 |

### 后端环境配置

后端根据 `APP_ENV` 自动加载对应的 `.env` 文件：

- `server/.env.development` — 本地开发配置
- `server/.env.production` — 生产环境配置

启动时指定环境：
```bash
# 本地开发（默认）
python run.py

# 生产环境
APP_ENV=production python run.py
```

### 前端环境配置

前端使用 Vite 的环境变量机制：

- `web/.env.development` — 本地开发（API 代理到本地后端）
- `web/.env.production` — 生产环境（API 通过 Nginx 代理）

关键变量：
- `VITE_API_TARGET` — API 目标地址（留空使用 Vite 代理，本地开发时务必留空）
- `VITE_APP_ENV` — 环境标识（`development` / `production`）

### 环境隔离验证

本地开发环境确保不连接远程服务器：
1. 前端 `.env.development` 中 `VITE_API_TARGET` 留空，使用 Vite 代理
2. Vite 代理配置 `target: 'http://127.0.0.1:8000'`，仅连接本地
3. 后端 CORS 仅允许 `localhost:3000` 来源

---

## 密码管理系统

### 密码存储机制

密码使用 **bcrypt** 算法哈希后存储在数据库 `system_config` 表中：

| 特性 | 旧版 | 新版 |
|------|------|------|
| 哈希算法 | SHA-256（无盐） | bcrypt（自带盐，rounds=12） |
| 存储位置 | 文件 `.access_password` | 数据库 `system_config` 表 |
| JWT 密钥 | 文件 `.secret_key` | 数据库 `system_config` 表 |
| 密码强度 | 无校验 | 字母+数字，≥6位 |

### 迁移说明

首次启动新版后端时，系统自动执行迁移：
1. 读取旧文件 `.access_password` 和 `.secret_key`
2. 将内容写入数据库 `system_config` 表
3. 旧文件重命名为 `.bak` 备份
4. 旧 SHA-256 密码在首次验证成功后自动升级为 bcrypt

### 命令行密码管理工具

使用 `manage_password.py` 管理密码：

```bash
# 重置密码（无需旧密码）
python manage_password.py reset --password NewPass123

# 交互式重置（不传密码参数则交互输入）
python manage_password.py reset

# 修改密码（需验证旧密码）
python manage_password.py change --old OldPass123 --new NewPass456

# 检查密码强度
python manage_password.py check --password TestPass123

# 查看密码存储状态
python manage_password.py info
```

### 密码强度要求

- 长度 6~128 位
- 必须同时包含字母和数字
- 不能包含中文字符
- 新密码不能与旧密码相同

### 审计日志

所有密码操作记录在 `server/logs/password_audit.log`，包含：
- 操作时间
- 操作结果（SUCCESS / FAILED）
- 操作类型（RESET / CHANGE）
- 详细信息

---

## 认证 API 接口

### POST /api/v1/auth/login — 密码登录

**请求体：**
```json
{
  "password": "your_password"
}
```

**成功响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

**失败响应：** `401` 密码错误

---

### POST /api/v1/auth/change-password — 修改密码

**请求体：**
```json
{
  "old_password": "current_password",
  "new_password": "new_password"
}
```

**成功响应：**
```json
{
  "code": 200,
  "message": "密码修改成功",
  "data": null
}
```

**失败响应：** `400` 旧密码错误 / 密码强度不足 / 新旧密码相同

---

### POST /api/v1/auth/reset-password — 重置密码（需认证）

**请求头：** `Authorization: Bearer <access_token>`

**请求体：**
```json
{
  "new_password": "new_password"
}
```

**成功响应：**
```json
{
  "code": 200,
  "message": "密码重置成功",
  "data": null
}
```

**失败响应：** `400` 密码强度不足

---

## Android 应用配置

### 切换服务器环境

在 Android 应用的 **设置** 页面，可以切换服务器环境：

- **远程服务器**: 连接 117.72.196.45 (生产环境)
- **本地服务器**: 连接 10.0.2.2:8000 (开发调试)

> 注意：本地服务器模式需要在同一网络下运行后端服务，Android 模拟器使用 `10.0.2.2` 访问宿主机。

---

## 配置文件说明

### 前端环境变量

| 文件 | 用途 | API 地址 |
|------|------|---------|
| `web/.env.development` | 本地开发 | Vite 代理到 http://127.0.0.1:8000 |
| `web/.env.production` | 生产环境 | 使用 Nginx 代理 |

### 后端环境变量

| 文件 | 用途 | 关键配置 |
|------|------|---------|
| `server/.env.development` | 本地开发 | `APP_ENV=development`, `ENABLE_DOCS=true` |
| `server/.env.production` | 生产环境 | `APP_ENV=production`, `ENABLE_DOCS=false` |

### 后端数据文件

后端数据存储在 `server/data/` 目录：
- `accounting.db` — SQLite 数据库（含密码哈希和 JWT 密钥）
- `llm_config.json` — AI 大模型配置
- `.access_password.bak` — 旧密码文件备份（迁移后保留）
- `.secret_key.bak` — 旧密钥文件备份（迁移后保留）

---

## 常见问题

### 1. 前端无法连接后端

**本地开发:**
- 确认后端服务已启动 (http://127.0.0.1:8000/health)
- 检查 `web/.env.development` 中 `VITE_API_TARGET` 应为空
- 检查 Vite 代理配置 `vite.config.js` 中 target 为 `http://127.0.0.1:8000`

**远程服务器:**
- 检查 Nginx 配置是否正确
- 确认后端服务运行中: `systemctl status accounting`

### 2. 忘记密码

使用命令行工具重置：
```bash
python manage_password.py reset --password NewPass123
```

### 3. Android 无法连接本地服务器

- 确保后端服务在本机运行
- 模拟器使用 `10.0.2.2` 而非 `localhost`
- 真机需要使用电脑的局域网 IP

### 4. 查看后端日志

```bash
# 远程服务器
ssh root@117.72.196.45 "journalctl -u accounting -f"

# 本地开发
cd server
python view_logs.py -f
```

### 5. 查看密码审计日志

```bash
# 查看所有密码操作记录
cat server/logs/password_audit.log
```

---

## 服务管理命令

### 远程服务器

```bash
# 查看服务状态
systemctl status accounting

# 重启服务
systemctl restart accounting

# 查看日志
journalctl -u accounting -f

# 重载 Nginx
systemctl reload nginx
```
