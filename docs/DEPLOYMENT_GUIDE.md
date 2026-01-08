# 生产环境部署指南 (1Panel 特供版)

本指南专门针对 **阿里云轻量服务器 + 1Panel 面板 (2核 2G)** 环境进行了优化。

## 1. 准备工作

### 1.1 1Panel 环境检查
1.  登录 1Panel 面板。
2.  进入 **[容器]** 菜单，确保 Docker 和 Docker Compose 已安装并正常运行。
3.  进入 **[主机] -> [SSH]**，确保你可以正常连接到服务器终端。

### 1.2 内存优化 (针对 2G 内存)
2G 内存直接构建前端可能会出现 OOM（内存溢出）。我们首先增加虚拟内存（Swap）：
1.  在 1Panel 的 **[终端]** 中执行：
    ```bash
    # 创建 2G 的交换文件
    dd if=/dev/zero of=/swapfile bs=1M count=2048
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    # 永久生效
    echo "/swapfile swap swap defaults 0 0" >> /etc/fstab
    ```

---

## 2. 部署步骤

### 2.1 克隆代码
进入 1Panel 的 **[主机] -> [终端]**，执行：
```bash
mkdir -p /opt/1panel/apps/16lily
cd /opt/1panel/apps/16lily
git clone https://github.com/aokest/16group.git .
```

### 2.2 配置环境变量
在当前目录下创建 `.env.prod` 文件：
```bash
cat > .env.prod <<EOF
DEBUG=0
SECRET_KEY=$(openssl rand -base64 32)
ALLOWED_HOSTS=你的服务器公网IP,localhost,127.0.0.1
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=opportunity_db
SQL_USER=postgres
SQL_PASSWORD=设置一个复杂的密码
SQL_HOST=db
SQL_PORT=5432
BACKEND_URL=http://web:8000
EOF
```

### 2.3 一键启动
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### 2.4 初始化数据库
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

---

## 3. 访问与维护

1.  **访问**：在浏览器输入 `http://你的服务器IP`。
2.  **安全组**：确保阿里云后台开放了 80 端口。
3.  **1Panel 管理**：你可以在 1Panel 的 **[容器]** 页面看到正在运行的 `web`、`db`、`nginx` 等服务，并直接查看日志。

## 4. 常见问题
- **构建慢**：2G 内存即使有 Swap 也会比较慢，请耐心等待 5-10 分钟。
- **端口冲突**：如果 80 端口被 1Panel 本身或其他应用占用，请修改 `docker-compose.prod.yml` 中的 nginx 端口映射。

## 4. 常见问题 (FAQ)

- **前端页面显示 404**：检查 Nginx 配置中的 `root` 路径是否正确，并确保 `frontend_dist` 卷已成功挂载。
- **无法登录**：确保后端 `web` 容器已启动，并检查 `.env.prod` 中的 `ALLOWED_HOSTS` 是否包含了当前访问的域名或 IP。
- **数据库连接失败**：确保 `db` 容器处于 `running` 状态，且环境变量中的数据库主机名设置为 `db`（即 Docker Compose 中的服务名）。

---
**提示**：为了数据安全，请务必修改默认的数据库密码，并在云控制台关闭不必要的端口。
