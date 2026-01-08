#!/bin/bash

# =================================================================
# 🚀 自动化部署脚本 - 适用于 1Panel + 阿里云 2C/2G 环境
# =================================================================

# --- 配置区 (请根据实际情况修改) ---
SERVER_IP="47.94.22.64"
SERVER_USER="root"
REMOTE_DIR="/opt/16lily"
PROJECT_NAME="16lily"

# --- 1. 本地打包 (深度清洗) ---
echo "📦 正在本地打包项目 (进行深度清洗)..."
rm -f project.zip
# 排除项说明：
# - .git: 版本控制文件
# - __pycache__, .pyc: Python 编译缓存
# - venv, .venv: 本地虚拟环境
# - node_modules: 前端依赖包
# - .env, .env.local: 本地敏感配置文件 (非常重要！)
# - db.sqlite3: 本地测试数据库
# - *.zip, *.log: 压缩包和日志
# - frontend_dashboard/dist: 前端编译产物 (由服务器 Docker 重新编译)
zip -r project.zip . -x \
    "*.git*" \
    "*__pycache__*" \
    "venv/*" \
    ".venv/*" \
    "*node_modules*" \
    "*.DS_Store*" \
    "*.zip" \
    "*.log" \
    ".env*" \
    "db.sqlite3" \
    "frontend_dashboard/dist*" \
    "static/*" \
    "media/*"

if [ $? -ne 0 ]; then
    echo "❌ 打包失败，请检查 zip 命令是否正常"
    exit 1
fi

# --- 2. 上传到服务器 ---
echo "📤 正在上传项目到服务器 $SERVER_IP ..."
# 确保远程目录存在并清空旧包
ssh $SERVER_USER@$SERVER_IP "rm -f /tmp/project.zip"
scp project.zip $SERVER_USER@$SERVER_IP:/tmp/

if [ $? -ne 0 ]; then
    echo "❌ 上传失败，请检查 SSH 连接或 IP 地址"
    exit 1
fi

# --- 3. 远程部署 (彻底清理模式) ---
echo "🚀 正在远程清理并重新启动..."
ssh $SERVER_USER@$SERVER_IP << 'EOF'
    # 1. 彻底停止并清理干扰容器 (防止 1Panel 缓存幽灵代码)
    if [ -d "/opt/16lily" ]; then
        cd /opt/16lily
        echo "🛑 正在深度清理干扰容器并停止旧镜像..."
        docker stop 16lily-dashboard-1 2>/dev/null || true
        docker rm 16lily-dashboard-1 2>/dev/null || true
        docker compose -f docker-compose.prod.yml down --rmi all --remove-orphans 2>/dev/null
    fi

    # 2. 准备更新目录
    echo "📂 清理目录 (保护核心数据)..."
    find /opt/16lily -maxdepth 1 ! -name '.env.prod' ! -name 'postgres_data' ! -name 'docker-data' ! -name '.' -exec rm -rf {} + 2>/dev/null
    rm -rf /opt/16lily/docker-data/nginx/html/* 2>/dev/null
    mkdir -p /opt/16lily
    
    # 3. 移动新包并解压
    if [ -f "/tmp/project.zip" ]; then
        mv /tmp/project.zip /opt/16lily/
        cd /opt/16lily
        echo "📦 正在解压新版本代码..."
        unzip -o -q project.zip
    else
        echo "❌ 错误: 未在 /tmp 找到上传的 project.zip"
        exit 1
    fi
    
    # 4. 恢复 .env.prod (如果不存在则创建默认)
    if [ ! -f .env.prod ]; then
        echo "📝 创建默认生产环境配置..."
        cat > .env.prod << EOT
DEBUG=0
SECRET_KEY=django-insecure-production-key-47-94-22-64
ALLOWED_HOSTS=*
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=opportunity_db
SQL_USER=postgres
SQL_PASSWORD=postgres
SQL_HOST=db
SQL_PORT=5432
EOT
    fi

    # 5. 启动并构建容器
    echo "🏗️ 强制全新构建 (彻底剔除缓存)..."
    docker image prune -af 2>/dev/null # 清理所有旧镜像
    docker compose -f docker-compose.prod.yml build --no-cache
    docker compose -f docker-compose.prod.yml up -d --force-recreate
    
    # 6. 等待后端启动并检查健康状态
    echo "⏳ 等待后端服务启动 (20s)..."
    sleep 20
    
    # 检查 web 容器是否在线
    if ! docker ps | grep -q "web"; then
        echo "❌ 警告: web 容器未能正常启动，尝试查看日志..."
        docker compose -f docker-compose.prod.yml logs web | tail -n 20
        # 强制重启一次
        docker compose -f docker-compose.prod.yml restart web
        sleep 10
    fi

    # 7. 验证后端代码逻辑 (使用 manage.py shell 避免环境错误)
    echo "🔍 验证云端后端代码逻辑..."
    docker compose -f docker-compose.prod.yml exec -T web python manage.py shell -c "from core.serializers import AIConfigurationSerializer; print('✅ AI Serializer OK')"
    
    # 8. 彻底清理 Nginx 静态文件缓存 (解决前端不更新问题)
    echo "🧹 强制刷新前端静态资源..."
    docker compose -f docker-compose.prod.yml exec -T nginx rm -rf /usr/share/nginx/html/* 2>/dev/null
    docker compose -f docker-compose.prod.yml restart nginx

    # 9. 数据库迁移
    echo "🗄️ 执行数据库迁移..."
    docker compose -f docker-compose.prod.yml exec -T web python manage.py migrate --noinput

    # 10. (已禁用) 清理脏数据 - 用户要求保留所有业务数据
    # if [ -f "clean_business_data.py" ]; then
    #     docker compose -f docker-compose.prod.yml exec -T web python clean_business_data.py
    # fi
    
    # 11. 消息通知修复：仅清理导致小铃铛显示异常的无效数据 (无标题或无归属人的通知)
    echo "🔔 正在修复小铃铛通知显示异常..."
    docker compose -f docker-compose.prod.yml exec -T web python manage.py shell -c "from core.models import Notification; Notification.objects.filter(title='').delete(); Notification.objects.filter(recipient__isnull=True).delete(); print('✅ 通知数据修复完成')"

    echo "✅ 阿里云环境 (47.94.22.64) 部署与清洗完成！"
EOF

# --- 4. 清理本地包 ---
rm -f project.zip
echo "✨ 部署流程结束。"
