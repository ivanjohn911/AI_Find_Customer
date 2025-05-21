#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import time
import csv
import re
import argparse
import random
import sys
import logging
import requests
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Ensure output directories exist
OUTPUT_DIR = "output"
EMPLOYEE_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "employee")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    logger.info(f"Created output directory: {OUTPUT_DIR}")
if not os.path.exists(EMPLOYEE_OUTPUT_DIR):
    os.makedirs(EMPLOYEE_OUTPUT_DIR)
    logger.info(f"Created employee output directory: {EMPLOYEE_OUTPUT_DIR}")

# Maximum retries for API requests
MAX_RETRIES = 3

class SerperEmployeeSearch:
    def __init__(self, output_file=None, gl="us", num_results=30):
        self.api_key = os.getenv("SERPER_API_KEY")
        if not self.api_key:
            raise ValueError("SERPER_API_KEY not found in environment variables")
        
        self.output_file = output_file
        if self.output_file:
            self.output_file = os.path.join(EMPLOYEE_OUTPUT_DIR, self.output_file)
        
        self.base_url = "https://google.serper.dev/search"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Default geolocation and number of results
        self.gl = gl
        self.num_results = num_results
        
        # Initialize CSV file if output file is provided
        if self.output_file:
            self._initialize_csv()
    
    def _initialize_csv(self):
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Name', 'Title', 'Company', 'LinkedIn URL', 'Description', 'Email', 
                'Phone', 'Twitter', 'Facebook', 'Instagram', 'Search Query'
            ])
    
    def extract_email(self, text):
        """Extract email addresses from text"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        if match:
            return match.group(0)
        return ""
    
    def extract_phone(self, text):
        """Extract phone numbers from text"""
        # Basic pattern for phone numbers
        phone_pattern = r'(\+\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
        match = re.search(phone_pattern, text)
        if match:
            return match.group(0)
        return ""
    
    def extract_social_links(self, results):
        """Extract social media links from search results"""
        social_links = {
            'twitter': "",
            'facebook': "",
            'instagram': ""
        }
        
        # Look for social links in organic results
        for result in results.get('organic', []):
            link = result.get('link', '')
            
            if ('twitter.com' in link or 'x.com' in link) and not social_links['twitter']:
                social_links['twitter'] = link
            elif 'facebook.com' in link and not social_links['facebook']:
                social_links['facebook'] = link
            elif 'instagram.com' in link and not social_links['instagram']:
                social_links['instagram'] = link
        
        return social_links
    
    def search_employees(self, company_name, position, location=None, country=None, additional_keywords=None):
        """Search for employees with specific position at a company"""
        # Construct the search query
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
            if isinstance(additional_keywords, list):
                query_parts.extend(additional_keywords)
            else:
                query_parts.append(additional_keywords)
        
        query = " ".join(query_parts)
        logger.info(f"Searching employees with: {query}")
        
        payload = json.dumps({
            "q": query,
            "gl": self.gl,
            "num": self.num_results
        })
        
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.post(self.base_url, headers=self.headers, data=payload)
                response.raise_for_status()
                results = response.json()
                
                # Process results
                employees = self.extract_employees(results, company_name, position, query)
                
                # If output file wasn't provided in constructor, generate one based on search
                if not self.output_file:
                    timestamp = int(time.time())
                    company_str = company_name.lower().replace(' ', '_')
                    position_str = position.lower().replace(' ', '_')
                    gl_str = self.gl.lower()
                    location_str = location.lower().replace(' ', '_') if location else 'no_location'
                    
                    output_file = os.path.join(
                        EMPLOYEE_OUTPUT_DIR, 
                        f"{company_str}_{position_str}_{location_str}_{gl_str}_{timestamp}.csv"
                    )
                    self.output_file = output_file
                    self._initialize_csv()
                
                # Save results
                self.save_results(employees)
                
                # Also save as JSON
                json_output_file = self.output_file.replace('.csv', '.json')
                with open(json_output_file, 'w', encoding='utf-8') as f:
                    json.dump(employees, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Found {len(employees)} employees matching the search criteria")
                logger.info(f"Results saved to {self.output_file} and {json_output_file}")
                
                return employees
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt+1}/{MAX_RETRIES} failed: {e}")
                if attempt < MAX_RETRIES - 1:
                    # Calculate exponential backoff delay
                    backoff_time = (2 ** attempt) * random.uniform(5, 15)
                    logger.info(f"Waiting {backoff_time:.1f} seconds before retrying...")
                    time.sleep(backoff_time)
                else:
                    logger.error("Failed to search employees after maximum retries")
                    return []
    
    def extract_employees(self, search_results, company_name, position, query):
        """Extract employee information from search results"""
        employees = []
        
        if not search_results or 'organic' not in search_results:
            return employees
        
        for result in search_results.get('organic', []):
            link = result.get('link', '')
            
            # Only process LinkedIn personal profiles
            if 'linkedin.com/in/' in link:
                title = result.get('title', '')
                description = result.get('snippet', '')
                
                # Extract the person's name from the title
                # LinkedIn titles are typically "Name - Position at Company | LinkedIn"
                name = ""
                if " - " in title:
                    name = title.split(' - ')[0].strip()
                elif " | " in title:
                    name = title.split(' | ')[0].strip()
                
                employee_info = {
                    'name': name,
                    'title': position,  # Use the searched position
                    'company': company_name,
                    'url': link,
                    'description': description,
                    'email': self.extract_email(description),
                    'phone': self.extract_phone(description),
                    'twitter': "",
                    'facebook': "",
                    'instagram': "",
                    'query': query
                }
                
                # Add to employees list
                employees.append(employee_info)
        
        return employees
    
    def save_results(self, employees):
        """Save employee information to CSV file"""
        with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for employee in employees:
                writer.writerow([
                    employee.get('name', ''),
                    employee.get('title', ''),
                    employee.get('company', ''),
                    employee.get('url', ''),
                    employee.get('description', ''),
                    employee.get('email', ''),
                    employee.get('phone', ''),
                    employee.get('twitter', ''),
                    employee.get('facebook', ''),
                    employee.get('instagram', ''),
                    employee.get('query', '')
                ])

def read_companies(input_file):
    """Read company information from CSV file"""
    # Check if file is in output or output/company directory
    input_path = os.path.join(OUTPUT_DIR, input_file)
    if not os.path.exists(input_path):
        company_input_path = os.path.join(OUTPUT_DIR, "company", input_file)
        if os.path.exists(company_input_path):
            input_path = company_input_path
    
    companies = []
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                companies.append(row)
        logger.info(f"Read {len(companies)} companies from {input_path}")
        return companies
    except FileNotFoundError:
        logger.error(f"Input file not found: {input_path}")
        return []
    except Exception as e:
        logger.error(f"Error reading company file: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description="Employee search using Serper API")
    
    # Add two mutually exclusive modes
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--company', help='Company name to search for employees')
    mode_group.add_argument('--input-file', help='CSV file with company information (in output directory)')
    
    parser.add_argument('--position', required=True, help='Job position/title to search for')
    parser.add_argument('--country', help='Country keyword for search')
    parser.add_argument('--location', help='Location/city keyword for search')
    parser.add_argument('--keywords', help='Additional keywords, comma separated')
    parser.add_argument('--output', help='Output filename (will be saved in output/employee directory)')
    parser.add_argument('--gl', help='Geolocation parameter (e.g. "us", "fr", "de", "cn")', default='us')
    parser.add_argument('--num', type=int, help='Number of search results to return', default=30)
    
    args = parser.parse_args()
    
    logger.info("Serper Employee Search Tool")
    logger.info("--------------------------")
    
    # Process keywords if provided
    additional_keywords = None
    if args.keywords:
        additional_keywords = [kw.strip() for kw in args.keywords.split(',')]
    
    # Generate output filename with parameters and timestamp
    timestamp = int(time.time())
    
    # Set output file
    output_file = args.output
    if not output_file and args.company:
        # Generate output file name based on company, position, and timestamp
        company_str = args.company.lower().replace(' ', '_')
        position_str = args.position.lower().replace(' ', '_')
        gl_str = args.gl.lower()
        location_str = args.location.lower().replace(' ', '_') if args.location else 'no_location'
        country_str = args.country.lower().replace(' ', '_') if args.country else 'no_country'
        
        output_file = f"{company_str}_{position_str}_{location_str}_{country_str}_{gl_str}_{timestamp}.csv"
    elif not output_file:
        # Generic name for multi-company search
        position_str = args.position.lower().replace(' ', '_')
        gl_str = args.gl.lower()
        output_file = f"multi_company_{position_str}_{gl_str}_{timestamp}.csv"
    
    # Single company mode
    if args.company:
        logger.info(f"Searching for {args.position} at {args.company}")
        if args.location:
            logger.info(f"Location: {args.location}")
        if args.country:
            logger.info(f"Country: {args.country}")
        if args.keywords:
            logger.info(f"Additional keywords: {args.keywords}")
        logger.info(f"Google location: {args.gl}")
        logger.info(f"Number of results: {args.num}")
        logger.info("--------------------------")
        
        searcher = SerperEmployeeSearch(
            output_file=output_file,
            gl=args.gl,
            num_results=args.num
        )
        
        employees = searcher.search_employees(
            company_name=args.company,
            position=args.position,
            location=args.location,
            country=args.country,
            additional_keywords=additional_keywords
        )
        
        if employees:
            logger.info(f"\nSearch complete! Found {len(employees)} employees.")
            logger.info(f"Results saved to {searcher.output_file} and {searcher.output_file.replace('.csv', '.json')}")
    
    # Multi-company mode
    else:
        companies = read_companies(args.input_file)
        if not companies:
            return
        
        all_employees = []
        
        # Create a searcher without specifying output file yet
        searcher = SerperEmployeeSearch(
            gl=args.gl,
            num_results=args.num
        )
        
        for i, company in enumerate(companies):
            company_name = company.get('Company Name', '')
            if not company_name:
                logger.warning(f"Skipping company at index {i} - missing name")
                continue
                
            logger.info(f"\nProcessing company {i+1}/{len(companies)}: {company_name}")
            
            # Generate company-specific output file
            timestamp = int(time.time())
            company_str = company_name.lower().replace(' ', '_')
            position_str = args.position.lower().replace(' ', '_')
            gl_str = args.gl.lower()
            
            # Get company location if available in CSV
            company_location = company.get('Location', args.location)
            location_str = company_location.lower().replace(' ', '_') if company_location else 'no_location'
            
            company_output = f"{company_str}_{position_str}_{location_str}_{gl_str}_{timestamp}.csv"
            company_output_path = os.path.join(EMPLOYEE_OUTPUT_DIR, company_output)
            searcher.output_file = company_output_path
            searcher._initialize_csv()
            
            employees = searcher.search_employees(
                company_name=company_name,
                position=args.position,
                location=company_location,
                country=args.country,
                additional_keywords=additional_keywords
            )
            
            all_employees.extend(employees)
            
            # Add delay between companies to avoid rate limiting
            if i < len(companies) - 1:
                delay = random.uniform(10, 20)
                logger.info(f"Waiting {delay:.1f} seconds before the next company...")
                time.sleep(delay)
        
        # Save all results to a combined file
        combined_output = os.path.join(EMPLOYEE_OUTPUT_DIR, output_file)
        with open(combined_output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Name', 'Title', 'Company', 'LinkedIn URL', 'Description', 'Email', 
                'Phone', 'Twitter', 'Facebook', 'Instagram', 'Search Query'
            ])
            
            for employee in all_employees:
                writer.writerow([
                    employee.get('name', ''),
                    employee.get('title', ''),
                    employee.get('company', ''),
                    employee.get('url', ''),
                    employee.get('description', ''),
                    employee.get('email', ''),
                    employee.get('phone', ''),
                    employee.get('twitter', ''),
                    employee.get('facebook', ''),
                    employee.get('instagram', ''),
                    employee.get('query', '')
                ])
        
        # Save combined results as JSON
        json_output = combined_output.replace('.csv', '.json')
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(all_employees, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\nSearch complete! Found {len(all_employees)} employees across {len(companies)} companies")
        logger.info(f"Combined results saved to {combined_output} and {json_output}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nProgram interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True) 