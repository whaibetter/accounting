"""
FastAPI应用主入口模块。

功能描述：
    - 创建FastAPI应用实例
    - 注册所有API路由
    - 配置CORS跨域支持
    - 配置应用启动时的事件处理（数据库初始化）
    - 提供健康检查接口

使用方法：
    通过 uvicorn 启动:
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

    或通过 run.py 启动:
        python run.py

接口文档：
    启动后访问 http://localhost:8000/docs 查看自动生成的Swagger文档
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import account, bill, category, tag, statistics, export


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理。

    启动时执行数据库初始化（创建表、插入预设数据）。
    """
    init_db()
    yield


app = FastAPI(
    title="记账软件API",
    description="个人记账软件后端API，支持记账、资金管理、统计分析等功能",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(account.router)
app.include_router(bill.router)
app.include_router(category.router)
app.include_router(tag.router)
app.include_router(statistics.router)
app.include_router(export.router)


@app.get("/health", tags=["系统"])
def health_check():
    """
    健康检查接口。

    Returns:
        dict: {"status": "ok"}
    """
    return {"status": "ok"}
