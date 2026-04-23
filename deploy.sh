#!/usr/bin/env bash
set -e

echo "========================================="
echo "  记账软件后端 - 一键部署脚本"
echo "========================================="
echo ""

read -p "  服务器IP [117.72.196.45]: " REMOTE_HOST
REMOTE_HOST=${REMOTE_HOST:-117.72.196.45}

read -p "  登录用户 [root]: " REMOTE_USER
REMOTE_USER=${REMOTE_USER:-root}

read -p "  SSH密钥路径 [C:\\Users\\whaif\\Documents\\priKey\\whjd.pem]: " SSH_KEY
SSH_KEY=${SSH_KEY:-C:\\Users\\whaif\\Documents\\priKey\\whjd.pem}

read -p "  远程部署目录 [/opt/accounting/server]: " REMOTE_PATH
REMOTE_PATH=${REMOTE_PATH:-/opt/accounting/server}

SSH_OPTS="-i \"$SSH_KEY\" -o StrictHostKeyChecking=no"

echo ""
echo "  目标: $REMOTE_USER@$REMOTE_HOST"
echo "  密钥: $SSH_KEY"
echo "  目录: $REMOTE_PATH"
echo ""

read -p "  确认部署? [Y/n]: " CONFIRM
if [[ "$CONFIRM" == "n" || "$CONFIRM" == "N" ]]; then
    echo "  已取消"
    exit 0
fi

echo ""
echo "[1/5] 同步代码到远程服务器..."
scp $SSH_OPTS -r ./server/app $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/
scp $SSH_OPTS ./server/requirements.txt $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/
scp $SSH_OPTS ./server/run.py $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/
echo "  ✓ 代码同步完成"

echo ""
echo "[2/5] 安装/更新 Python 依赖..."
ssh $SSH_OPTS $REMOTE_USER@$REMOTE_HOST "cd $REMOTE_PATH && pip3 install -r requirements.txt -q"
echo "  ✓ 依赖安装完成"

echo ""
echo "[3/5] 确保 systemd 服务配置..."
scp $SSH_OPTS ./accounting.service $REMOTE_USER@$REMOTE_HOST:/etc/systemd/system/accounting.service
ssh $SSH_OPTS $REMOTE_USER@$REMOTE_HOST "sed -i 's|WorkingDirectory=.*|WorkingDirectory=$REMOTE_PATH|' /etc/systemd/system/accounting.service"
echo "  ✓ 服务配置已更新"

echo ""
echo "[4/5] 重启服务..."
ssh $SSH_OPTS $REMOTE_USER@$REMOTE_HOST "systemctl daemon-reload && systemctl restart accounting && sleep 2"
echo "  ✓ 服务已重启"

echo ""
echo "[5/5] 验证部署..."
HEALTH=$(ssh $SSH_OPTS $REMOTE_USER@$REMOTE_HOST "curl -s http://localhost:8000/health")
STATUS=$(echo $HEALTH | grep -o '"ok"' || true)

if [ "$STATUS" = '"ok"' ]; then
    echo "  ✓ 健康检查通过: $HEALTH"
else
    echo "  ✗ 健康检查失败: $HEALTH"
    exit 1
fi

echo ""
echo "========================================="
echo "  部署成功！"
echo "  API: http://$REMOTE_HOST:8000"
echo "  健康检查: http://$REMOTE_HOST:8000/health"
echo "========================================="
