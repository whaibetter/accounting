# 部署指南

## 环境说明

本项目支持两种部署环境：

| 环境 | 前端地址 | 后端地址 | 用途 |
|------|---------|---------|------|
| 本地开发 | http://localhost:3000/accountig/ | http://127.0.0.1:8000 | 开发调试 |
| 远程服务器 | http://117.72.196.45/accountig/ | http://117.72.196.45:8000 | 生产环境 |

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
- 前端: http://localhost:3000/accountig/
- 后端: http://127.0.0.1:8000
- API文档: http://127.0.0.1:8000/docs

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
| `.env.development` | 本地开发 | http://127.0.0.1:8000 |
| `.env.production` | 生产环境 | 使用 Nginx 代理 |

### 后端配置

后端配置存储在 `server/data/` 目录：
- `accounting.db` - SQLite 数据库
- `llm_config.json` - AI 大模型配置
- `.access_password` - 访问密码

---

## 常见问题

### 1. 前端无法连接后端

**本地开发:**
- 确认后端服务已启动 (http://127.0.0.1:8000/health)
- 检查 `.env.development` 中的 `API_TARGET` 配置

**远程服务器:**
- 检查 Nginx 配置是否正确
- 确认后端服务运行中: `systemctl status accounting`

### 2. Android 无法连接本地服务器

- 确保后端服务在本机运行
- 模拟器使用 `10.0.2.2` 而非 `localhost`
- 真机需要使用电脑的局域网 IP

### 3. 查看后端日志

```bash
# 远程服务器
ssh root@117.72.196.45 "journalctl -u accounting -f"

# 本地开发
cd server
python view_logs.py -f
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
