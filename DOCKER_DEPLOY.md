# Docker 部署指南

## 系统要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 2GB 可用内存
- 至少 5GB 可用磁盘空间

## 快速部署

### 1. 准备环境变量

首次部署前，需要配置 API 密钥：

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加你的 API 密钥
nano .env
```

**必需的 API 密钥：**
- `SERPER_API_KEY` - Serper.dev API 密钥（用于搜索功能）

### 2. 使用部署脚本（推荐）

我们提供了一个交互式部署脚本，简化部署流程：

```bash
# 给脚本添加执行权限
chmod +x docker_deploy.sh

# 运行部署脚本
./docker_deploy.sh
```

选择选项 1 进行完整部署（构建并启动）。

### 3. 手动部署

如果你更喜欢手动控制，可以使用以下命令：

```bash
# 构建 Docker 镜像
docker build -t ai-customer-finder .

# 使用 docker-compose 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 访问应用

部署成功后，在浏览器中访问：

```
http://localhost:8501
```

## 目录结构

```
AI_Find_Customer/
├── output/              # 输出文件目录（自动创建）
│   ├── company/        # 公司搜索结果
│   ├── contact/        # 联系信息提取结果
│   └── employee/       # 员工搜索结果
├── .env                # 环境变量配置（需要创建）
├── docker-compose.yml  # Docker Compose 配置
└── Dockerfile         # Docker 镜像配置
```

## 常用命令

### 查看服务状态
```bash
docker-compose ps
```

### 查看实时日志
```bash
docker-compose logs -f
```

### 重启服务
```bash
docker-compose restart
```

### 停止并删除容器
```bash
docker-compose down
```

### 重新构建镜像（代码更新后）
```bash
docker-compose build
docker-compose up -d
```

## 数据持久化

所有搜索结果保存在 `output/` 目录中，该目录通过 Docker volume 挂载，数据不会因容器重启而丢失。

## 故障排查

### 1. 端口占用

如果 8501 端口被占用，修改 `docker-compose.yml`：

```yaml
ports:
  - "8502:8501"  # 改为其他端口
```

### 2. 内存不足

如果遇到内存问题，可以限制容器内存使用：

```yaml
services:
  ai-customer-finder:
    mem_limit: 2g
    mem_reservation: 1g
```

### 3. API 密钥错误

检查 `.env` 文件中的 API 密钥是否正确：

```bash
# 查看当前配置（不显示密钥值）
grep SERPER_API_KEY .env

# 验证密钥是否被正确加载
docker-compose exec ai-customer-finder env | grep SERPER
```

### 4. Playwright 浏览器问题

如果遇到浏览器相关错误，可以重新安装：

```bash
docker-compose exec ai-customer-finder playwright install chromium
```

## 性能优化

### 1. 调整并发数

编辑 `.env` 文件：

```bash
# 设置页面加载超时（毫秒）
TIMEOUT=30000

# 启用无头模式（提高性能）
HEADLESS=true
```

### 2. 资源限制

在 `docker-compose.yml` 中设置资源限制：

```yaml
services:
  ai-customer-finder:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## 安全建议

1. **不要提交 .env 文件到版本控制**
   - `.env` 文件已在 `.gitignore` 中排除

2. **定期更新 Docker 镜像**
   ```bash
   docker-compose pull
   docker-compose build --no-cache
   ```

3. **使用环境变量管理敏感信息**
   - 所有 API 密钥都通过环境变量传递
   - 生产环境建议使用 Docker Secrets

## 更新部署

当代码更新后，执行以下步骤：

```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose build

# 重启服务
docker-compose up -d
```

## 监控和日志

### 查看容器资源使用
```bash
docker stats ai-customer-finder
```

### 导出日志
```bash
docker-compose logs > app_logs.txt
```

### 健康检查
```bash
curl http://localhost:8501/_stcore/health
```

## 常见问题

**Q: 搜索结果数量限制为 20 个？**
A: 这是 Serper API 的限制，对于某些查询，结果数量超过 20 会返回错误。

**Q: 如何在后台运行？**
A: 使用 `-d` 参数：`docker-compose up -d`

**Q: 如何完全清理 Docker 环境？**
A: 
```bash
docker-compose down -v
docker rmi ai-customer-finder
```

## 支持

如遇到问题，请查看：
- 应用日志：`docker-compose logs`
- GitHub Issues：[项目问题追踪](https://github.com/your-repo/AI_Find_Customer/issues)