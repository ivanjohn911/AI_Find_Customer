"""
Company Search Page - Streamlit
Search for companies by industry, region, or custom queries
"""
import streamlit as st
import pandas as pd
import os
import json
from core.company_search import CompanySearcher
from components.common import (
    display_api_status, 
    show_usage_tips, 
    create_download_buttons,
    display_metrics,
    format_dataframe_columns
)

st.set_page_config(page_title="Company Search", page_icon="🔍", layout="wide")

st.title("🔍 Smart Company Search")
st.markdown("Search for target companies by industry, region, or custom queries")

# Initialize searcher
# Temporarily disable cache to ensure new code is loaded
# @st.cache_resource
def get_searcher():
    try:
        return CompanySearcher()
    except ValueError as e:
        st.error(f"Error initializing searcher: {str(e)}")
        return None

searcher = get_searcher()

if not searcher:
    st.error("Cannot initialize company searcher. Please check your API configuration.")
    st.stop()

# Search form
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Search Criteria")
    
    # Search mode selection
    search_mode = st.radio(
        "Search Mode",
        ["General Search", "LinkedIn Company Search", "Custom Query"],
        help="Choose different search modes"
    )
    
    # Input fields based on mode
    if search_mode == "Custom Query":
        custom_query = st.text_area(
            "Custom Search Query",
            placeholder="Enter complete search query, e.g.: renewable energy companies California",
            height=100
        )
        industry = None
        region = None
    else:
        custom_query = None
        industry = st.text_input(
            "Industry Keywords",
            placeholder="e.g.: solar energy, software, manufacturing"
        )
        
        region = st.text_input(
            "Region/Location",
            placeholder="e.g.: California, New York, London"
        )
        
        keywords = st.text_input(
            "Additional Keywords (Optional)",
            placeholder="Separate multiple keywords with commas",
            help="Add extra search keywords to refine results"
        )
    
    # Advanced options
    with st.expander("Advanced Options"):
        gl = st.selectbox(
            "Target Market",
            options=["us", "uk", "cn", "de", "fr", "jp", "au", "ca", "in", "br"],
            index=0,
            help="Select geographic preference for search"
        )
        
        num_results = st.slider(
            "Number of Results",
            min_value=10,
            max_value=100,
            value=30,
            step=10,
            help="Number of search results to return"
        )
    
    # Search button
    search_button = st.button("🚀 Start Search", type="primary", use_container_width=True)

# Results display area
with col2:
    st.subheader("Search Results")
    
    if search_button:
        # Validate input
        if search_mode == "Custom Query" and not custom_query:
            st.error("Please enter a custom query")
        elif search_mode != "Custom Query" and not industry and not region:
            st.error("Please enter at least industry or region")
        else:
            # Execute search
            with st.spinner("Searching for companies..."):
                # Prepare parameters
                search_params = {
                    "search_mode": "linkedin" if search_mode == "LinkedIn Company Search" else "general",
                    "gl": gl,
                    "num_results": num_results
                }
                
                if search_mode == "Custom Query":
                    search_params["custom_query"] = custom_query
                else:
                    search_params["industry"] = industry
                    search_params["region"] = region
                    if 'keywords' in locals() and keywords:
                        search_params["keywords"] = [k.strip() for k in keywords.split(",")]
                
                # Execute search
                result = searcher.search_companies(**search_params)
                
                if result["success"]:
                    companies = result["data"]
                    
                    if companies:
                        st.success(f"✅ Found {len(companies)} companies!")
                        
                        # Convert to DataFrame
                        df = pd.DataFrame(companies)
                        
                        # Display statistics
                        metrics = {
                            "Total Companies": len(companies),
                            "Unique Domains": df['domain'].dropna().nunique() if 'domain' in df else 0,
                            "LinkedIn Profiles": df['linkedin'].notna().sum() if 'linkedin' in df else 0
                        }
                        display_metrics(metrics)
                        
                        # Display data table
                        st.dataframe(
                            df,
                            use_container_width=True,
                            height=400,
                            column_config=format_dataframe_columns(df),
                            hide_index=True
                        )
                        
                        # Download options
                        st.divider()
                        st.subheader("📥 Download Results")
                        
                        filename_prefix = f"companies_{search_mode.lower().replace(' ', '_')}_{gl}"
                        create_download_buttons(df, filename_prefix, "both")
                        
                        # Show save location
                        if result.get("output_file"):
                            st.info(f"💾 Results saved to: `{result['output_file']}`")
                    else:
                        st.warning("No companies found matching your criteria")
                else:
                    st.error(f"❌ Search failed: {result['error']}")

# Sidebar content
with st.sidebar:
    # API status
    display_api_status()
    
    # Usage tips
    show_usage_tips("company_search")
    
    # Recent searches (if output directory exists)
    st.divider()
    st.header("📁 Recent Searches")
    
    company_dir = os.path.join("output", "company")
    if os.path.exists(company_dir):
        csv_files = [f for f in os.listdir(company_dir) if f.endswith('.csv')]
        csv_files.sort(key=lambda x: os.path.getmtime(os.path.join(company_dir, x)), reverse=True)
        
        if csv_files:
            recent_files = csv_files[:5]  # Show last 5 files
            for file in recent_files:
                file_path = os.path.join(company_dir, file)
                file_size = os.path.getsize(file_path) / 1024  # Convert to KB
                st.markdown(f"📄 {file[:30]}... ({file_size:.1f} KB)")
        else:
            st.info("No search results yet")