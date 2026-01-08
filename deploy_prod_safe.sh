#!/bin/bash

# =================================================================
# 🛡️ 安全部署脚本 (v1.3 - 增强版)
# =================================================================
# 功能：
# 1. 全量备份：数据库(SQL)、媒体文件(Media)、代码配置
# 2. 自动生成一键回滚脚本
# 3. 安全部署：本地零修改，云端保留数据
# =================================================================

SERVER_IP="47.94.22.64"
SERVER_USER="root"
REMOTE_DIR="/opt/16lily"
BACKUP_DIR="/opt/16lily_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🔒 [Phase 1] 正在准备本地构建包..."
echo "ℹ️  此操作不会修改您本地的任何源代码或数据。"

# 1. 本地打包 (排除敏感数据与开发环境文件)
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

echo "📤 [Phase 2] 连接服务器 $SERVER_IP 进行深度备份..."
echo "🔑 请输入服务器密码以开始备份与部署:"

# 2. 远程执行核心逻辑
ssh $SERVER_USER@$SERVER_IP "bash -s" << EOF
    set -e # 遇到错误立即停止

    # --- A. 准备备份目录 ---
    mkdir -p $BACKUP_DIR
    echo "💾 [Remote] 创建备份目录: $BACKUP_DIR"

    # --- B. 备份数据 (DB & Media) ---
    if docker ps | grep -q 16lily-web-1; then
        echo "📸 [Remote] 正在备份媒体文件 (Media)..."
        # 从 web 容器中复制 media 目录
        docker cp 16lily-web-1:/app/media $BACKUP_DIR/media_temp_$TIMESTAMP
        tar -czf $BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz -C $BACKUP_DIR media_temp_$TIMESTAMP
        rm -rf $BACKUP_DIR/media_temp_$TIMESTAMP
        echo "✅ 媒体文件已备份"
    fi

    if docker ps | grep -q 16lily-db-1; then
        echo "🗄️ [Remote] 正在导出生产数据库..."
        docker exec 16lily-db-1 pg_dump -U postgres opportunity_db > $BACKUP_DIR/db_backup_$TIMESTAMP.sql
        gzip $BACKUP_DIR/db_backup_$TIMESTAMP.sql
        echo "✅ 数据库已备份至: $BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz"
    else
        echo "⚠️ [Remote] 数据库容器未运行，跳过数据库导出"
    fi

    # --- C. 备份环境配置 ---
    if [ -d "$REMOTE_DIR" ]; then
        echo "📦 [Remote] 正在归档当前运行代码与配置..."
        tar -czf $BACKUP_DIR/code_env_backup_$TIMESTAMP.tar.gz -C /opt 16lily
        echo "✅ 环境已备份"
    fi

    # --- D. 生成一键还原脚本 ---
    cat > $BACKUP_DIR/restore_last_$TIMESTAMP.sh << 'RESTORE_EOF'
#!/bin/bash
echo "⏪ 开始一键回滚..."
cd /opt

# 1. 停止当前服务
if [ -d "/opt/16lily" ]; then
    cd /opt/16lily
    docker compose -f docker-compose.prod.yml down || true
fi

# 2. 恢复代码与配置
echo "📂 恢复代码与配置..."
rm -rf /opt/16lily
tar -xzf $BACKUP_DIR/code_env_backup_$TIMESTAMP.tar.gz -C /opt

# 3. 恢复媒体文件 (启动容器后执行)
echo "🖼️ 准备恢复媒体文件..."

# 4. 重启服务
cd /opt/16lily
docker compose -f docker-compose.prod.yml up -d --build

# 5. 等待容器启动并恢复媒体
echo "⏳ 等待服务启动..."
sleep 15
if [ -f "$BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz" ]; then
    echo "🖼️ 正在还原媒体文件..."
    tar -xzf $BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz -C $BACKUP_DIR
    docker cp $BACKUP_DIR/media_temp_$TIMESTAMP/. 16lily-web-1:/app/media/
    rm -rf $BACKUP_DIR/media_temp_$TIMESTAMP
fi

echo "✅ 回滚完成！系统已恢复到 $TIMESTAMP 状态。"
RESTORE_EOF
    chmod +x $BACKUP_DIR/restore_last_$TIMESTAMP.sh
    echo "🛡️ [Remote] 已生成回滚脚本: $BACKUP_DIR/restore_last_$TIMESTAMP.sh"

    # --- E. 清理旧代码 (保留 .env.prod 以防万一) ---
    echo "🧹 [Remote] 清理旧代码..."
    if [ -d "$REMOTE_DIR" ]; then
        cd $REMOTE_DIR
        # 停止容器但不删除卷
        docker compose -f docker-compose.prod.yml down --remove-orphans || true
    fi
    
    # 仅清理代码文件，保留目录结构
    mkdir -p $REMOTE_DIR
    find $REMOTE_DIR -maxdepth 1 ! -name 'postgres_data' ! -name 'docker-data' ! -name '.env.prod' ! -name '.' -exec rm -rf {} + 2>/dev/null || true

EOF

if [ $? -ne 0 ]; then
    echo "❌ 远程备份失败，终止部署！您的环境未受影响。"
    exit 1
fi

# 3. 上传新包 (使用 /tmp 中转以确保成功)
echo "🚀 [Phase 3] 上传新版本..."
scp project_release.zip $SERVER_USER@$SERVER_IP:/tmp/project_release.zip

if [ $? -ne 0 ]; then
    echo "❌ 上传失败！请尝试手动运行回滚脚本恢复环境。"
    exit 1
fi

# 4. 解压与启动
echo "▶️ [Phase 4] 解压并启动服务..."
ssh $SERVER_USER@$SERVER_IP "bash -s" << EOF
    # 确保目标目录存在
    mkdir -p $REMOTE_DIR
    
    # 移动文件
    mv /tmp/project_release.zip $REMOTE_DIR/project_release.zip
    
    cd $REMOTE_DIR
    unzip -o -q project_release.zip
    rm project_release.zip

    # 检查 .env.prod，如果不存在则创建默认 (通常已有备份)
    if [ ! -f .env.prod ]; then
        echo "📝 创建默认 .env.prod..."
        cat > .env.prod << 'ENV_EOF'
DEBUG=0
SECRET_KEY=prod-key-auto-generated
ALLOWED_HOSTS=*
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=opportunity_db
SQL_USER=postgres
SQL_PASSWORD=postgres
SQL_HOST=db
SQL_PORT=5432
ENV_EOF
    fi

    # 启动
    echo "🐳 启动 Docker 容器..."
    docker compose -f docker-compose.prod.yml up -d --build

    # 执行数据库迁移
    echo "🔄 执行数据库迁移 (migrate)..."
    docker exec 16lily-backend-1 python manage.py migrate
    
    # 清理通知数据
    echo "🧹 清理无效通知..."
    docker exec 16lily-backend-1 python manage.py clean_notifications

    echo "✅ 部署成功！"
    echo "🌍 访问地址: http://$SERVER_IP"
EOF

# 清理本地临时文件
rm -f project_release.zip
echo "✨ 本地清理完成。"
