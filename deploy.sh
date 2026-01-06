#!/bin/bash

# =================================================================
# 🚀 自动化部署脚本 - 适用于 1Panel + 阿里云 2C/2G 环境
# =================================================================

# --- 配置区 (请根据实际情况修改) ---
SERVER_IP="47.94.22.64"
SERVER_USER="root"
REMOTE_DIR="/opt/16lily"
PROJECT_NAME="opportunity_system"

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
    # 1. 停止并彻底删除旧容器、镜像和数据卷
    if [ -d "/opt/16lily" ]; then
        cd /opt/16lily
        echo "🛑 正在停止并清理旧容器与数据卷..."
        docker compose -f docker-compose.prod.yml down -v --rmi local 2>/dev/null
    fi

    # 2. 强力清空远程目录
    echo "🗑️ 正在清空远程目录 /opt/16lily ..."
    rm -rf /opt/16lily
    mkdir -p /opt/16lily
    
    # 3. 移动新包并解压
    if [ -f "/tmp/project.zip" ]; then
        mv /tmp/project.zip /opt/16lily/
        cd /opt/16lily
        echo "📦 正在解压新版本..."
        unzip -q project.zip
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

    # 5. 启动服务
    echo "🏗️ 正在构建并启动新容器..."
    docker compose -f docker-compose.prod.yml up -d --build
    
    # 6. 等待数据库就绪
    echo "⏳ 等待数据库初始化 (10s)..."
    sleep 10

    # 7. 初始化数据库
    WEB_CONTAINER=$(docker compose -f docker-compose.prod.yml ps -q web)
    if [ -n "$WEB_CONTAINER" ]; then
        echo "⚙️ 执行数据库迁移..."
        docker exec $WEB_CONTAINER python manage.py migrate
        
        echo "👤 创建初始管理员 (admin/admin123456)..."
        docker exec $WEB_CONTAINER python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')
    print('Admin created successfully.')
else:
    u = User.objects.get(username='admin')
    u.set_password('admin123456')
    u.is_superuser = True
    u.is_staff = True
    u.save()
    print('Admin password reset.')
"
        
        # 导入组织架构种子数据 (如果存在)
        if [ -f "core_structure_seed.json" ]; then
            echo "🌱 导入组织架构种子数据..."
            # 忽略由于数据冲突导致的错误，确保脚本继续
            docker exec $WEB_CONTAINER python manage.py loaddata core_structure_seed.json || echo "⚠️ 种子数据导入有冲突，已跳过。"
        fi

        echo "✅ 部署与初始化全部完成！"
    else
        echo "❌ 启动失败，请检查 docker logs."
    fi
EOF

echo "✨ 所有操作已完成。"
