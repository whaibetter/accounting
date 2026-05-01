# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

跨平台个人记账应用，支持 Web 端和 Android 端，共用后端服务。核心功能包括基础记账、AI智能记账（自然语言解析）、多账户管理、数据分析统计。

## Tech Stack

| 端 | 技术 |
|---|------|
| Web前端 | Vue 3 + Pinia + Vite + TypeScript + Chart.js |
| 后端 | Python + FastAPI + SQLAlchemy + SQLite |
| Android | Kotlin + Jetpack Compose + Material3 |

## Quick Start

### 后端

```bash
cd server
pip install -r requirements.txt
python run.py
# 访问 http://localhost:8000/docs 查看API文档
```

### Web前端

```bash
cd web
npm install
npm run dev
# 访问 http://localhost:3000/accounting/
```

## Project Structure

```
accounting/
├── server/              # 后端服务 (FastAPI)
│   ├── app/
│   │   ├── models.py     # SQLAlchemy数据模型
│   │   ├── schemas.py    # Pydantic请求/响应模型
│   │   ├── crud.py       # 数据访问层
│   │   ├── auth.py       # JWT认证
│   │   ├── llm_service.py # LLM服务集成
│   │   ├── llm_config.py # LLM配置管理
│   │   ├── routers/      # API路由模块
│   │   └── middleware.py # 中间件
│   ├── data/            # SQLite数据库文件
│   ├── logs/            # 应用日志
│   └── run.py           # 启动入口
├── web/                 # Web前端
│   ├── src/
│   │   ├── views/       # 页面组件
│   │   ├── stores/      # Pinia状态管理
│   │   ├── api/         # API调用封装
│   │   └── router/      # 路由配置
│   └── vite.config.ts
└── android/             # Android应用
```

## Key Architecture Notes

### 后端架构
- **路由模块**: `server/app/routers/` 下按功能划分（auth, bill, account, category, tag, statistics, llm, admin等）
- **认证**: JWT token机制，通过`dependencies.py`中的`require_auth`依赖注入
- **LLM集成**: 支持多AI提供商（OpenRouter等），配置存储在`llm_config.py`
- **审计日志**: `audit_service.py`记录操作日志到`OperationLog`模型

### 前端架构
- **状态管理**: Pinia store（auth.js, data.js, theme.js）
- **API封装**: `src/api/` 统一管理后端请求
- **路由**: `src/router/` 定义页面路由
- **基础路径**: Web应用部署在 `/accounting/` 子路径下

### 数据库
- SQLite存储在 `server/data/` 目录
- 核心模型：User, Account, Bill, Category, Tag, BillTag, OperationLog, SystemConfig

## Development Notes

- 后端环境变量通过 `.env.development` / `.env.production` 管理
- Web前端开发服务器默认端口3000，代理API到后端8000端口
- API文档仅在开发环境启用（`ENABLE_DOCS`配置）
- 生产环境部署参考 `DEPLOY.md`
