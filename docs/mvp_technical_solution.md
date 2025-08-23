# AI客户开发工具 MVP技术方案（开源版）

## 项目目标

将命令行工具转换为Web界面，保留所有核心功能，让普通用户无需技术背景即可使用。

## MVP核心原则

- ✅ 保留所有核心功能（企业搜索、联系信息提取、员工搜索）
- ✅ 简单直观的Web界面
- ✅ 无需用户管理（开源自部署）
- ✅ 最小化技术复杂度
- ✅ 1-2周可完成开发

## 技术方案

### 1. 技术栈（极简）

- **Web框架**: Streamlit
- **数据存储**: 文件系统（CSV/JSON）
- **依赖**: 继承现有requirements.txt + streamlit

### 2. 项目结构

```
AI_Find_Customer/
├── streamlit_app.py           # Streamlit主应用入口
├── pages/                     # Streamlit多页面
│   ├── 1_🔍_Company_Search.py
│   ├── 2_📧_Contact_Extraction.py
│   └── 3_👥_Employee_Search.py
├── components/                # UI组件
│   ├── __init__.py
│   └── common.py             # 通用UI组件
├── core/                      # 核心业务逻辑（从现有代码重构）
│   ├── __init__.py
│   ├── company_search.py     # 基于serper_company_search.py
│   ├── contact_extractor.py  # 基于extract_contact_info.py
│   └── employee_search.py    # 基于serper_employee_search.py
├── output/                    # 保持现有输出结构
│   ├── company/
│   ├── contact/
│   └── employee/
├── .env                       # API密钥配置
├── requirements.txt           # 添加streamlit依赖
└── README.md                  # 更新使用说明
```

### 3. 核心代码重构

#### 3.1 将命令行脚本重构为函数库

```python
# core/company_search.py
# 基于现有的serper_company_search.py重构

import json
import os
import time
import csv
import re
import requests
from typing import List, Dict, Optional

class CompanySearcher:
    def __init__(self):
        self.api_key = os.getenv("SERPER_API_KEY")
        if not self.api_key:
            raise ValueError("SERPER_API_KEY not found")
        
        self.base_url = "https://google.serper.dev/search"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
    
    def search_companies(
        self,
        search_mode: str = "general",
        industry: Optional[str] = None,
        region: Optional[str] = None,
        custom_query: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        gl: str = "us",
        num_results: int = 30
    ) -> Dict:
        """
        统一的企业搜索接口
        返回: {"success": bool, "data": list, "error": str}
        """
        try:
            if search_mode == "linkedin":
                results = self._search_linkedin_companies(
                    industry, region, keywords, gl, num_results
                )
            else:
                results = self._search_general_companies(
                    industry, region, keywords, custom_query, gl, num_results
                )
            
            # 保存结果到文件（保持原有行为）
            self._save_results(results, search_mode, industry, region, gl)
            
            return {
                "success": True,
                "data": results,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "error": str(e)
            }
    
    # ... 其他方法从原脚本迁移
```

#### 3.2 Streamlit主应用

```python
# streamlit_app.py
import streamlit as st
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="AI Customer Finder",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/AI_Find_Customer',
        'Report a bug': "https://github.com/your-repo/AI_Find_Customer/issues",
        'About': "# AI Customer Finder\n开源的B2B客户开发工具"
    }
)

# 检查API密钥配置
def check_api_keys():
    """检查必要的API密钥是否配置"""
    required_keys = ["SERPER_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        st.error(f"⚠️ 缺少必要的API密钥: {', '.join(missing_keys)}")
        st.info("请在 .env 文件中配置相应的API密钥")
        st.stop()

# 主页面
st.title("🤖 AI Customer Finder")
st.markdown("""
### 开源的B2B客户智能开发工具

本工具可以帮助您：
- 🔍 **智能搜索企业** - 根据行业、地区快速找到目标客户
- 📧 **提取联系方式** - 自动从企业网站提取邮箱、电话等信息  
- 👥 **查找关键人员** - 定位企业决策者和关键联系人

---

### 快速开始
1. 确保已配置 `.env` 文件中的API密钥
2. 从左侧导航选择所需功能
3. 填写搜索条件并执行
4. 查看结果并下载数据

### 输出文件位置
所有结果将保存在 `output/` 目录下：
- 企业搜索结果: `output/company/`
- 联系信息: `output/contact/`
- 员工信息: `output/employee/`
""")

# API密钥状态检查
check_api_keys()

# 显示当前配置状态
with st.sidebar:
    st.header("⚙️ 配置状态")
    
    # API密钥状态
    serper_status = "✅" if os.getenv("SERPER_API_KEY") else "❌"
    st.write(f"Serper API: {serper_status}")
    
    # LLM配置状态
    llm_provider = os.getenv("LLM_PROVIDER", "none")
    llm_status = "✅" if llm_provider != "none" else "⚠️"
    st.write(f"LLM Provider: {llm_status} {llm_provider}")
    
    st.divider()
    
    # 快速链接
    st.header("🔗 快速链接")
    st.markdown("""
    - [查看输出文件](file://output/)
    - [GitHub仓库](https://github.com/your-repo)
    - [使用文档](https://github.com/your-repo/wiki)
    """)
```

#### 3.3 企业搜索页面

```python
# pages/1_🔍_Company_Search.py
import streamlit as st
import pandas as pd
from core.company_search import CompanySearcher
import os
import json

st.set_page_config(page_title="Company Search", page_icon="🔍", layout="wide")

st.title("🔍 企业智能搜索")
st.markdown("根据行业、地区等条件搜索目标企业")

# 初始化搜索器
@st.cache_resource
def get_searcher():
    return CompanySearcher()

searcher = get_searcher()

# 搜索表单
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("搜索条件")
    
    # 搜索模式选择
    search_mode = st.radio(
        "搜索模式",
        ["通用搜索", "LinkedIn企业搜索", "自定义查询"],
        help="选择不同的搜索模式"
    )
    
    # 根据模式显示不同的输入框
    if search_mode == "自定义查询":
        custom_query = st.text_area(
            "自定义搜索查询",
            placeholder="输入完整的搜索查询，例如：renewable energy companies California",
            height=100
        )
    else:
        industry = st.text_input(
            "行业关键词",
            placeholder="例如: solar energy, software, manufacturing"
        )
        
        region = st.text_input(
            "地区/位置",
            placeholder="例如: California, New York, London"
        )
        
        keywords = st.text_input(
            "附加关键词（可选）",
            placeholder="用逗号分隔多个关键词",
            help="添加额外的搜索关键词来精确结果"
        )
    
    # 高级选项
    with st.expander("高级选项"):
        gl = st.selectbox(
            "目标市场",
            options=["us", "uk", "cn", "de", "fr", "jp", "au", "ca"],
            index=0,
            help="选择搜索的地理位置偏好"
        )
        
        num_results = st.slider(
            "结果数量",
            min_value=10,
            max_value=100,
            value=30,
            step=10,
            help="返回的搜索结果数量"
        )
    
    # 搜索按钮
    search_button = st.button("🚀 开始搜索", type="primary", use_container_width=True)

# 结果显示区域
with col2:
    st.subheader("搜索结果")
    
    if search_button:
        # 参数验证
        if search_mode == "自定义查询" and not custom_query:
            st.error("请输入自定义查询内容")
        elif search_mode != "自定义查询" and not industry and not region:
            st.error("请至少输入行业或地区")
        else:
            # 执行搜索
            with st.spinner("正在搜索企业信息..."):
                # 准备参数
                search_params = {
                    "search_mode": "linkedin" if search_mode == "LinkedIn企业搜索" else "general",
                    "gl": gl,
                    "num_results": num_results
                }
                
                if search_mode == "自定义查询":
                    search_params["custom_query"] = custom_query
                else:
                    search_params["industry"] = industry
                    search_params["region"] = region
                    if keywords:
                        search_params["keywords"] = [k.strip() for k in keywords.split(",")]
                
                # 执行搜索
                result = searcher.search_companies(**search_params)
                
                if result["success"]:
                    companies = result["data"]
                    st.success(f"✅ 找到 {len(companies)} 家企业！")
                    
                    # 转换为DataFrame显示
                    if companies:
                        df = pd.DataFrame(companies)
                        
                        # 显示统计信息
                        col_stat1, col_stat2, col_stat3 = st.columns(3)
                        with col_stat1:
                            st.metric("找到企业数", len(companies))
                        with col_stat2:
                            domains = df['domain'].dropna().nunique()
                            st.metric("独立域名数", domains)
                        with col_stat3:
                            linkedin_count = df['linkedin'].notna().sum()
                            st.metric("LinkedIn链接", linkedin_count)
                        
                        # 显示数据表格
                        st.dataframe(
                            df,
                            use_container_width=True,
                            height=400,
                            column_config={
                                "url": st.column_config.LinkColumn("网站链接"),
                                "linkedin": st.column_config.LinkColumn("LinkedIn"),
                                "name": st.column_config.TextColumn("公司名称", width="medium"),
                                "description": st.column_config.TextColumn("描述", width="large"),
                            },
                            hide_index=True
                        )
                        
                        # 下载选项
                        st.divider()
                        col_dl1, col_dl2 = st.columns(2)
                        
                        with col_dl1:
                            csv_data = df.to_csv(index=False)
                            st.download_button(
                                label="📥 下载CSV文件",
                                data=csv_data,
                                file_name=f"companies_{search_mode}_{gl}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                        
                        with col_dl2:
                            json_data = json.dumps(companies, ensure_ascii=False, indent=2)
                            st.download_button(
                                label="📥 下载JSON文件",
                                data=json_data,
                                file_name=f"companies_{search_mode}_{gl}.json",
                                mime="application/json",
                                use_container_width=True
                            )
                        
                        # 显示文件保存位置
                        st.info(f"💾 结果已自动保存到: `output/company/` 目录")
                    else:
                        st.warning("未找到符合条件的企业")
                else:
                    st.error(f"❌ 搜索失败: {result['error']}")

# 侧边栏说明
with st.sidebar:
    st.header("📖 使用说明")
    st.markdown("""
    ### 搜索模式说明
    
    **通用搜索**
    - 在Google上搜索企业信息
    - 返回企业网站和基本信息
    
    **LinkedIn企业搜索**
    - 专门搜索LinkedIn企业页面
    - 获取更多企业详细信息
    
    **自定义查询**
    - 完全自定义搜索查询
    - 适合高级用户使用
    
    ### 搜索技巧
    
    1. **行业关键词**: 使用具体的行业术语
       - ✅ "solar panel manufacturing"
       - ❌ "energy"
    
    2. **地区选择**: 可以是国家、州或城市
       - ✅ "California", "London", "上海"
       - ✅ "Silicon Valley", "Bay Area"
    
    3. **组合搜索**: 同时使用多个条件获得精确结果
    """)
```

### 4. 实施步骤（1-2周）

#### 第1周：核心重构
1. **Day 1**: 项目结构搭建，环境配置
2. **Day 2-3**: 重构三个核心脚本为可复用的类/函数
3. **Day 4**: 实现Streamlit主框架和导航
4. **Day 5**: 完成企业搜索页面

#### 第2周：完善功能
1. **Day 1-2**: 实现联系信息提取页面
2. **Day 3**: 实现员工搜索页面
3. **Day 4**: UI优化和错误处理
4. **Day 5**: 测试和文档更新

### 5. 部署说明

#### 本地运行
```bash
# 安装依赖
pip install -r requirements.txt
playwright install chromium

# 配置环境变量
cp .env.example .env
# 编辑.env文件，填入API密钥

# 运行应用
streamlit run streamlit_app.py
```

#### Docker部署
```bash
# 构建镜像
docker build -t ai-customer-finder .

# 运行容器
docker run -p 8501:8501 -v $(pwd)/output:/app/output ai-customer-finder
```

### 6. 核心功能保证

✅ **保留所有原有功能**
- 企业搜索（通用/LinkedIn/自定义）
- 联系信息提取（支持批量）
- 员工搜索
- 多种LLM支持
- 结果导出（CSV/JSON）

✅ **用户体验提升**
- 可视化Web界面
- 实时进度显示
- 结果预览和筛选
- 一键下载

✅ **保持简单**
- 无需数据库
- 无需用户系统
- 无需复杂配置
- 开箱即用

### 7. 后续可能的增强

- 添加结果去重功能
- 支持历史记录查看
- 添加数据可视化图表
- 支持更多导出格式（Excel）
- 添加API调用统计