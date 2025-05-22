#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import time
import csv
import re
import argparse
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure output directories exist
OUTPUT_DIR = "output"
COMPANY_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "company")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
if not os.path.exists(COMPANY_OUTPUT_DIR):
    os.makedirs(COMPANY_OUTPUT_DIR)
    print(f"Created output directory: {COMPANY_OUTPUT_DIR}")

class SerperCompanySearch:
    def __init__(self, output_file="company_search_results.csv", gl="us", num_results=30):
        self.api_key = os.getenv("SERPER_API_KEY")
        if not self.api_key:
            raise ValueError("SERPER_API_KEY not found in environment variables")
        
        # Ensure output file goes to the company output directory
        self.output_file = os.path.join(COMPANY_OUTPUT_DIR, output_file)
        self.base_url = "https://google.serper.dev/search"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Default geolocation and number of results
        self.gl = gl
        self.num_results = num_results
    
    def extract_domain(self, url):
        """Extract domain from URL"""
        domain_pattern = r'https?://(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        match = re.search(domain_pattern, url)
        if match:
            return match.group(1)
        return ""
    
    def search_linkedin_companies(self, industry=None, region=None, additional_keywords=None):
        """Search for companies on LinkedIn based on industry, region, and keywords"""
        # Construct the search query
        query_parts = ["site:linkedin.com/company"]
        
        if industry:
            query_parts.append(f'"{industry}"')
        
        if region:
            query_parts.append(f'"{region}"')
        
        if additional_keywords:
            if isinstance(additional_keywords, list):
                query_parts.extend(additional_keywords)
            else:
                query_parts.append(additional_keywords)
        
        query = " ".join(query_parts)
        print(f"Searching LinkedIn companies with: {query}")
        
        payload = json.dumps({
            "q": query,
            "gl": self.gl,
            "num": self.num_results
        })
        
        try:
            response = requests.post(self.base_url, headers=self.headers, data=payload)
            response.raise_for_status()
            results = response.json()
            
            # Process results
            companies = self.extract_linkedin_companies(results, query)
            
            # Create a filename with search parameters and timestamp
            timestamp = int(time.time())
            industry_str = industry.replace(' ', '_').lower() if industry else 'no_industry'
            region_str = region.replace(' ', '_').lower() if region else 'no_region'
            gl_str = self.gl.lower()
            
            output_file = os.path.join(COMPANY_OUTPUT_DIR, 
                f"linkedin_{industry_str}_{region_str}_{gl_str}_{timestamp}.csv")
            
            self.save_linkedin_results(companies, output_file)
            
            return companies
        except requests.exceptions.RequestException as e:
            print(f"Error searching LinkedIn companies: {e}")
            return None
    
    def extract_linkedin_companies(self, search_results, query):
        """Extract company information from LinkedIn search results"""
        companies = []
        
        if not search_results or 'organic' not in search_results:
            return companies
        
        for idx, result in enumerate(search_results.get('organic', [])):
            link = result.get('link', '')
            
            # Only process LinkedIn company pages
            if 'linkedin.com/company/' in link:
                # Extract company name from the LinkedIn URL
                company_name_match = re.search(r'linkedin\.com/company/([^/]+)', link)
                company_name = company_name_match.group(1).replace('-', ' ').title() if company_name_match else ""
                
                if not company_name and result.get('title'):
                    # Try to extract from title
                    company_name = result.get('title').split('|')[0].split('-')[0].strip()
                
                company_info = {
                    'name': company_name,
                    'query': query,
                    'url': result.get('link', ''),
                    'title': result.get('title', ''),
                    'description': result.get('snippet', ''),
                    'domain': '',  # We don't have the domain from LinkedIn directly
                    'linkedin': link,
                    'type': 'linkedin_search'
                }
                companies.append(company_info)
        
        return companies
    
    def save_linkedin_results(self, companies, output_file=None):
        """Save LinkedIn company information to CSV file"""
        if output_file is None:
            # Generate a default name with timestamp if none provided
            timestamp = int(time.time())
            output_file = os.path.join(COMPANY_OUTPUT_DIR, f"linkedin_companies_{timestamp}.csv")
            
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow([
                'Company Name', 'Search Query', 'LinkedIn URL', 'Title', 'Description', 
                'Type', 'GL'
            ])
            # Write data
            for company in companies:
                writer.writerow([
                    company['name'],
                    company['query'],
                    company['linkedin'],
                    company['title'],
                    company['description'],
                    company['type'],
                    self.gl
                ])
        
        print(f"LinkedIn search results saved to {output_file}")
        
        # Also save as JSON
        json_output_file = output_file.replace('.csv', '.json')
        with open(json_output_file, 'w', encoding='utf-8') as f:
            # Add gl to each company record in the JSON
            for company in companies:
                company['gl'] = self.gl
            json.dump(companies, f, indent=2, ensure_ascii=False)
        
        print(f"LinkedIn search results also saved to {json_output_file}")
        
        return output_file
    
    def search_general_companies(self, industry=None, region=None, additional_keywords=None, custom_query=None):
        """Search for companies on Google based on industry, region, and keywords without LinkedIn restriction"""
        # Use custom query if provided, otherwise construct the search query
        if custom_query:
            query = custom_query
            print(f"Searching with custom query: {query}")
            query_for_results = custom_query  # 保存原始自定义查询
        else:
            # Construct the search query
            query_parts = ["company", "business"]
            
            if industry:
                query_parts.append(f'"{industry}"')
            
            if region:
                query_parts.append(f'"{region}"')
            
            if additional_keywords:
                if isinstance(additional_keywords, list):
                    query_parts.extend(additional_keywords)
                else:
                    query_parts.append(additional_keywords)
            
            query = " ".join(query_parts)
            query_for_results = query
            print(f"Searching companies with: {query}")
        
        payload = json.dumps({
            "q": query,
            "gl": self.gl,
            "num": self.num_results
        })
        
        try:
            response = requests.post(self.base_url, headers=self.headers, data=payload)
            response.raise_for_status()
            results = response.json()
            
            # Extract information for multiple companies
            companies = self.extract_general_companies(results, query_for_results, custom_query)
            
            # Create a filename with search parameters and timestamp
            timestamp = int(time.time())
            if custom_query:
                # 处理自定义查询，使其适合作为文件名
                query_str = custom_query.replace(' ', '_').replace('"', '').lower()
                # 限制长度并移除不合法的文件名字符
                query_str = ''.join(c for c in query_str if c.isalnum() or c in '_-')[:40]
                gl_str = self.gl.lower()
                output_file = os.path.join(COMPANY_OUTPUT_DIR, 
                    f"general_custom_{query_str}_{gl_str}_{timestamp}.csv")
            else:
                industry_str = industry.replace(' ', '_').lower() if industry else 'no_industry'
                region_str = region.replace(' ', '_').lower() if region else 'no_region'
                gl_str = self.gl.lower()
                output_file = os.path.join(COMPANY_OUTPUT_DIR, 
                    f"general_{industry_str}_{region_str}_{gl_str}_{timestamp}.csv")
            
            # Save results
            self.save_general_results(companies, output_file)
            
            print(f"\nFound {len(companies)} potential companies matching search criteria")
            print(f"Results saved to {output_file} and {output_file.replace('.csv', '.json')}")
            
            return companies
        except requests.exceptions.RequestException as e:
            print(f"Error searching for companies: {e}")
            return None
    
    def extract_general_companies(self, search_results, query, custom_query=None):
        """Extract company information from general search results"""
        companies = []
        
        if not search_results or 'organic' not in search_results:
            return companies
        
        for idx, result in enumerate(search_results.get('organic', [])):
            link = result.get('link', '')
            title = result.get('title', '')
            description = result.get('snippet', '')
            
            # Skip obvious non-company results
            skip_domains = ['wikipedia.org', 'youtube.com', 'linkedin.com/in/', 'twitter.com/hashtag']
            if any(domain in link for domain in skip_domains):
                continue
            
            # Check if result appears to be a company
            # We'll use some basic heuristics like looking for company indicators in title/description
            company_indicators = [
                'company', 'corporation', 'inc', 'ltd', 'limited', 'gmbh', 'co.', 'corp', 
                'business', 'enterprise', 'industry', 'manufacturer', 'supplier', 'service'
            ]
            
            # Simplistic check - if result contains company indicators or has company-like domain
            is_likely_company = (
                any(indicator in title.lower() or indicator in description.lower() for indicator in company_indicators) or
                self.extract_domain(link) # Any domain probably represents a company
            )
            
            if is_likely_company:
                # Try to extract company name from title
                company_name = title.split('-')[0].split('|')[0].strip()
                
                company_info = {
                    'name': company_name,
                    'query': query,
                    'url': link,
                    'title': title,
                    'description': description,
                    'domain': self.extract_domain(link),
                    'type': "general_search"
                }
                
                # 添加自定义查询信息
                if custom_query:
                    company_info['custom_query'] = custom_query
                
                # Look for social links if available
                if 'linkedin.com/company' in link:
                    company_info['linkedin'] = link
                else:
                    company_info['linkedin'] = ""
                
                companies.append(company_info)
        
        return companies

    def save_general_results(self, companies, output_file=None):
        """Save general company information to CSV file"""
        if output_file is None:
            # Generate a default name with timestamp if none provided
            timestamp = int(time.time())
            output_file = os.path.join(COMPANY_OUTPUT_DIR, f"general_companies_{timestamp}.csv")
            
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow([
                'Company Name', 'Search Query', 'URL', 'Title', 'Description', 'Domain', 
                'LinkedIn', 'Type', 'Custom Query', 'GL'
            ])
            # Write data
            for company in companies:
                writer.writerow([
                    company.get('name', ''),
                    company.get('query', ''),
                    company.get('url', ''),
                    company.get('title', ''),
                    company.get('description', ''),
                    company.get('domain', ''),
                    company.get('linkedin', ''),
                    company.get('type', ''),
                    company.get('custom_query', ''),
                    self.gl
                ])
        
        print(f"General search results saved to {output_file}")
        
        # Also save as JSON
        json_output_file = output_file.replace('.csv', '.json')
        with open(json_output_file, 'w', encoding='utf-8') as f:
            # Add gl to each company record in the JSON
            for company in companies:
                company['gl'] = self.gl
            json.dump(companies, f, indent=2, ensure_ascii=False)
        
        print(f"General search results also saved to {json_output_file}")
        
        return output_file

def main():
    parser = argparse.ArgumentParser(description="Company search using Serper API")
    parser.add_argument("--linkedin-search", action="store_true", help="Search for companies on LinkedIn")
    parser.add_argument("--general-search", action="store_true", help="Search for companies on Google (not restricted to LinkedIn)")
    parser.add_argument("--industry", help="Industry keyword for company search")
    parser.add_argument("--region", help="Region/location for company search")
    parser.add_argument("--keywords", help="Additional keywords for company search, comma separated")
    parser.add_argument("--output", "-o", help="Output CSV file name")
    parser.add_argument("--gl", help="Geolocation parameter (e.g. 'us', 'fr', 'de', 'cn')", default="us")
    parser.add_argument("--num", type=int, help="Number of search results to return", default=30)
    parser.add_argument("--custom-query", help="Custom search query (overrides industry, region, and default keywords)")
    
    args = parser.parse_args()
    
    # Generate output filename with parameters and timestamp
    timestamp = int(time.time())
    output_file = None
    
    if args.linkedin_search or args.general_search:
        # 如果提供了自定义查询，使用它来生成文件名
        if args.custom_query:
            # 处理自定义查询，使其适合作为文件名
            query_str = args.custom_query.replace(' ', '_').replace('"', '').lower()
            # 限制长度并移除不合法的文件名字符
            query_str = ''.join(c for c in query_str if c.isalnum() or c in '_-')[:40]
            gl_str = args.gl.lower()
            
            search_type = "linkedin" if args.linkedin_search else "general"
            output_file = f"{search_type}_custom_{query_str}_{gl_str}_{timestamp}.csv"
        else:
            # 使用行业和地区生成文件名
            industry_str = args.industry.replace(' ', '_').lower() if args.industry else 'no_industry'
            region_str = args.region.replace(' ', '_').lower() if args.region else 'no_region'
            gl_str = args.gl.lower()
            
            search_type = "linkedin" if args.linkedin_search else "general"
            output_file = f"{search_type}_{industry_str}_{region_str}_{gl_str}_{timestamp}.csv"
    
    # Use specified output file if provided
    if args.output:
        output_file = args.output
    
    searcher = SerperCompanySearch(
        output_file=output_file,
        gl=args.gl,
        num_results=args.num
    )
    
    if args.linkedin_search:
        # Process keywords if provided
        additional_keywords = None
        if args.keywords:
            additional_keywords = [kw.strip() for kw in args.keywords.split(',')]
            
        companies = searcher.search_linkedin_companies(
            industry=args.industry,
            region=args.region,
            additional_keywords=additional_keywords
        )
        
        # Display results
        if companies:
            print(f"\nFound {len(companies)} LinkedIn companies")
            print(f"Industry: {args.industry or 'Not specified'}")
            print(f"Region: {args.region or 'Not specified'}")
            print(f"Keywords: {args.keywords or 'Not specified'}")
            print(f"Region (gl): {args.gl}")
            print("-" * 50)
            
            # Show details for up to 5 companies
            for i, company in enumerate(companies[:5]):
                print(f"Company {i+1}: {company['name']}")
                print(f"LinkedIn: {company['linkedin']}")
                print(f"Description: {company['description'][:100]}..." if company['description'] else "Description: N/A")
                print("-" * 50)
    
    elif args.general_search:
        # Process keywords if provided
        additional_keywords = None
        if args.keywords:
            additional_keywords = [kw.strip() for kw in args.keywords.split(',')]
            
        companies = searcher.search_general_companies(
            industry=args.industry,
            region=args.region,
            additional_keywords=additional_keywords,
            custom_query=args.custom_query
        )
        
        # Display results
        if companies:
            print(f"\nFound {len(companies)} companies")
            print(f"Industry: {args.industry or 'Not specified'}")
            print(f"Region: {args.region or 'Not specified'}")
            print(f"Keywords: {args.keywords or 'Not specified'}")
            print(f"Region (gl): {args.gl}")
            print("-" * 50)
            
            # Show details for up to 5 companies
            for i, company in enumerate(companies[:5]):
                print(f"Company {i+1}: {company['name']}")
                print(f"Website: {company['url']}")
                print(f"Domain: {company['domain']}")
                if company.get('linkedin'):
                    print(f"LinkedIn: {company['linkedin']}")
                print(f"Description: {company['description'][:100]}..." if company['description'] else "Description: N/A")
                print("-" * 50)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 