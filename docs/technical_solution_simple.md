# AI客户开发工具 Web化技术方案（简化版）

## 项目概述

使用Streamlit快速构建Web界面，让非技术用户能够轻松使用AI驱动的B2B客户开发功能。

## 简化版技术方案 (2-3周快速实现)

### 1. 技术栈选择（极简化）

- **Web框架**: Streamlit（Python原生，快速开发）
- **数据库**: SQLite（轻量级，易于部署）
- **后台任务**: Python threading（避免复杂的Celery配置）
- **部署**: Streamlit Cloud 或 单机Docker

### 2. 项目结构（简化版）

```
AI_Find_Customer/
├── web_app/                    # Web应用
│   ├── app.py                 # Streamlit主应用
│   ├── pages/                 # 多页面应用
│   │   ├── 1_🔍_企业搜索.py
│   │   ├── 2_📧_联系信息提取.py
│   │   ├── 3_👥_员工搜索.py
│   │   └── 4_📊_历史记录.py
│   ├── components/            # UI组件
│   │   ├── __init__.py
│   │   ├── auth.py           # 认证组件
│   │   ├── search_form.py    # 搜索表单
│   │   └── results_table.py  # 结果表格
│   ├── core/                  # 核心业务逻辑（重构自现有脚本）
│   │   ├── __init__.py
│   │   ├── company_search.py
│   │   ├── contact_extractor.py
│   │   ├── employee_search.py
│   │   └── llm_manager.py
│   ├── database/              # 数据库相关
│   │   ├── __init__.py
│   │   ├── models.py         # SQLAlchemy模型
│   │   └── crud.py          # 数据库操作
│   ├── utils/                 # 工具函数
│   │   ├── __init__.py
│   │   ├── auth.py           # 认证工具
│   │   └── config.py         # 配置管理
│   ├── requirements.txt
│   └── .env.example
├── docs/                      # 文档
│   └── user_guide.md         # 用户指南
└── data/                      # 数据存储
    ├── database.db           # SQLite数据库
    └── exports/              # 导出文件
```

### 3. 核心功能实现

#### 3.1 用户认证（简化版）
```python
# 使用Streamlit内置的secrets管理和session state
import streamlit as st
import hashlib

def simple_auth():
    """简单的用户认证"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        with st.form("login_form"):
            username = st.text_input("用户名")
            password = st.text_input("密码", type="password")
            submitted = st.form_submit_button("登录")
            
            if submitted:
                # 简单的密码验证
                if check_credentials(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
        return False
    return True
```

#### 3.2 企业搜索页面
```python
# pages/1_🔍_企业搜索.py
import streamlit as st
from core.company_search import search_companies
import pandas as pd

st.set_page_config(page_title="企业搜索", page_icon="🔍")

# 侧边栏搜索表单
with st.sidebar:
    st.header("搜索条件")
    
    search_mode = st.radio(
        "搜索模式",
        ["通用搜索", "LinkedIn搜索", "自定义查询"]
    )
    
    if search_mode != "自定义查询":
        industry = st.text_input("行业关键词", placeholder="如：solar energy")
        region = st.text_input("地区", placeholder="如：California")
        keywords = st.text_input("附加关键词", placeholder="用逗号分隔")
    else:
        custom_query = st.text_area("自定义搜索查询", 
                                   placeholder="输入完整的搜索查询...")
    
    gl = st.selectbox("目标市场", ["us", "uk", "cn", "de", "fr"])
    num_results = st.slider("结果数量", 10, 100, 30)
    
    search_button = st.button("🚀 开始搜索", type="primary")

# 主界面
st.title("🔍 企业智能搜索")
st.markdown("通过行业、地区等条件快速找到目标企业")

# 搜索逻辑
if search_button:
    with st.spinner("正在搜索企业信息..."):
        # 调用核心搜索逻辑
        results = search_companies(
            mode=search_mode,
            industry=industry if search_mode != "自定义查询" else None,
            region=region if search_mode != "自定义查询" else None,
            custom_query=custom_query if search_mode == "自定义查询" else None,
            gl=gl,
            num_results=num_results
        )
        
        if results:
            st.success(f"找到 {len(results)} 家企业！")
            
            # 显示结果表格
            df = pd.DataFrame(results)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "url": st.column_config.LinkColumn("网站"),
                    "linkedin": st.column_config.LinkColumn("LinkedIn")
                }
            )
            
            # 下载按钮
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 下载CSV",
                data=csv,
                file_name=f"companies_{search_mode}_{gl}.csv",
                mime="text/csv"
            )
            
            # 保存到数据库
            save_to_database(results, st.session_state.username)
```

#### 3.3 进度显示（使用Streamlit原生组件）
```python
def process_with_progress(items, process_func, description="处理中"):
    """带进度条的批量处理"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    results = []
    
    for i, item in enumerate(items):
        # 更新进度
        progress = (i + 1) / len(items)
        progress_bar.progress(progress)
        status_text.text(f"{description}: {i+1}/{len(items)} - {item}")
        
        # 处理单个项目
        try:
            result = process_func(item)
            results.append(result)
        except Exception as e:
            st.warning(f"处理 {item} 时出错: {str(e)}")
            results.append(None)
    
    progress_bar.empty()
    status_text.empty()
    return results
```

### 4. 数据库设计（简化版）

```python
# database/models.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password_hash = Column(String(256))
    created_at = Column(DateTime, default=datetime.utcnow)
    search_quota = Column(Integer, default=100)  # 每月搜索配额

class SearchHistory(Base):
    __tablename__ = 'search_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    search_type = Column(String(50))  # company/contact/employee
    parameters = Column(JSON)
    results_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class SearchResult(Base):
    __tablename__ = 'search_results'
    
    id = Column(Integer, primary_key=True)
    history_id = Column(Integer)
    result_type = Column(String(50))
    data = Column(JSON)
    quality_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 5. 配置管理（简化版）

```python
# utils/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ARK_API_KEY = os.getenv("ARK_API_KEY")
    
    # Database
    DATABASE_URL = "sqlite:///data/database.db"
    
    # App Settings
    MAX_RESULTS_PER_SEARCH = 100
    HEADLESS_BROWSER = True
    REQUEST_TIMEOUT = 15000
    
    # User Quotas (MVP阶段简单配额)
    MONTHLY_SEARCH_QUOTA = 100
    DAILY_EXTRACT_QUOTA = 50
```

### 6. 主应用入口

```python
# app.py
import streamlit as st
from utils.auth import simple_auth
from database.models import init_db

# 页面配置
st.set_page_config(
    page_title="AI客户开发助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化数据库
init_db()

# 认证检查
if not simple_auth():
    st.stop()

# 主页面
st.title("🤖 AI客户开发助手")
st.markdown("""
### 欢迎使用AI驱动的B2B客户开发工具！

本工具可以帮助您：
- 🔍 **智能搜索企业** - 根据行业、地区快速找到目标客户
- 📧 **提取联系方式** - 自动从企业网站提取邮箱、电话等信息
- 👥 **查找关键人员** - 定位企业决策者和关键联系人

#### 快速开始
1. 从左侧导航选择功能
2. 填写搜索条件
3. 点击搜索按钮
4. 查看和下载结果

#### 使用配额
- 本月剩余搜索次数：{}/{}
- 今日剩余提取次数：{}/{}
""".format(
    st.session_state.get('remaining_searches', 100),
    100,
    st.session_state.get('remaining_extracts', 50),
    50
))

# 显示最近的搜索记录
st.subheader("📊 最近搜索")
recent_searches = get_recent_searches(st.session_state.username)
if recent_searches:
    st.dataframe(recent_searches, use_container_width=True)
else:
    st.info("暂无搜索记录")
```

### 7. 部署方案（极简版）

#### 方案1：Streamlit Cloud（推荐）
1. 将代码推送到GitHub
2. 在Streamlit Cloud连接仓库
3. 配置环境变量
4. 一键部署

#### 方案2：单机Docker部署
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list \
    && apt-get update && apt-get install -y \
    google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p data

# 运行应用
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 8. 实施计划（2-3周）

#### 第1周：核心功能移植
- Day 1-2: 项目搭建，数据库设计
- Day 3-4: 重构核心业务逻辑为可复用模块
- Day 5: 实现简单用户认证和配额管理

#### 第2周：界面开发
- Day 1-2: 企业搜索页面
- Day 3-4: 联系信息提取页面
- Day 5: 员工搜索页面和历史记录

#### 第3周：优化和部署
- Day 1-2: UI优化和错误处理
- Day 3: 性能优化和测试
- Day 4-5: 部署上线

### 9. 优势和限制

#### 优势
- ✅ 开发速度快（2-3周完成）
- ✅ 部署简单（Streamlit Cloud一键部署）
- ✅ 维护成本低
- ✅ 用户界面友好
- ✅ 适合MVP验证

#### 限制
- ⚠️ 并发能力有限（适合小团队使用）
- ⚠️ 缺少复杂的任务队列（长任务会阻塞）
- ⚠️ 扩展性受限（单机应用）

### 10. 后续升级路径

如果MVP验证成功，可以逐步升级：
1. 添加Redis缓存提升性能
2. 使用FastAPI + React重构以支持更多用户
3. 引入Celery处理长时间任务
4. 迁移到PostgreSQL提升数据库性能