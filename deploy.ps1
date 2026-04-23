$ErrorActionPreference = "Stop"

$REMOTE_HOST = if ($env:REMOTE_HOST) { $env:REMOTE_HOST } else { "117.72.196.45" }
$REMOTE_USER = if ($env:REMOTE_USER) { $env:REMOTE_USER } else { "root" }
$SSH_KEY = if ($env:SSH_KEY) { $env:SSH_KEY } else { "C:\Users\whaif\Documents\priKey\whjd.pem" }
$REMOTE_BACKEND_PATH = if ($env:REMOTE_BACKEND_PATH) { $env:REMOTE_BACKEND_PATH } else { "/opt/accounting/server" }
$REMOTE_FRONTEND_PATH = if ($env:REMOTE_FRONTEND_PATH) { $env:REMOTE_FRONTEND_PATH } else { "/opt/accounting/web" }

$SSH_OPTS = "-i", $SSH_KEY, "-o", "StrictHostKeyChecking=no"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  记账软件 - 一键部署脚本" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  目标: $REMOTE_USER@$REMOTE_HOST" -ForegroundColor Yellow
Write-Host "  密钥: $SSH_KEY" -ForegroundColor Yellow
Write-Host "  后端目录: $REMOTE_BACKEND_PATH" -ForegroundColor Yellow
Write-Host "  前端目录: $REMOTE_FRONTEND_PATH" -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "  确认部署? [Y/n]"
if ($confirm -eq "n" -or $confirm -eq "N") {
    Write-Host "  已取消" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "[1/6] 同步后端代码到远程服务器..." -ForegroundColor Green
& scp @SSH_OPTS -r "$PSScriptRoot/server/app" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_BACKEND_PATH}/"
& scp @SSH_OPTS "$PSScriptRoot/server/requirements.txt" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_BACKEND_PATH}/"
& scp @SSH_OPTS "$PSScriptRoot/server/run.py" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_BACKEND_PATH}/"
Write-Host "  ✓ 后端代码同步完成" -ForegroundColor Green

Write-Host ""
Write-Host "[2/6] 安装/更新 Python 依赖..." -ForegroundColor Green
& ssh @SSH_OPTS "$REMOTE_USER@$REMOTE_HOST" "cd $REMOTE_BACKEND_PATH && pip3 install -r requirements.txt -q"
Write-Host "  ✓ 依赖安装完成" -ForegroundColor Green

Write-Host ""
Write-Host "[3/6] 上传 systemd 服务配置..." -ForegroundColor Green
& scp @SSH_OPTS "$PSScriptRoot/accounting.service" "${REMOTE_USER}@${REMOTE_HOST}:/etc/systemd/system/accounting.service"
& ssh @SSH_OPTS "$REMOTE_USER@$REMOTE_HOST" "sed -i 's|WorkingDirectory=.*|WorkingDirectory=$REMOTE_BACKEND_PATH|' /etc/systemd/system/accounting.service"
Write-Host "  ✓ 服务配置已更新" -ForegroundColor Green

Write-Host ""
Write-Host "[4/6] 重启后端服务..." -ForegroundColor Green
& ssh @SSH_OPTS "$REMOTE_USER@$REMOTE_HOST" "systemctl daemon-reload && systemctl restart accounting && sleep 2"
Write-Host "  ✓ 后端服务已重启" -ForegroundColor Green

Write-Host ""
Write-Host "[5/6] 部署前端资源..." -ForegroundColor Green
& ssh @SSH_OPTS "$REMOTE_USER@$REMOTE_HOST" "mkdir -p $REMOTE_FRONTEND_PATH"
& scp @SSH_OPTS -r "$PSScriptRoot/web/dist/*" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_FRONTEND_PATH}/"
Write-Host "  ✓ 前端资源已部署" -ForegroundColor Green

Write-Host ""
Write-Host "[6/6] 配置 Nginx..." -ForegroundColor Green
$NGINX_CONF = @"
server {
    listen 80;
    listen [::]:80;
    server_name _;

    location /accountig/api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
        proxy_read_timeout 60s;
    }

    location /accountig/ {
        alias $REMOTE_FRONTEND_PATH/;
        index index.html;
        try_files `$uri `$uri/ /accountig/index.html;
    }
}
"@

$tempNginxFile = "$env:TEMP\accounting-nginx.conf"
$NGINX_CONF | Out-File -FilePath $tempNginxFile -Encoding UTF8
& scp @SSH_OPTS $tempNginxFile "${REMOTE_USER}@${REMOTE_HOST}:/etc/nginx/sites-available/accounting"
& ssh @SSH_OPTS "$REMOTE_USER@$REMOTE_HOST" "ln -sf /etc/nginx/sites-available/accounting /etc/nginx/sites-enabled/accounting && nginx -t && systemctl reload nginx"
Remove-Item $tempNginxFile -Force
Write-Host "  ✓ Nginx 配置完成" -ForegroundColor Green

Write-Host ""
Write-Host "验证部署..." -ForegroundColor Green
$health = & ssh @SSH_OPTS "$REMOTE_USER@$REMOTE_HOST" "curl -s http://localhost:8000/health"
if ($health -match '"ok"') {
    Write-Host "  ✓ 后端健康检查通过: $health" -ForegroundColor Green
} else {
    Write-Host "  ✗ 后端健康检查失败: $health" -ForegroundColor Red
}

$frontend = & ssh @SSH_OPTS "$REMOTE_USER@$REMOTE_HOST" "curl -s -o /dev/null -w '%{http_code}' http://localhost/accountig/"
if ($frontend -eq "200") {
    Write-Host "  ✓ 前端页面访问正常 (HTTP $frontend)" -ForegroundColor Green
} else {
    Write-Host "  ✗ 前端页面访问异常 (HTTP $frontend)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  部署完成！" -ForegroundColor Cyan
Write-Host "  前端: http://$REMOTE_HOST/accountig/" -ForegroundColor Yellow
Write-Host "  后端: http://$REMOTE_HOST:8000" -ForegroundColor Yellow
Write-Host "  健康检查: http://$REMOTE_HOST:8000/health" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Cyan
