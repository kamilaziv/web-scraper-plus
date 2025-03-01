
import csv
import requests
import re
import logging
import os
import time
import concurrent.futures
import argparse
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("website_scanner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WebsiteScanner")

class WebsiteChecker:
    def __init__(self, timeout=30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def check_website(self, url):
        """Check if website is accessible"""
        if not url or not isinstance(url, str):
            return False, "Invalid URL"
            
        # Ensure URL has a scheme
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            if response.status_code >= 400:
                return False, f"Error {response.status_code}"
            return True, response
        except requests.RequestException as e:
            return False, str(e)

class WebsiteScraper:
    def __init__(self, max_pages=5, timeout=30):
        self.max_pages = max_pages
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def extract_emails(self, text):
        """Extract emails from text using regex"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        return list(set(emails))  # Remove duplicates
        
    def extract_phones(self, text):
        """Extract phone numbers using various patterns"""
        # Multiple phone patterns to catch different formats
        patterns = [
            r'\+[0-9]{1,3}[\s.-][0-9]{3}[\s.-][0-9]{3}[\s.-][0-9]{4}',
            r'\+[0-9]{1,3}[\s.-][0-9]{3}[\s.-][0-9]{4}',
            r'\([0-9]{3}\)[\s.-][0-9]{3}[\s.-][0-9]{4}',
            r'[0-9]{3}[\s.-][0-9]{3}[\s.-][0-9]{4}',
            r'[0-9]{10,12}'
        ]
        
        phones = []
        for pattern in patterns:
            found = re.findall(pattern, text)
            phones.extend(found)
            
        return list(set(phones))  # Remove duplicates
        
    def extract_social_links(self, soup, base_url, platform):
        """Extract social media links based on platform"""
        links = []
        
        if platform == 'linkedin':
            patterns = [
                r'linkedin\.com\/company\/[a-zA-Z0-9._-]+',
                r'linkedin\.com\/in\/[a-zA-Z0-9._-]+'
            ]
        elif platform == 'instagram':
            patterns = [
                r'instagram\.com\/[a-zA-Z0-9._-]+',
                r'instagr\.am\/[a-zA-Z0-9._-]+'
            ]
        else:
            return []
            
        # Check all links on the page
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            
            for pattern in patterns:
                if re.search(pattern, full_url, re.IGNORECASE):
                    links.append(full_url)
                    
        return list(set(links))  # Remove duplicates
        
    def scrape_website(self, url):
        """Scrape website for contact information"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        results = {
            'email': [],
            'phone': [],
            'linkedin': [],
            'instagram': []
        }
        
        visited_urls = set()
        urls_to_visit = [url]
        
        logger.info(f"Starting to scrape {url}")
        
        try:
            domain = urlparse(url).netloc
            
            for _ in range(min(len(urls_to_visit), self.max_pages)):
                if not urls_to_visit:
                    break
                    
                current_url = urls_to_visit.pop(0)
                if current_url in visited_urls:
                    continue
                    
                visited_urls.add(current_url)
                
                logger.info(f"Visiting {current_url}")
                
                try:
                    response = self.session.get(current_url, timeout=self.timeout)
                    if response.status_code >= 400:
                        logger.warning(f"Error {response.status_code} for {current_url}")
                        continue
                        
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract emails from the page text
                    emails = self.extract_emails(response.text)
                    if emails:
                        logger.info(f"Found emails: {emails}")
                    results['email'].extend(emails)
                    
                    # Extract phone numbers from the page text
                    phones = self.extract_phones(response.text)
                    if phones:
                        logger.info(f"Found phones: {phones}")
                    results['phone'].extend(phones)
                    
                    # Extract LinkedIn and Instagram links
                    linkedin_links = self.extract_social_links(soup, current_url, 'linkedin')
                    if linkedin_links:
                        logger.info(f"Found LinkedIn: {linkedin_links}")
                    results['linkedin'].extend(linkedin_links)
                    
                    instagram_links = self.extract_social_links(soup, current_url, 'instagram')
                    if instagram_links:
                        logger.info(f"Found Instagram: {instagram_links}")
                    results['instagram'].extend(instagram_links)
                    
                    # Find more internal links to visit
                    if len(visited_urls) < self.max_pages:
                        for a_tag in soup.find_all('a', href=True):
                            href = a_tag['href']
                            full_url = urljoin(current_url, href)
                            
                            # Only follow links within the same domain
                            if urlparse(full_url).netloc == domain and full_url not in visited_urls and full_url not in urls_to_visit:
                                urls_to_visit.append(full_url)
                                
                except Exception as e:
                    logger.warning(f"Error scraping {current_url}: {str(e)}")
                    continue
                    
            # Remove duplicates and return results
            for key in results:
                results[key] = list(set(results[key]))
                
            logger.info(f"Finished scraping {url}. Results: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error scraping website {url}: {str(e)}")
            return results

class CSVProcessor:
    def __init__(self, input_file, output_file=None, max_workers=5):
        self.input_file = input_file
        self.output_file = output_file or f"processed_{os.path.basename(input_file)}"
        self.max_workers = max_workers
        self.website_checker = WebsiteChecker()
        self.website_scraper = WebsiteScraper()
        
    def process_row(self, row):
        """Process a single row from the CSV"""
        try:
            # Check both "Website URL" and "website url" (case insensitive)
            url = None
            for key in row:
                if key and key.lower() == "website url":
                    url = row[key]
                    break
                    
            if not url:
                logger.warning(f"No URL found in row: {row}")
                row['Status'] = 'No URL provided'
                row['Error'] = 'Missing URL in input'
                row['Email'] = ''
                row['Phone'] = ''
                row['LinkedIn'] = ''
                row['Instagram'] = ''
                return row
                
            logger.info(f"Processing URL: {url}")
            
            # Check if website is accessible
            is_accessible, response = self.website_checker.check_website(url)
            
            if not is_accessible:
                logger.warning(f"Website not accessible: {url} - {response}")
                row['Status'] = 'Not working'
                row['Error'] = str(response)
                row['Email'] = ''
                row['Phone'] = ''
                row['LinkedIn'] = ''
                row['Instagram'] = ''
                return row
                
            # Website is accessible, scrape for information
            logger.info(f"Website accessible: {url}")
            row['Status'] = 'Working'
            row['Error'] = ''
            
            # Scrape website
            scrape_results = self.website_scraper.scrape_website(url)
            
            # Update row with scraped information
            row['Email'] = '; '.join(scrape_results['email']) if scrape_results['email'] else ''
            row['Phone'] = '; '.join(scrape_results['phone']) if scrape_results['phone'] else ''
            row['LinkedIn'] = '; '.join(scrape_results['linkedin']) if scrape_results['linkedin'] else ''
            row['Instagram'] = '; '.join(scrape_results['instagram']) if scrape_results['instagram'] else ''
            
            logger.info(f"Processed {url}: Email={row['Email']}, Phone={row['Phone']}, LinkedIn={row['LinkedIn']}, Instagram={row['Instagram']}")
            
            return row
            
        except Exception as e:
            logger.error(f"Error processing row: {str(e)}", exc_info=True)
            row['Status'] = 'Error'
            row['Error'] = str(e)
            row['Email'] = ''
            row['Phone'] = ''
            row['LinkedIn'] = ''
            row['Instagram'] = ''
            return row
            
    def process_csv(self):
        """Process the entire CSV file"""
        try:
            # Check if input file exists
            if not os.path.exists(self.input_file):
                logger.error(f"Input file {self.input_file} does not exist")
                return False
                
            # Read the input CSV file
            rows = []
            fieldnames = []
            try:
                with open(self.input_file, 'r', newline='', encoding='utf-8-sig') as csvfile:
                    reader = csv.DictReader(csvfile)
                    fieldnames = list(reader.fieldnames) if reader.fieldnames else []
                    
                    # Check if the file has any column headers
                    if not fieldnames:
                        logger.error(f"Input file {self.input_file} has no column headers")
                        return False
                        
                    # Check if required columns exist (case insensitive check)
                    has_url_column = False
                    for field in fieldnames:
                        if field and field.lower() == "website url":
                            has_url_column = True
                            break
                            
                    if not has_url_column:
                        logger.warning(f"Input file {self.input_file} doesn't have a 'Website URL' column. "
                                      f"Available columns: {fieldnames}")
                        
                    # Read all rows
                    rows = list(reader)
                    
                    # Check if the file has any rows
                    if not rows:
                        logger.error(f"Input file {self.input_file} is empty or has no data rows")
                        return False
                    
            except Exception as e:
                logger.error(f"Error reading CSV file {self.input_file}: {str(e)}", exc_info=True)
                return False
                
            # Add required output columns if they don't exist
            required_columns = ['Status', 'Error', 'Email', 'Phone', 'LinkedIn', 'Instagram']
            for col in required_columns:
                if col not in fieldnames:
                    fieldnames.append(col)
            
            logger.info(f"Processing {len(rows)} rows from {self.input_file}")
            logger.info(f"Columns: {fieldnames}")
            
            # Process rows with progress bar
            processed_rows = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all rows for processing
                future_to_row = {executor.submit(self.process_row, row): row for row in rows}
                
                # Process results as they complete with a progress bar
                for future in tqdm(concurrent.futures.as_completed(future_to_row), total=len(rows), desc="Processing websites"):
                    try:
                        processed_row = future.result()
                        processed_rows.append(processed_row)
                    except Exception as e:
                        logger.error(f"Error in thread: {str(e)}", exc_info=True)
                        
            # Write the output CSV file
            with open(self.output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(processed_rows)
                
            logger.info(f"CSV processing complete. Results saved to {self.output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing CSV: {str(e)}", exc_info=True)
            return False

def main():
    parser = argparse.ArgumentParser(description='Website scanner for CSV files')
    parser.add_argument('input_file', help='Input CSV file path')
    parser.add_argument('-o', '--output', help='Output CSV file path')
    parser.add_argument('-w', '--workers', type=int, default=5, help='Number of worker threads')
    parser.add_argument('-p', '--pages', type=int, default=5, help='Maximum pages to scan per website')
    
    args = parser.parse_args()
    
    # Create processor and start processing
    processor = CSVProcessor(
        input_file=args.input_file,
        output_file=args.output,
        max_workers=args.workers
    )
    
    # Set max pages for scraper
    processor.website_scraper.max_pages = args.pages
    
    # Process the CSV
    processor.process_csv()

if __name__ == "__main__":
    start_time = time.time()
    main()
    duration = time.time() - start_time
    logger.info(f"Script completed in {duration:.2f} seconds")
