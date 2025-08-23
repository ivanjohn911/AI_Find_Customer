"""
Employee Search Page - Streamlit
Search for employees and decision makers in companies
"""
import streamlit as st
import pandas as pd
import os
import sys
import time
import json
from components.common import (
    display_api_status,
    show_usage_tips,
    create_download_buttons,
    display_metrics
)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Employee Search", page_icon="👥", layout="wide")

st.title("👥 Employee & Decision Maker Search")
st.markdown("Find key employees and decision makers in target companies")

# Import refactored employee search module
try:
    from core.employee_search import EmployeeSearcher
    search_available = True
except ImportError as e:
    st.error(f"Error importing employee search module: {str(e)}")
    search_available = False

# Main content
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Search Criteria")
    
    # Input method
    input_method = st.radio(
        "Input Method",
        ["Single Company", "Company List (CSV)"],
        help="Choose how to specify target companies"
    )
    
    if input_method == "Single Company":
        company_name = st.text_input(
            "Company Name",
            placeholder="e.g., Tesla, Microsoft, Apple",
            help="Enter the name of the company"
        )
        
    else:
        # CSV file selection from company search results
        company_dir = os.path.join("output", "company")
        if os.path.exists(company_dir):
            csv_files = [f for f in os.listdir(company_dir) if f.endswith('.csv')]
            if csv_files:
                selected_file = st.selectbox(
                    "Select Company List",
                    options=csv_files,
                    help="Choose from previous company search results"
                )
                
                # Preview selected file
                if selected_file:
                    file_path = os.path.join(company_dir, selected_file)
                    df_preview = pd.read_csv(file_path)
                    st.info(f"Selected file contains {len(df_preview)} companies")
                    
                    # Select company name column
                    name_columns = df_preview.columns.tolist()
                    company_column = st.selectbox(
                        "Company Name Column",
                        options=name_columns,
                        index=name_columns.index("name") if "name" in name_columns else 0
                    )
            else:
                st.warning("No company files found. Please run a company search first.")
                selected_file = None
        else:
            st.warning("No company directory found.")
            selected_file = None
    
    # Position/Title search
    position = st.text_input(
        "Position/Title",
        placeholder="e.g., CEO, Sales Director, Marketing Manager",
        help="Specify the job title or position to search for"
    )
    
    # Location filters
    with st.expander("Location Filters (Optional)"):
        location = st.text_input(
            "City/State",
            placeholder="e.g., San Francisco, California",
            help="Filter by location"
        )
        
        country = st.text_input(
            "Country",
            placeholder="e.g., United States, UK",
            help="Filter by country"
        )
    
    # Advanced options
    with st.expander("Advanced Options"):
        gl = st.selectbox(
            "Search Region",
            options=["us", "uk", "cn", "de", "fr", "jp", "au", "ca", "in", "br"],
            index=0,
            help="Geographic region for search"
        )
        
        num_results = st.slider(
            "Results per Company",
            min_value=5,
            max_value=50,
            value=20,
            step=5,
            help="Number of employee results per company"
        )
    
    # Search button
    search_button = st.button("🔍 Search Employees", type="primary", use_container_width=True)

# Results area
with col2:
    st.subheader("Search Results")
    
    if search_button and search_available:
        # Validate input
        companies_to_search = []
        
        if input_method == "Single Company":
            if company_name and position:
                companies_to_search = [company_name]
            else:
                st.error("Please enter both company name and position")
                
        else:
            if selected_file and position:
                file_path = os.path.join(company_dir, selected_file)
                df_companies = pd.read_csv(file_path)
                if 'company_column' in locals():
                    companies_to_search = df_companies[company_column].dropna().tolist()
                    # Limit for demo
                    if len(companies_to_search) > 5:
                        st.warning(f"Demo mode: Searching first 5 companies only")
                        companies_to_search = companies_to_search[:5]
                else:
                    st.error("Please select a company name column")
            else:
                st.error("Please select a file and enter a position")
        
        if companies_to_search:
            # Initialize search
            with st.spinner(f"Searching for {position} in {len(companies_to_search)} companies..."):
                try:
                    # Create searcher instance
                    searcher = EmployeeSearcher()
                    
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    all_employees = []
                    
                    # Search each company
                    for i, company in enumerate(companies_to_search):
                        # Update progress
                        progress = (i + 1) / len(companies_to_search)
                        progress_bar.progress(progress)
                        status_text.text(f"Searching {company}...")
                        
                        # Perform search
                        result = searcher.search_employees(
                            company_name=company,
                            position=position,
                            location=location if 'location' in locals() and location else None,
                            country=country if 'country' in locals() and country else None,
                            gl=gl,
                            num_results=num_results
                        )
                        
                        if result['success'] and result['data']:
                            all_employees.extend(result['data'])
                    
                    # Clear progress
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Display results
                    if all_employees:
                        st.success(f"✅ Found {len(all_employees)} employees!")
                        
                        # Convert to DataFrame
                        df_results = pd.DataFrame(all_employees)
                        
                        # Display metrics
                        metrics = {
                            "Total Profiles": len(all_employees),
                            "Companies": df_results['company'].nunique() if 'company' in df_results else 0,
                            "With Email": df_results['email'].notna().sum() if 'email' in df_results else 0,
                            "LinkedIn Profiles": df_results['linkedin_url'].notna().sum() if 'linkedin_url' in df_results else 0
                        }
                        display_metrics(metrics)
                        
                        # Display table
                        display_columns = ['name', 'title', 'company', 'linkedin_url', 'email', 'description']
                        display_df = df_results[[col for col in display_columns if col in df_results.columns]]
                        
                        st.dataframe(
                            display_df,
                            use_container_width=True,
                            height=400,
                            column_config={
                                "linkedin_url": st.column_config.LinkColumn("LinkedIn"),
                                "name": st.column_config.TextColumn("Name", width="medium"),
                                "title": st.column_config.TextColumn("Title", width="medium"),
                                "company": st.column_config.TextColumn("Company", width="medium"),
                            },
                            hide_index=True
                        )
                        
                        # Download options
                        st.divider()
                        st.subheader("📥 Download Results")
                        
                        # Generate timestamp for filename
                        timestamp = int(time.time())
                        filename_prefix = f"employees_{position.replace(' ', '_')}_{gl}_{timestamp}"
                        create_download_buttons(df_results, filename_prefix, "both")
                        
                        # Save info - Note: output_file may not be available in batch search
                        st.info(f"💾 Results available for download")
                        
                    else:
                        st.warning(f"No employees found with position '{position}' in the specified companies")
                        
                except Exception as e:
                    st.error(f"Search error: {str(e)}")
                    progress_bar.empty()
                    status_text.empty()

# Sidebar
with st.sidebar:
    # API status
    display_api_status()
    
    # Usage tips
    show_usage_tips("employee_search")
    
    # Recent searches
    st.divider()
    st.header("📁 Recent Searches")
    
    employee_dir = os.path.join("output", "employee")
    if os.path.exists(employee_dir):
        csv_files = [f for f in os.listdir(employee_dir) if f.endswith('.csv')]
        csv_files.sort(key=lambda x: os.path.getmtime(os.path.join(employee_dir, x)), reverse=True)
        
        if csv_files:
            recent_files = csv_files[:5]
            for file in recent_files:
                file_path = os.path.join(employee_dir, file)
                file_size = os.path.getsize(file_path) / 1024
                st.markdown(f"📄 {file[:30]}... ({file_size:.1f} KB)")
        else:
            st.info("No search results yet")