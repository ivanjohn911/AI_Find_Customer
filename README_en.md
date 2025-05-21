# AI Business and Contact Intelligence Search Tool

[中文版本](README.md)

A powerful set of Python tools for automating the customer development process in international trade and B2B sales. This tool uses search engine APIs and AI technology to help you quickly find target companies, extract contact information, and identify key decision-makers.

## Project Features

This project contains three main scripts, each addressing different stages of the sales process:

1. **Company Search** (`serper_company_search.py`)
   - Search for target companies based on industry, region, and keywords
   - Support custom search queries with full control over search content
   - Automatically extract company websites, domains, and basic information
   - Support for both general search and LinkedIn company-specific search

2. **Contact Information Extraction** (`extract_contact_info.py`)
   - Automatically extract contact information from company websites
   - Identify email addresses, phone numbers, and physical addresses
   - Collect social media accounts (LinkedIn, Twitter, Facebook, Instagram)
   - Support for batch processing of multiple URLs while optimizing browser resources
   - Option to merge results with input CSV files for data integration

3. **Employee and Decision-Maker Search** (`serper_employee_search.py`)
   - Search for employees of target companies based on company name and position
   - Identify key decision-makers and potential contacts
   - Extract information from employee LinkedIn profiles

## Problems Solved

- **Reduce Customer Development Costs**: Decrease manual search and data collection time, improve sales team efficiency
- **Increase Customer Accuracy**: Precisely target companies that match industry and regional criteria
- **Simplify Contact Process**: Directly obtain effective contact information without switching between multiple platforms
- **Identify Key Decision-Makers**: Directly find key personnel in companies, shortening the sales cycle

## Technical Implementation

- **Search Technology**: Uses Serper.dev API for efficient search engine queries
- **Web Content Extraction**: Uses Playwright for automated browser rendering and website content extraction
- **AI Content Analysis**: Analyzes web content through various LLM models (OpenAI, Volcano Engine, Anthropic, Google) to extract structured information
- **Parallel Processing**: Optimizes browser instance management for efficient batch processing
- **Fault Tolerance**: Includes timeout handling, content cleaning, and error recovery features

## Installation Guide

### Prerequisites

- Python 3.8+
- Serper.dev API key ([Apply for free key](https://serper.dev/))
- (Optional) LLM API key (Volcano Engine API recommended for users in China)

### Installation Steps

1. Clone or download the project files

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browser (for website content extraction):
```bash
playwright install chromium
```

4. Create `.env` configuration file (in the project root directory):
```
# Required: Serper API key
SERPER_API_KEY=your_serper_api_key_here

# LLM Configuration (choose one)
LLM_PROVIDER=huoshan  # Options: openai, anthropic, google, huoshan, none

# Volcano Engine Configuration (recommended for users in China)
ARK_API_KEY=your_ark_api_key_here
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ARK_MODEL=doubao-1-5-pro-256k-250115

# Or use other LLM services
# OPENAI_API_KEY=your_openai_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
# GOOGLE_API_KEY=your_google_api_key_here

# Website extraction configuration
HEADLESS=true
TIMEOUT=15000
VISIT_CONTACT_PAGE=false
```

## Usage Guide

### 1. Company Search

Use the `serper_company_search.py` script to search for company information:

#### Search companies based on industry and region:
```bash
python serper_company_search.py --general-search --industry "solar energy" --region "California" --gl "us"
```

#### Use custom queries (full control over query content):
```bash
python serper_company_search.py --general-search --custom-query "top solar panel manufacturers California renewable energy" --gl "us"
```

#### Parameter Description:
- `--general-search`: Use general search mode
- `--linkedin-search`: Use LinkedIn company-specific search mode
- `--industry`: Target industry keywords
- `--region`: Target region/city
- `--custom-query`: Fully customized search query (overrides industry, region, and default keywords)
- `--gl`: Region code (e.g., "us", "uk", "cn", etc.)
- `--num`: Number of results to return (default 30)
- `--keywords`: Additional keywords (comma-separated)
- `--output`: Custom output filename

#### Results:
Results will be saved in the `output/company/` directory in CSV and JSON formats. Filenames are automatically generated based on search parameters.

### 2. Contact Information Extraction

Use the `extract_contact_info.py` script to extract contact information from websites:

#### Process a single website:
```bash
python extract_contact_info.py --url example.com --headless
```

#### Process multiple websites (from a text file):
```bash
python extract_contact_info.py --url-list urls.txt --timeout 15000
```

#### Process company search results:
```bash
python extract_contact_info.py --csv output/company/general_solar_energy_california_us_1234567890.csv --url-column Domain
```

#### Process CSV and merge results:
```bash
python extract_contact_info.py --csv companies.csv --url-column Domain --merge-results
```

#### Parameter Description:
- `--url`: Single website URL
- `--url-list`: Text file containing multiple URLs (one per line)
- `--csv`: CSV file containing a URL column
- `--url-column`: Name of the URL column in the CSV file (default "URL")
- `--domain-column`: Alternative domain column name (default "Domain")
- `--output`: Custom output filename
- `--headless`: Run browser in headless mode (no UI)
- `--timeout`: Page load timeout in milliseconds
- `--visit-contact`: Enable contact page visit (more comprehensive but slower)
- `--merge-results`: Merge extracted contact information with the input CSV (only applicable with the `--csv` option)

#### Results:
- Basic contact information results are saved in the `output/contact/` directory, including:
  - Company name
  - Email addresses
  - Phone numbers
  - Physical addresses
  - Social media links (LinkedIn, Twitter, Facebook, Instagram)
  
- When using `--merge-results`, an additional `*_merged.csv` file is generated, containing the original CSV data plus the extracted contact information.

### 3. Employee Search

Use the `serper_employee_search.py` script to find company employees and decision-makers:

#### Search for employees of a specific company:
```bash
python serper_employee_search.py --company "Tesla" --position "sales manager" --location "California"
```

#### Parameter Description:
- `--company`: Target company name
- `--input-file`: CSV file containing company information (located in the output directory)
- `--position`: Target position/title
- `--location`: Location/city
- `--country`: Country
- `--keywords`: Additional keywords (comma-separated)
- `--output`: Custom output filename
- `--gl`: Region code (e.g., "us", "uk", etc.)
- `--num`: Number of results to return (default 30)

#### Results:
Results will be saved in the `output/employee/` directory, containing employee names, positions, LinkedIn links, and other available information.

## Advanced Usage Tips

### Complete Sales Process Automation:

1. Search for target companies using a custom query:
```bash
python serper_company_search.py --general-search --custom-query "renewable energy companies Texas usa" --gl "us" --output texas_renewable.csv
```

2. Extract and merge contact information from search results:
```bash
python extract_contact_info.py --csv output/company/texas_renewable.csv --url-column Domain  --headless --merge-results
```


## Notes and Limitations

- Serper.dev API has free usage limits; please control query frequency reasonably
- Some websites may block automated access; you may need to adjust request headers or use proxies
- Contact information extraction accuracy depends on website structure and content quality
- Please comply with relevant laws, regulations, and platform terms of use
- For large-scale batch processing, it's recommended to control concurrency and add sufficient delays

## Frequently Asked Questions

**Q: Unable to extract contact information from certain websites**  
A: Try using the `--visit-contact` parameter to enable contact page visiting, or adjust the `--timeout` parameter to increase loading time.

**Q: Browser windows frequently open and close**  
A: Add the `--headless` parameter to use headless mode for improved efficiency. When batch processing multiple URLs, the system automatically optimizes browser instance usage.

**Q: How to process contact information in CSV data**  
A: Use the `--merge-results` parameter to merge extracted contact information with the original CSV, generating a new file containing all data.

**Q: API key configuration issues**  
A: Ensure the API keys in the `.env` file are correctly formatted and do not contain quotes or extra spaces.

## Contact Information

<div style="display: flex; justify-content: space-between;">
  <div style="text-align: center; margin-right: 20px;">
    <h3>Personal WeChat</h3>
    <img src="img/me_code.jpg" width="200" alt="Personal WeChat QR Code">
  </div>
  <div style="text-align: center; margin-right: 20px;">
    <h3>WeChat Group</h3>
    <img src="img/group_code.jpg" width="200" alt="WeChat Group QR Code">
  </div>
  <div style="text-align: center;">
    <h3>Telegram Group</h3>
    <a href="https://t.me/+jjmdspjqpbcwOGFl">Join Telegram Group</a>
  </div>
</div>