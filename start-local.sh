#!/bin/bash

echo "========================================="
echo "  记账软件 - 本地开发环境启动"
echo "========================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python，请先安装 Python 3.10+"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "[错误] 未找到 Node.js，请先安装 Node.js 18+"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 启动后端
echo "[1/4] 启动后端服务..."
cd "$SCRIPT_DIR/server"
if [ ! -d "venv" ]; then
    echo "      创建虚拟环境..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt -q 2>/dev/null
echo "      后端服务启动中... (http://127.0.0.1:8000)"
python run.py &
BACKEND_PID=$!

# 等待后端启动
echo ""
echo "[2/4] 等待后端服务就绪..."
sleep 3

# 启动前端
echo ""
echo "[3/4] 启动前端服务..."
cd "$SCRIPT_DIR/web"
if [ ! -d "node_modules" ]; then
    echo "      安装前端依赖..."
    npm install
fi
echo "      前端服务启动中... (http://localhost:3000/accountig/)"
npm run dev &
FRONTEND_PID=$!

# 等待前端启动
echo ""
echo "[4/4] 等待前端服务就绪..."
sleep 5

echo ""
echo "========================================="
echo "  本地开发环境已启动！"
echo "========================================="
echo ""
echo "  前端: http://localhost:3000/accountig/"
echo "  后端: http://127.0.0.1:8000"
echo "  API文档: http://127.0.0.1:8000/docs"
echo ""
echo "  按 Ctrl+C 停止服务"
echo "========================================="
echo ""

# 打开浏览器 (macOS)
if command -v open &> /dev/null; then
    open http://localhost:3000/accountig/
fi

# 等待中断信号
trap "echo ''; echo '停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM
wait
