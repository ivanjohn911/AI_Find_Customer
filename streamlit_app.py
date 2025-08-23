"""
AI Customer Finder - Streamlit Web Application
Main entry point for the web interface
"""
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Customer Finder",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/AI_Find_Customer',
        'Report a bug': "https://github.com/your-repo/AI_Find_Customer/issues",
        'About': "# AI Customer Finder\nOpen-source B2B customer development tool"
    }
)

# Import common components
from components.common import check_api_keys, display_api_status, display_quick_links

# Main page
st.title("🤖 AI Customer Finder")
st.markdown("""
### Open-Source B2B Customer Intelligence Tool

This tool helps you:
- 🔍 **Smart Company Search** - Find target customers by industry and region
- 📧 **Contact Extraction** - Automatically extract emails, phones from websites
- 👥 **Employee Search** - Locate decision makers and key contacts

---

### Quick Start
1. Ensure API keys are configured in `.env` file
2. Select desired function from left navigation
3. Fill in search criteria and execute
4. View results and download data

### Output File Location
All results are saved in `output/` directory:
- Company search results: `output/company/`
- Contact information: `output/contact/`
- Employee information: `output/employee/`
""")

# Check API keys
api_status = check_api_keys()

if not api_status["SERPER_API_KEY"]:
    st.error("⚠️ Missing required API key: SERPER_API_KEY")
    st.info("Please configure it in the .env file")
    
    with st.expander("📝 How to configure API keys"):
        st.markdown("""
        1. Create a `.env` file in the project root directory
        2. Add your API keys:
        ```
        SERPER_API_KEY=your_serper_api_key_here
        LLM_PROVIDER=openai  # or anthropic, google, huoshan
        OPENAI_API_KEY=your_openai_key_here  # if using OpenAI
        ```
        3. Restart the application
        """)
    st.stop()

# Display configuration status in sidebar
display_api_status()

# Display quick links
display_quick_links()

# Feature cards
st.markdown("---")
st.subheader("🚀 Available Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 🔍 Company Search
    Search for companies by:
    - Industry keywords
    - Geographic location
    - Custom search queries
    - LinkedIn profiles
    
    [Go to Company Search →](/Company_Search)
    """)

with col2:
    st.markdown("""
    ### 📧 Contact Extraction
    Extract contact info from:
    - Single website URL
    - Batch CSV processing
    - Company search results
    - Contact pages crawling
    
    [Go to Contact Extraction →](/Contact_Extraction)
    """)

with col3:
    st.markdown("""
    ### 👥 Employee Search
    Find employees by:
    - Company name
    - Job position/title
    - Location filtering
    - LinkedIn profiles
    
    [Go to Employee Search →](/Employee_Search)
    """)

# Statistics section
st.markdown("---")
st.subheader("📊 Usage Statistics")

# Check for existing output files
output_dir = "output"
stats = {}

if os.path.exists(output_dir):
    # Count files in each subdirectory
    for subdir in ["company", "contact", "employee"]:
        subdir_path = os.path.join(output_dir, subdir)
        if os.path.exists(subdir_path):
            csv_files = len([f for f in os.listdir(subdir_path) if f.endswith('.csv')])
            stats[subdir] = csv_files

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Company Files", stats.get("company", 0))
    
    with col2:
        st.metric("Contact Files", stats.get("contact", 0))
    
    with col3:
        st.metric("Employee Files", stats.get("employee", 0))
else:
    st.info("No output files generated yet. Start by searching for companies!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray;">
    <small>
    AI Customer Finder v1.0 | 
    <a href="https://github.com/your-repo/AI_Find_Customer">GitHub</a> | 
    <a href="https://github.com/your-repo/AI_Find_Customer/wiki">Documentation</a>
    </small>
</div>
""", unsafe_allow_html=True)