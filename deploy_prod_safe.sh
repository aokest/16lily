#!/bin/bash

# =================================================================
# 🛡️ 安全部署脚本 (带全量备份与一键还原) - v1.2.1
# =================================================================
# 功能：
# 1. 自动备份云端数据库 (SQL Dump)
# 2. 自动备份云端代码目录
# 3. 生成云端一键还原脚本
# 4. 上传并部署新版本
# =================================================================

SERVER_IP="47.94.22.64"
SERVER_USER="root"
REMOTE_DIR="/opt/16lily"
BACKUP_DIR="/opt/16lily_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🔒 [Phase 1] 正在准备本地构建包..."

# 1. 本地打包 (排除敏感数据)
rm -f project_release.zip
zip -r -q project_release.zip . -x \
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
    "media/*" \
    "*.bak" \
    "cloud_data_export.json" \
    "local_backup_before_fix.sql"

if [ ! -f project_release.zip ]; then
    echo "❌ 打包失败！"
    exit 1
fi

echo "📤 [Phase 2] 连接服务器 $SERVER_IP 进行备份与部署..."
echo "⚠️  注意：如果询问密码，请输入服务器 root 密码"

# 2. 远程执行核心逻辑 (备份 -> 生成还原脚本 -> 部署)
ssh $SERVER_USER@$SERVER_IP "bash -s" << EOF
    set -e # 遇到错误立即停止

    # --- A. 准备备份目录 ---
    mkdir -p $BACKUP_DIR
    echo "💾 [Remote] 创建备份目录: $BACKUP_DIR"

    # --- B. 执行数据库备份 (如果容器在运行) ---
    if docker ps | grep -q 16lily-db-1; then
        echo "🗄️ [Remote] 正在导出生产数据库..."
        docker exec 16lily-db-1 pg_dump -U postgres opportunity_db > $BACKUP_DIR/db_backup_$TIMESTAMP.sql
        gzip $BACKUP_DIR/db_backup_$TIMESTAMP.sql
        echo "✅ 数据库已备份至: $BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz"
    else
        echo "⚠️ [Remote] 数据库容器未运行，跳过数据库导出 (假设是首次部署或已停止)"
    fi

    # --- C. 备份代码与数据卷 ---
    if [ -d "$REMOTE_DIR" ]; then
        echo "📦 [Remote] 正在归档当前运行环境..."
        tar -czf $BACKUP_DIR/full_env_backup_$TIMESTAMP.tar.gz -C /opt 16lily
        echo "✅ 环境已备份至: $BACKUP_DIR/full_env_backup_$TIMESTAMP.tar.gz"
    fi

    # --- D. 生成一键还原脚本 ---
    cat > $BACKUP_DIR/restore_last_$TIMESTAMP.sh << 'RESTORE_EOF'
#!/bin/bash
echo "⏪ 开始回滚操作..."
cd /opt
# 1. 停止当前服务
if [ -d "/opt/16lily" ]; then
    cd /opt/16lily
    docker compose -f docker-compose.prod.yml down || true
fi

# 2. 恢复文件
echo "📂 恢复旧版文件..."
rm -rf /opt/16lily
tar -xzf $BACKUP_DIR/full_env_backup_$TIMESTAMP.tar.gz -C /opt

# 3. 恢复数据库 (如果需要)
# 注意：通常代码回滚不需要回滚数据库，除非 Schema 变更破坏了兼容性。
# 如果需要强制恢复数据库，请取消注释以下行：
# echo "🗄️ 正在恢复数据库..."
# cd /opt/16lily && docker compose -f docker-compose.prod.yml up -d db
# sleep 10
# gunzip -c $BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz | docker exec -i 16lily-db-1 psql -U postgres opportunity_db

# 4. 重启服务
cd /opt/16lily
docker compose -f docker-compose.prod.yml up -d --build
echo "✅ 回滚完成！"
RESTORE_EOF
    chmod +x $BACKUP_DIR/restore_last_$TIMESTAMP.sh
    echo "🛡️ [Remote] 已生成回滚脚本: $BACKUP_DIR/restore_last_$TIMESTAMP.sh"

    # --- E. 清理旧环境 (保留数据卷) ---
    echo "🧹 [Remote] 清理旧代码 (保留 postgres_data)..."
    # 停止容器
    if [ -d "$REMOTE_DIR" ]; then
        cd $REMOTE_DIR
        docker compose -f docker-compose.prod.yml down --remove-orphans || true
    fi
    
    # 清理代码文件，保留数据
    mkdir -p $REMOTE_DIR
    find $REMOTE_DIR -maxdepth 1 ! -name 'postgres_data' ! -name 'docker-data' ! -name '.env.prod' ! -name '.' -exec rm -rf {} + 2>/dev/null || true

EOF

if [ $? -ne 0 ]; then
    echo "❌ 远程备份或清理失败，终止部署！"
    exit 1
fi

# 3. 上传新包
echo "🚀 [Phase 3] 上传新版本..."
scp project_release.zip $SERVER_USER@$SERVER_IP:$REMOTE_DIR/

# 4. 解压与启动
echo "▶️ [Phase 4] 解压并启动服务..."
ssh $SERVER_USER@$SERVER_IP "bash -s" << EOF
    cd $REMOTE_DIR
    unzip -o -q project_release.zip
    rm project_release.zip

    # 确保 .env.prod 存在
    if [ ! -f .env.prod ]; then
        echo "📝 创建默认 .env.prod..."
        echo "DEBUG=0" > .env.prod
        echo "SECRET_KEY=prod-key-$(date +%s)" >> .env.prod
        echo "ALLOWED_HOSTS=*" >> .env.prod
        echo "SQL_ENGINE=django.db.backends.postgresql" >> .env.prod
        echo "SQL_DATABASE=opportunity_db" >> .env.prod
        echo "SQL_USER=postgres" >> .env.prod
        echo "SQL_PASSWORD=postgres" >> .env.prod
        echo "SQL_HOST=db" >> .env.prod
        echo "SQL_PORT=5432" >> .env.prod
    fi

    # 启动
    echo "🐳 启动 Docker 容器..."
    docker compose -f docker-compose.prod.yml up -d --build

    # 迁移数据库
    echo "🔄 执行数据库迁移..."
    docker exec 16lily-backend-1 python manage.py migrate
    
    # 清理无效通知 (新增功能)
    echo "🧹 清理无效通知数据..."
    docker exec 16lily-backend-1 python manage.py clean_notifications

    echo "✅ 部署完成！访问地址: http://$SERVER_IP"
    echo "🔙 如需回滚，请在服务器执行: $BACKUP_DIR/restore_last_$TIMESTAMP.sh"
EOF
