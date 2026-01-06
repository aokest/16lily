#!/bin/bash
# 一键更新脚本

echo "开始更新系统..."

# 1. 拉取代码
# git pull origin main

# 2. 内存优化：构建前先停止当前运行的容器，腾出内存
echo "正在腾出内存空间..."
docker-compose -f docker-compose.prod.yml down

# 3. 构建并启动容器
echo "开始构建镜像（这可能需要几分钟，请耐心等待）..."
docker-compose -f docker-compose.prod.yml up -d --build

# 3. 运行数据库迁移
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate --noinput

# 4. 收集静态文件
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

# 5. 清理过期的 Docker 镜像
docker image prune -f

echo "更新完成！"
