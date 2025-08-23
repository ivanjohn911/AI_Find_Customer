"""
Employee Search Core Module
Refactored from serper_employee_search.py for web interface
"""
import json
import os
import time
import csv
import re
import random
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure output directories exist
OUTPUT_DIR = "output"
EMPLOYEE_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "employee")
if not os.path.exists(EMPLOYEE_OUTPUT_DIR):
    os.makedirs(EMPLOYEE_OUTPUT_DIR, exist_ok=True)


class EmployeeSearcher:
    """Employee and decision maker search using Serper API"""
    
    MAX_RETRIES = 3
    
    def __init__(self):
        """Initialize employee searcher"""
        self.api_key = os.getenv("SERPER_API_KEY")
        if not self.api_key:
            raise ValueError("SERPER_API_KEY not found in environment variables")
        
        self.base_url = "https://google.serper.dev/search"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Use session for connection pooling and set default headers
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search_employees(
        self,
        company_name: str,
        position: Optional[str] = None,
        location: Optional[str] = None,
        country: Optional[str] = None,
        additional_keywords: Optional[List[str]] = None,
        gl: str = "us",
        num_results: int = 20
    ) -> Dict:
        """
        Search for employees at a specific company
        
        Args:
            company_name: Name of the company
            position: Job position/title to search for
            location: City/state location filter
            country: Country filter
            additional_keywords: Additional search keywords
            gl: Geographic location for search
            num_results: Number of results to return
            
        Returns:
            Dictionary with search results
        """
        try:
            # Construct search query
            query_parts = ["site:linkedin.com/in"]
            
            if company_name:
                query_parts.append(f'"{company_name}"')
            
            if position:
                query_parts.append(f'"{position}"')
            
            if location:
                query_parts.append(f'"{location}"')
            
            if country:
                query_parts.append(f'"{country}"')
            
            if additional_keywords:
                query_parts.extend(additional_keywords)
            
            query = " ".join(query_parts)
            
            # Prepare API request
            payload = json.dumps({
                "q": query,
                "gl": gl,
                "num": num_results
            })
            
            # Execute search with retries
            for attempt in range(self.MAX_RETRIES):
                try:
                    response = self.session.post(
                        self.base_url,
                        data=payload
                    )
                    response.raise_for_status()
                    results = response.json()
                    
                    # Extract employee information
                    employees = self._extract_employees(results, company_name, query)
                    
                    # Save results
                    output_file = self._save_results(
                        employees, company_name, position, gl
                    )
                    
                    return {
                        "success": True,
                        "data": employees,
                        "query": query,
                        "error": None,
                        "output_file": output_file
                    }
                    
                except requests.exceptions.RequestException as e:
                    if attempt < self.MAX_RETRIES - 1:
                        backoff_time = (2 ** attempt) * random.uniform(1, 3)
                        time.sleep(backoff_time)
                    else:
                        raise Exception(f"Failed after {self.MAX_RETRIES} retries: {str(e)}")
            
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "query": query if 'query' in locals() else "",
                "error": str(e),
                "output_file": None
            }
    
    def search_multiple_companies(
        self,
        companies: List[str],
        position: Optional[str] = None,
        location: Optional[str] = None,
        gl: str = "us",
        num_results: int = 20,
        progress_callback=None
    ) -> Dict:
        """
        Search for employees across multiple companies
        
        Args:
            companies: List of company names
            position: Job position/title to search for
            location: Location filter
            gl: Geographic location for search
            num_results: Number of results per company
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with aggregated results
        """
        all_employees = []
        failed_companies = []
        
        for i, company in enumerate(companies):
            if progress_callback:
                progress_callback(i + 1, len(companies), company)
            
            result = self.search_employees(
                company_name=company,
                position=position,
                location=location,
                gl=gl,
                num_results=num_results
            )
            
            if result["success"]:
                all_employees.extend(result["data"])
            else:
                failed_companies.append(company)
            
            # Small delay between searches
            if i < len(companies) - 1:
                time.sleep(2)
        
        # Save aggregated results
        if all_employees:
            timestamp = int(time.time())
            position_str = position.replace(' ', '_').lower() if position else 'all'
            filename = f"employees_batch_{position_str}_{gl}_{timestamp}"
            output_file = self._save_results(all_employees, None, position, gl, filename)
        else:
            output_file = None
        
        return {
            "success": len(all_employees) > 0,
            "data": all_employees,
            "total_found": len(all_employees),
            "companies_searched": len(companies),
            "failed_companies": failed_companies,
            "output_file": output_file
        }
    
    def _extract_employees(self, search_results: Dict, company_name: str, query: str) -> List[Dict]:
        """Extract employee information from search results"""
        employees = []
        
        if not search_results or 'organic' not in search_results:
            return employees
        
        for result in search_results.get('organic', []):
            link = result.get('link', '')
            
            # Only process LinkedIn profile pages
            if 'linkedin.com/in/' in link:
                # Extract name from title or URL
                title = result.get('title', '')
                name = self._extract_name(title, link)
                
                # Extract job title from snippet
                snippet = result.get('snippet', '')
                job_title = self._extract_job_title(snippet, title)
                
                employee_info = {
                    'name': name,
                    'title': job_title,
                    'company': company_name,
                    'linkedin_url': link,
                    'description': snippet,
                    'email': self._extract_email(snippet),
                    'phone': self._extract_phone(snippet),
                    'search_query': query
                }
                
                # Extract social media if present
                social_links = self._extract_social_links(snippet)
                employee_info.update(social_links)
                
                employees.append(employee_info)
        
        return employees
    
    def _extract_name(self, title: str, url: str) -> str:
        """Extract person's name from title or URL"""
        # Try to extract from title first
        if title:
            # Common LinkedIn title format: "Name - Title - Company | LinkedIn"
            parts = title.split(' - ')
            if parts:
                return parts[0].strip()
        
        # Try to extract from URL
        if '/in/' in url:
            username = url.split('/in/')[-1].split('/')[0]
            # Convert URL format to name (john-doe -> John Doe)
            name_parts = username.replace('-', ' ').title()
            return name_parts
        
        return "Unknown"
    
    def _extract_job_title(self, snippet: str, title: str) -> str:
        """Extract job title from snippet or title"""
        # Try title first
        if ' - ' in title:
            parts = title.split(' - ')
            if len(parts) > 1:
                return parts[1].strip()
        
        # Look for common patterns in snippet
        title_patterns = [
            r'(?:^|\n)([A-Z][^.!?\n]{10,50})\s+at\s+',
            r'(?:^|\n)([A-Z][^.!?\n]{10,50})\s+@\s+',
            r'(?:^|\n)([A-Z][^.!?\n]{10,50})\s+\|\s+',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, snippet)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_email(self, text: str) -> str:
        """Extract email from text"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0) if match else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number from text"""
        phone_pattern = r'(\+\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
        match = re.search(phone_pattern, text)
        return match.group(0) if match else ""
    
    def _extract_social_links(self, text: str) -> Dict[str, str]:
        """Extract social media links from text"""
        social_links = {}
        
        patterns = {
            'twitter': r'twitter\.com/([a-zA-Z0-9_]+)',
            'github': r'github\.com/([a-zA-Z0-9-]+)',
        }
        
        for platform, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                social_links[platform] = f"https://{platform}.com/{match.group(1)}"
        
        return social_links
    
    def _save_results(
        self,
        employees: List[Dict],
        company_name: Optional[str],
        position: Optional[str],
        gl: str,
        filename: Optional[str] = None
    ) -> str:
        """Save employee search results to CSV and JSON"""
        if not filename:
            timestamp = int(time.time())
            company_str = company_name.replace(' ', '_').lower() if company_name else 'multiple'
            position_str = position.replace(' ', '_').lower() if position else 'all'
            filename = f"employees_{company_str}_{position_str}_{gl}_{timestamp}"
        
        csv_path = os.path.join(EMPLOYEE_OUTPUT_DIR, f"{filename}.csv")
        json_path = os.path.join(EMPLOYEE_OUTPUT_DIR, f"{filename}.json")
        
        # Save to CSV
        if employees:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['name', 'title', 'company', 'linkedin_url', 'email', 
                             'phone', 'description', 'twitter', 'github']
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(employees)
        
        # Save to JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(employees, f, indent=2, ensure_ascii=False)
        
        return csv_path
    
    def __del__(self):
        """Cleanup on deletion"""
        if hasattr(self, 'session'):
            self.session.close()