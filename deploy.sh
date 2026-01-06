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
    # 1. 停止容器 (保留数据卷以保护核心数据)
    if [ -d "/opt/16lily" ]; then
        cd /opt/16lily
        echo "🛑 正在停止容器 (保留数据卷)..."
        docker compose -f docker-compose.prod.yml down 2>/dev/null
    fi

    # 2. 准备更新目录
    echo "📂 正在准备代码更新目录 (保护 .env.prod 和数据库卷)..."
    # 严格保护 postgres_data 目录 (核心数据库文件所在处)
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

    # 5. 启动并构建容器 (强制无缓存构建以彻底剔除 Mock 数据)
     echo "🏗️ 正在强制无缓存重新构建镜像..."
     docker compose -f docker-compose.prod.yml build --no-cache
     echo "🚀 正在启动容器..."
     docker compose -f docker-compose.prod.yml up -d --force-recreate
     echo "🔄 强制重启后端服务以确保代码生效..."
     docker compose -f docker-compose.prod.yml restart web
    
    # 6. 等待后端启动
    echo "⏳ 等待后端服务启动 (15s)..."
    sleep 15

    # 7. 初始化数据库
    # 使用更通用的方式获取 web 容器 ID
    WEB_CONTAINER=$(docker ps --format "{{.Names}}" | grep "web" | head -n 1)
    if [ -n "$WEB_CONTAINER" ]; then
        echo "🔎 找到 Web 容器: $WEB_CONTAINER"
        echo "🧹 正在精准清理业务脏数据 (保留用户/部门/岗位)..."
        docker exec $WEB_CONTAINER python clean_business_data.py
        
        echo "⚙️ 执行数据库迁移..."
        docker exec $WEB_CONTAINER python manage.py migrate
        
        echo "👤 创建初始管理员 (admin/admin123456)..."
        docker exec $WEB_CONTAINER python manage.py shell -c "from django.contrib.auth.models import User; u=User.objects.filter(username='admin').first(); u.set_password('admin123456') if u else User.objects.create_superuser('admin', 'admin@example.com', 'admin123456'); u.save() if u else None"
        
        # 导入组织架构种子数据 (如果存在)
        if [ -f "core_structure_seed.json" ]; then
            echo "🌱 导入组织架构种子数据..."
            docker exec $WEB_CONTAINER python manage.py loaddata core_structure_seed.json || echo "⚠️ 种子数据导入有冲突，已跳过。"
        fi

        echo "🔍 验证后端 API 返回数据..."
        TOKEN=$(docker exec $WEB_CONTAINER python manage.py shell -c "from rest_framework.authtoken.models import Token; from django.contrib.auth.models import User; u=User.objects.get(username='admin'); t,_=Token.objects.get_or_create(user=u); print(t.key)")
        API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Token $TOKEN" http://localhost:8000/api/dashboard/stats/)
        if [ "$API_STATUS" == "200" ]; then
            STATS=$(curl -s -H "Authorization: Token $TOKEN" http://localhost:8000/api/dashboard/stats/)
            echo "✅ API 响应正常: $STATS"
        else
            echo "❌ API 响应异常, 状态码: $API_STATUS"
        fi

        echo "✅ 部署与初始化全部完成！"
    else
        echo "❌ 启动失败，请检查 docker logs."
    fi
EOF

echo "✨ 所有操作已完成。请在浏览器中强制刷新 (Ctrl+F5) 查看效果。"
