#!/bin/bash
# 数据库自动备份脚本

BACKUP_DIR="/app/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="db_backup_$TIMESTAMP.sql"

# 创建备份目录（如果不存在）
mkdir -p $BACKUP_DIR

echo "开始备份数据库..."

# 运行 pg_dump
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U postgres opportunity_db > "$BACKUP_DIR/$BACKUP_NAME"

# 压缩备份文件
gzip "$BACKUP_DIR/$BACKUP_NAME"

# 删除 7 天前的备份
find $BACKUP_DIR -type f -name "*.sql.gz" -mtime +7 -delete

echo "备份完成: $BACKUP_DIR/$BACKUP_NAME.gz"
