# 系统维护与安全指南

## 1. 生产环境部署 (上线)

本系统采用 Docker 容器化部署，确保环境一致性和安全性。

### 1.1 首次部署

1. 确保服务器已安装 Docker 和 Docker Compose。
2. 复制项目代码到服务器。
3. 修改 `.env.prod` 文件，设置强密码和密钥：
   ```bash
   nano .env.prod
   # 修改 SECRET_KEY, POSTGRES_PASSWORD 等
   ```
4. 启动服务：
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```
5. 初始化数据库：
   ```bash
   docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
   docker-compose -f docker-compose.prod.yml exec web python manage.py init_roles
   docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
   ```

---

## 2. 日常维护与修改

### 2.1 代码修改与更新

当你修改了本地代码并推送到仓库后，在服务器上执行以下脚本即可自动更新：

```bash
./scripts/update.sh
```

该脚本会自动：
1. 拉取最新代码 (`git pull`)
2. 重建 Docker 容器 (如果有依赖变更)
3. 运行数据库迁移 (`migrate`)
4. 收集静态文件
5. 重启服务

### 2.2 数据备份

为了防止数据丢失，建议定期运行备份脚本：

```bash
./scripts/backup.sh
```

备份文件会保存在 `backups/` 目录下，文件名包含时间戳，例如 `db_backup_20231027_103000.sql`。

**建议**：可以使用 crontab 设置每天自动备份。
```bash
# 每天凌晨 3 点备份
0 3 * * * /path/to/project/scripts/backup.sh >> /var/log/backup.log 2>&1
```

---

## 3. 安全保障机制

### 3.1 网络安全

1. **反向代理 (Nginx)**:
   - 系统使用 Nginx 作为反向代理，对外只暴露 HTTP (80) / HTTPS (443) 端口。
   - 内部应用服务器 (Gunicorn/Django) 运行在 8000 端口，**不对外暴露**，仅允许 Nginx 访问。

2. **数据库隔离**:
   - PostgreSQL 数据库运行在 Docker 内部网络中，**不映射 5432 端口到主机**。
   - 这意味着外部攻击者无法直接连接数据库，只有容器内的 Django 应用可以访问。

3. **静态文件分离**:
   - Nginx 直接处理静态文件和媒体文件请求，减轻应用服务器压力并提高安全性。

### 3.2 数据安全

1. **自动备份**: 使用 `scripts/backup.sh` 定期备份。
2. **环境变量管理**: 敏感信息（数据库密码、Secret Key）存储在 `.env.prod` 文件中，**不要提交到代码仓库**。
3. **权限控制**: Django Admin 内置了基于角色的权限控制 (RBAC)，确保只有授权人员能操作敏感数据。

---

## 4. 故障排查

查看日志：
```bash
# 查看所有日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看 Web 应用日志
docker-compose -f docker-compose.prod.yml logs -f web

# 查看 Nginx 日志
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### 4.1 AI 解析诊断（开发环境）

```bash
docker-compose logs -n 200 web | grep "LLM API Error"
docker-compose logs -n 200 web | grep "JSON Decode Error"
docker-compose exec web python manage.py check
```

## 5. AI 解析问题定位方法

- 确认 `provider/base_url/model_name/api_key` 正确；DeepSeek 推荐 `https://api.deepseek.com/v1` + `deepseek-chat`
- 若“分析失败”，在“系统工具”点击“测试模型连接”，记录返回；同时查看后端日志：
  - `LLM API Error`: 说明接口返回非 2xx 或鉴权问题
  - `JSON Decode Error`: 说明模型未返回纯 JSON，需收紧提示词或启用函数调用
- 临时解决：系统会自动进行兜底填表，保证流程不中断；管理员后续修复解析并更新提示词模板
