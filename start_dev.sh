#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 正在启动团队商机系统 (核心引擎 v1.2)...${NC}"

# 0. 自动清理端口占用 (新增功能)
PORT=8000
PID=$(lsof -ti tcp:$PORT)
if [ ! -z "$PID" ]; then
  echo -e "${YELLOW}⚠️  发现端口 $PORT 被旧进程 (PID: $PID) 占用，正在自动清理...${NC}"
  kill -9 $PID
  echo -e "${GREEN}✅ 端口已释放${NC}"
fi

# 1. 检查并启动 Docker
if ! docker info > /dev/null 2>&1; then
  echo "Docker 未运行，正在尝试启动..."
  open -a Docker
  echo "等待 Docker 启动 (可能需要几分钟)..."
  while ! docker info > /dev/null 2>&1; do
    sleep 5
    echo -n "."
  done
  echo ""
fi
echo -e "${GREEN}✅ Docker 已运行${NC}"

# 2. 启动数据库
echo "启动 PostgreSQL 数据库..."
docker-compose up -d
echo "等待数据库初始化..."
sleep 2

# 3. 激活虚拟环境并初始化
echo "检查并应用更新..."
source venv/bin/activate
python manage.py migrate

# 4. 初始化/更新权限角色
echo "初始化角色权限组..."
python manage.py init_roles

# 5. 启动服务器
echo -e "${GREEN}🎉 系统启动成功!${NC}"
echo -e "👉 管理后台地址: http://127.0.0.1:8000/admin/"
echo -e "   账号: admin"
echo -e "   密码: admin123456"
echo "按 Ctrl+C 停止服务器"

python manage.py runserver 0.0.0.0:8000
