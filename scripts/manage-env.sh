#!/bin/bash

# 环境管理助手脚本
# 用法: ./scripts/manage-env.sh [dev|prod] [up|down|restart|logs]

ENV=$1
ACTION=$2

if [[ -z "$ENV" || -z "$ACTION" ]]; then
    echo "用法: $0 [dev|prod] [up|down|restart|logs]"
    exit 1
fi

case $ENV in
    dev)
        COMPOSE_FILE="docker-compose.yml"
        ENV_FILE=".env.dev"
        ;;
    prod)
        COMPOSE_FILE="docker-compose.prod.yml"
        ENV_FILE=".env.prod"
        ;;
    *)
        echo "错误: 未知的环境 '$ENV'. 请使用 'dev' 或 'prod'."
        exit 1
        ;;
esac

# 检查 .env 文件是否存在
if [[ ! -f "$ENV_FILE" ]]; then
    echo "警告: 配置文件 $ENV_FILE 不存在。"
    if [[ -f "$ENV_FILE.example" ]]; then
        echo "正在从模板创建 $ENV_FILE..."
        cp "$ENV_FILE.example" "$ENV_FILE"
        echo "请编辑 $ENV_FILE 以配置您的环境参数。"
    else
        echo "错误: 找不到模板 $ENV_FILE.example"
        exit 1
    fi
fi

echo "正在对 [$ENV] 环境执行 [$ACTION] 操作..."

case $ACTION in
    up)
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d --build
        ;;
    down)
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE down
        ;;
    restart)
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE restart
        ;;
    logs)
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE logs -f --tail=100
        ;;
    *)
        echo "错误: 未知的操作 '$ACTION'. 请使用 'up', 'down', 'restart' 或 'logs'."
        exit 1
        ;;
esac
