@echo off
chcp 65001 >nul
echo =========================================
echo   记账软件 - 本地开发环境启动
echo =========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

:: 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)

:: 启动后端
echo [1/4] 启动后端服务...
cd /d "%~dp0server"
if not exist "venv" (
    echo       创建虚拟环境...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt -q 2>nul
start "记账软件后端" cmd /k "venv\Scripts\python.exe run.py"
echo       后端服务启动中... (http://127.0.0.1:8000)

:: 等待后端启动
echo.
echo [2/4] 等待后端服务就绪...
timeout /t 3 /nobreak >nul

:: 启动前端
echo.
echo [3/4] 启动前端服务...
cd /d "%~dp0web"
if not exist "node_modules" (
    echo       安装前端依赖...
    npm install
)
start "记账软件前端" cmd /k "npm run dev"
echo       前端服务启动中... (http://localhost:3000/accountig/)

:: 等待前端启动
echo.
echo [4/4] 等待前端服务就绪...
timeout /t 5 /nobreak >nul

echo.
echo =========================================
echo   本地开发环境已启动！
echo =========================================
echo.
echo   前端: http://localhost:3000/accountig/
echo   后端: http://127.0.0.1:8000
echo   API文档: http://127.0.0.1:8000/docs
echo.
echo   按 Ctrl+C 停止服务
echo =========================================
echo.

:: 打开浏览器
start http://localhost:3000/accountig/

pause
