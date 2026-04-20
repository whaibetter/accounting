"""
应用启动脚本。

使用方法：
    python run.py

参数说明：
    --host: 绑定主机地址 (默认 0.0.0.0，允许局域网访问)
    --port: 绑定端口 (默认 8000)
    --reload: 开发热重载 (开发模式默认开启)

启动后访问：
    - API: http://localhost:8000
    - Swagger文档: http://localhost:8000/docs
    - ReDoc文档: http://localhost:8000/redoc
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
