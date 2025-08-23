# AI客户开发工具 Web化技术方案

## 项目概述

将现有的命令行工具转换为用户友好的Web应用，让非技术用户能够轻松使用AI驱动的B2B客户开发功能。

## Phase 1: 核心MVP技术方案 (4-6周)

### 1. 技术栈选择

#### 后端技术栈
- **Web框架**: FastAPI (高性能、原生异步支持、自动API文档)
- **异步任务队列**: Celery + Redis
- **数据库**: SQLite (MVP阶段) → PostgreSQL (生产环境)
- **ORM**: SQLAlchemy
- **WebSocket**: FastAPI WebSocket + Redis Pub/Sub
- **认证**: JWT Token
- **部署**: Docker + Docker Compose

#### 前端技术栈
- **框架**: React 18 + TypeScript
- **UI组件库**: Ant Design (企业级组件库，适合B2B应用)
- **状态管理**: Zustand (轻量级)
- **HTTP客户端**: Axios
- **WebSocket**: Socket.io-client
- **构建工具**: Vite
- **样式**: Tailwind CSS + Ant Design

### 2. 系统架构设计

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  React Frontend │────▶│  FastAPI Backend│────▶│   Celery Worker │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                        │
         │                       ▼                        ▼
         │              ┌─────────────────┐     ┌─────────────────┐
         │              │                 │     │                 │
         └─────────────▶│      Redis      │     │     SQLite      │
                        │   (Cache/Queue) │     │   (Database)    │
                        │                 │     │                 │
                        └─────────────────┘     └─────────────────┘
```

### 3. 项目结构设计

```
AI_Find_Customer/
├── backend/                    # 后端项目
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI主入口
│   │   ├── api/               # API路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py        # 认证相关API
│   │   │   ├── companies.py   # 企业搜索API
│   │   │   ├── contacts.py    # 联系人提取API
│   │   │   ├── employees.py   # 员工搜索API
│   │   │   └── tasks.py       # 任务状态API
│   │   ├── core/              # 核心业务逻辑（重构自现有脚本）
│   │   │   ├── __init__.py
│   │   │   ├── company_search.py
│   │   │   ├── contact_extractor.py
│   │   │   ├── employee_search.py
│   │   │   └── llm_manager.py
│   │   ├── models/            # 数据库模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── search_job.py
│   │   │   └── result.py
│   │   ├── schemas/           # Pydantic模型
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── company.py
│   │   │   └── task.py
│   │   ├── services/          # 业务服务层
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   └── search_service.py
│   │   ├── tasks/             # Celery任务
│   │   │   ├── __init__.py
│   │   │   ├── company_tasks.py
│   │   │   ├── contact_tasks.py
│   │   │   └── employee_tasks.py
│   │   ├── utils/             # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── websocket.py
│   │   └── config.py          # 配置管理
│   ├── alembic/               # 数据库迁移
│   ├── tests/                 # 测试
│   ├── requirements.txt
│   ├── celery_app.py          # Celery应用
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                   # 前端项目
│   ├── src/
│   │   ├── components/        # React组件
│   │   │   ├── common/
│   │   │   ├── search/
│   │   │   ├── results/
│   │   │   └── auth/
│   │   ├── pages/            # 页面组件
│   │   │   ├── Dashboard.tsx
│   │   │   ├── CompanySearch.tsx
│   │   │   ├── ContactExtract.tsx
│   │   │   └── Results.tsx
│   │   ├── services/         # API服务
│   │   │   ├── api.ts
│   │   │   ├── auth.ts
│   │   │   └── websocket.ts
│   │   ├── store/            # 状态管理
│   │   │   ├── auth.ts
│   │   │   └── search.ts
│   │   ├── types/            # TypeScript类型
│   │   ├── utils/            # 工具函数
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .env.example
│
├── docs/                      # 文档
│   ├── technical_solution.md  # 技术方案
│   ├── api_design.md         # API设计文档
│   └── deployment.md         # 部署文档
│
└── scripts/                   # 部署和维护脚本
    ├── setup.sh
    └── deploy.sh
```

### 4. 核心功能模块设计

#### 4.1 用户认证模块
- 注册/登录功能
- JWT Token认证
- 用户配额管理
- API密钥管理（平台统一管理用户的Serper/LLM密钥）

#### 4.2 企业搜索模块
- 表单化搜索界面
  - 行业选择器（预定义行业列表）
  - 地区选择器（国家/地区级联选择）
  - 高级选项（自定义查询、结果数量）
- 异步任务处理
  - 提交搜索请求后立即返回任务ID
  - 后台Celery处理实际搜索
  - WebSocket推送进度更新

#### 4.3 联系信息提取模块
- 批量网站处理
- 进度实时更新
- 结果质量评分
- 失败重试机制

#### 4.4 结果展示模块
- 数据表格展示（支持排序、筛选）
- 导出功能（CSV、Excel）
- 历史记录查看
- 数据统计概览

### 5. 数据库设计

```sql
-- 用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户配额表
CREATE TABLE user_quotas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    search_limit INTEGER DEFAULT 10,
    search_used INTEGER DEFAULT 0,
    reset_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- API密钥表（加密存储）
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    key_type VARCHAR(50) NOT NULL, -- 'serper', 'openai', 'anthropic', etc.
    encrypted_key TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 搜索任务表
CREATE TABLE search_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    job_type VARCHAR(50) NOT NULL, -- 'company', 'contact', 'employee'
    status VARCHAR(50) NOT NULL, -- 'pending', 'processing', 'completed', 'failed'
    parameters JSON NOT NULL,
    progress INTEGER DEFAULT 0,
    total_items INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 搜索结果表
CREATE TABLE search_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    result_type VARCHAR(50) NOT NULL,
    data JSON NOT NULL,
    quality_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES search_jobs(id)
);
```

### 6. API设计

#### 认证相关
```
POST /api/auth/register      # 用户注册
POST /api/auth/login         # 用户登录
POST /api/auth/refresh       # 刷新Token
GET  /api/auth/profile       # 获取用户信息
```

#### 企业搜索
```
POST /api/companies/search   # 创建企业搜索任务
GET  /api/companies/jobs/{job_id}  # 获取任务状态
GET  /api/companies/results/{job_id}  # 获取搜索结果
```

#### 联系信息提取
```
POST /api/contacts/extract   # 创建联系信息提取任务
GET  /api/contacts/jobs/{job_id}   # 获取任务状态
GET  /api/contacts/results/{job_id}  # 获取提取结果
```

#### WebSocket端点
```
WS /ws/jobs/{job_id}         # 订阅任务进度更新
```

### 7. 实施步骤

#### 第1周：基础架构搭建
1. 创建项目结构
2. 配置Docker环境
3. 设置FastAPI + Celery + Redis
4. 创建数据库模型和迁移

#### 第2周：核心业务逻辑重构
1. 将现有Python脚本重构为独立模块
2. 移除CLI依赖，改为函数接口
3. 实现异步任务封装
4. 添加错误处理和日志

#### 第3周：API开发
1. 实现用户认证API
2. 实现企业搜索API
3. 实现联系信息提取API
4. 实现WebSocket进度推送

#### 第4周：前端开发
1. 搭建React项目框架
2. 实现登录/注册界面
3. 实现企业搜索表单
4. 实现结果展示表格

#### 第5周：集成测试
1. 前后端联调
2. WebSocket通信测试
3. 异步任务流程测试
4. 性能优化

#### 第6周：部署准备
1. 编写部署文档
2. 配置生产环境
3. 安全加固
4. 用户测试

### 8. 技术难点及解决方案

#### 8.1 长时间任务处理
**问题**: Playwright爬取可能需要几分钟
**解决**: 
- Celery异步处理
- WebSocket实时进度推送
- 任务可中断/恢复机制

#### 8.2 并发资源管理
**问题**: 多用户同时使用会导致资源竞争
**解决**: 
- Celery Worker并发限制
- Redis任务队列管理
- 浏览器实例池化

#### 8.3 API成本控制
**问题**: 用户可能滥用API导致成本失控
**解决**: 
- 用户配额系统
- 结果缓存机制
- API调用频率限制

### 9. 安全考虑

1. **API密钥加密**: 使用AES加密存储用户的API密钥
2. **认证安全**: JWT Token + Refresh Token机制
3. **输入验证**: 严格的参数验证防止注入攻击
4. **访问控制**: 基于角色的访问控制(RBAC)
5. **日志审计**: 记录所有API调用和数据访问

### 10. 性能优化

1. **缓存策略**: 
   - Redis缓存搜索结果
   - 相同查询24小时内复用
   
2. **数据库优化**:
   - 适当的索引设计
   - 查询优化
   
3. **异步处理**:
   - 所有IO密集操作异步化
   - 批量处理优化

### 11. 监控和运维

1. **日志系统**: 结构化日志 + ELK Stack
2. **性能监控**: Prometheus + Grafana
3. **错误追踪**: Sentry
4. **健康检查**: 自动化健康检查端点

## 下一步行动

1. 确认技术方案
2. 搭建开发环境
3. 开始第1周的基础架构实现