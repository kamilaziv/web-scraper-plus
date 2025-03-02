import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { LucideCheck, LucideCode, LucideDownload, LucideFileCog, LucideGlobe, LucideInfo, LucidePlay } from "lucide-react";
import { toast } from "sonner";

const Index = () => {
  const [activeTab, setActiveTab] = useState("code");
  
  const handleDownload = () => {
    const link = document.createElement("a");
    link.href = "/website_scanner.py";
    link.download = "website_scanner.py";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    toast.success("Download started", {
      description: "The Python script is being downloaded to your device."
    });
  };
  
  const pythonCode = `
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
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        return list(set(emails))  # Remove duplicates
        
    def extract_phones(self, text):
        """Extract phone numbers using various patterns"""
        # Multiple phone patterns to catch different formats
        patterns = [
            r'\\+[0-9]{1,3}[\\s.-][0-9]{3}[\\s.-][0-9]{3}[\\s.-][0-9]{4}',
            r'\\+[0-9]{1,3}[\\s.-][0-9]{3}[\\s.-][0-9]{4}',
            r'\\([0-9]{3}\\)[\\s.-][0-9]{3}[\\s.-][0-9]{4}',
            r'[0-9]{3}[\\s.-][0-9]{3}[\\s.-][0-9]{4}',
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
                r'linkedin\\.com\\/company\\/[a-zA-Z0-9._-]+',
                r'linkedin\\.com\\/in\\/[a-zA-Z0-9._-]+'
            ]
        elif platform == 'instagram':
            patterns = [
                r'instagram\\.com\\/[a-zA-Z0-9._-]+',
                r'instagr\\.am\\/[a-zA-Z0-9._-]+'
            ]
        elif platform == 'whatsapp':
            patterns = [
                r'wa\\.me\\/[0-9]+',
                r'api\\.whatsapp\\.com\\/send\\?phone=[0-9]+',
                r'web\\.whatsapp\\.com\\/send\\?phone=[0-9]+'
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
            'instagram': [],
            'whatsapp': []
        }
        
        visited_urls = set()
        urls_to_visit = [url]
        
        try:
            domain = urlparse(url).netloc
            
            for _ in range(min(len(urls_to_visit), self.max_pages)):
                if not urls_to_visit:
                    break
                    
                current_url = urls_to_visit.pop(0)
                if current_url in visited_urls:
                    continue
                    
                visited_urls.add(current_url)
                
                try:
                    response = self.session.get(current_url, timeout=self.timeout)
                    if response.status_code >= 400:
                        continue
                        
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract emails from the page text
                    emails = self.extract_emails(response.text)
                    results['email'].extend(emails)
                    
                    # Extract phone numbers from the page text
                    phones = self.extract_phones(response.text)
                    results['phone'].extend(phones)
                    
                    # Extract LinkedIn and Instagram links
                    linkedin_links = self.extract_social_links(soup, current_url, 'linkedin')
                    results['linkedin'].extend(linkedin_links)
                    
                    instagram_links = self.extract_social_links(soup, current_url, 'instagram')
                    results['instagram'].extend(instagram_links)
                    
                    # Extract WhatsApp links
                    whatsapp_links = self.extract_social_links(soup, current_url, 'whatsapp')
                    results['whatsapp'].extend(whatsapp_links)
                    
                    # Find more internal links to visit
                    if len(visited_urls) < self.max_pages:
                        for a_tag in soup.find_all('a', href=True):
                            href = a_tag['href']
                            full_url = urljoin(current_url, href)
                            
                            # Only follow links within the same domain
                            if urlparse(full_url).netloc == domain and full_url not in visited_urls:
                                urls_to_visit.append(full_url)
                                
                except Exception as e:
                    logger.warning(f"Error scraping {current_url}: {str(e)}")
                    continue
                    
            # Remove duplicates and return results
            for key in results:
                results[key] = list(set(results[key]))
                
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
        self.url_column = None
        
    def find_url_column(self, fieldnames):
        """Find the column containing website URLs"""
        possible_names = ['website url', 'website_url', 'websiteurl', 'url', 'website', 'domain', 'site']
        
        # First try exact match
        for name in fieldnames:
            if name.lower() in possible_names:
                return name
                
        # Try partial match
        for name in fieldnames:
            for possible in possible_names:
                if possible in name.lower():
                    return name
                    
        # Return the first column as fallback
        if fieldnames:
            return fieldnames[0]
            
        return None
        
    def process_row(self, row):
        """Process a single row from the CSV"""
        try:
            # Get URL from the identified URL column
            url = row.get(self.url_column, '').strip() if self.url_column else ''
            
            if not url:
                row['Status'] = 'No URL provided'
                row['Error'] = 'Missing URL in input'
                return row
                
            # Check if website is accessible
            is_accessible, response = self.website_checker.check_website(url)
            
            if not is_accessible:
                row['Status'] = 'Not working'
                row['Error'] = str(response)
                return row
                
            # Website is accessible, scrape for information
            row['Status'] = 'Working'
            
            # Scrape website
            scrape_results = self.website_scraper.scrape_website(url)
            
            # Update row with scraped information
            row['Email'] = '; '.join(scrape_results['email']) if scrape_results['email'] else ''
            row['Phone'] = '; '.join(scrape_results['phone']) if scrape_results['phone'] else ''
            row['LinkedIn'] = '; '.join(scrape_results['linkedin']) if scrape_results['linkedin'] else ''
            row['Instagram'] = '; '.join(scrape_results['instagram']) if scrape_results['instagram'] else ''
            row['WhatsApp'] = '; '.join(scrape_results['whatsapp']) if scrape_results['whatsapp'] else ''
            
            return row
            
        except Exception as e:
            logger.error(f"Error processing row: {str(e)}")
            row['Status'] = 'Error'
            row['Error'] = str(e)
            return row
            
    def process_csv(self):
        """Process the entire CSV file"""
        try:
            # Read the input CSV file
            with open(self.input_file, 'r', newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                
                # Identify the URL column
                self.url_column = self.find_url_column(fieldnames)
                
                # Add required columns to output
                output_fields = fieldnames + ['Status', 'Error', 'Email', 'Phone', 'LinkedIn', 'Instagram', 'WhatsApp']
                
                # Read all rows
                rows = list(reader)
                
            logger.info(f"Processing {len(rows)} rows from {self.input_file}")
            logger.info(f"URL column identified as: {self.url_column}")
            
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
                        logger.error(f"Error in thread: {str(e)}")
                        
            # Write the output CSV file
            with open(self.output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=output_fields)
                writer.writeheader()
                writer.writerows(processed_rows)
                
            logger.info(f"CSV processing complete. Results saved to {self.output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing CSV: {str(e)}")
            return False

def main():
    import argparse
    
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
  `;

  const instructionsText = `
## Website Scanner for CSV Files

This Python script scans websites listed in a CSV file, checks if they're working, and extracts contact information.

### Features:
- Website status checking (working/not working)
- Extracts emails, phone numbers, LinkedIn links, Instagram links, and WhatsApp links
- Processes large CSV files efficiently using multithreading
- Detailed logging for troubleshooting

### Requirements:
\`\`\`
pip install requests beautifulsoup4 tqdm
\`\`\`

### How to Use:
1. Save the script as \`website_scanner.py\`
2. Prepare your CSV file with at least a "Website URL" column
3. Run the script:
   \`\`\`
   python website_scanner.py input.csv -o output.csv -w 10 -p 5
   \`\`\`

### Parameters:
- \`input.csv\`: Your input CSV file path
- \`-o, --output\`: Output CSV file path (default: processed_input.csv)
- \`-w, --workers\`: Number of worker threads (default: 5)
- \`-p, --pages\`: Maximum pages to scan per website (default: 5)

### Example:
\`\`\`
python website_scanner.py websites.csv --output results.csv --workers 20 --pages 10
\`\`\`

### Output:
The script adds the following columns to your CSV:
- Status: "Working" or "Not working"
- Error: Error message if website couldn't be accessed
- Email: Extracted email addresses
- Phone: Extracted phone numbers
- LinkedIn: LinkedIn profile links
- Instagram: Instagram profile links
- WhatsApp: WhatsApp contact links
  `;

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-4 sm:p-6 md:p-10 animate-in fade-in duration-700">
      <Card className="mx-auto max-w-4xl shadow-lg border border-gray-200 dark:border-gray-800 backdrop-blur-sm bg-white/90 dark:bg-black/80">
        <CardHeader className="px-6 pt-8 pb-4">
          <CardTitle className="text-2xl md:text-3xl font-light tracking-tight text-center">Website Scanner Tool</CardTitle>
          <CardDescription className="text-center text-gray-500 dark:text-gray-400 mt-2">
            A Python utility for scanning websites and extracting contact information from CSV data
          </CardDescription>
        </CardHeader>
        
        <Tabs defaultValue="code" className="w-full" onValueChange={setActiveTab}>
          <div className="px-6">
            <TabsList className="grid w-full grid-cols-2 mb-6">
              <TabsTrigger value="code" className="flex items-center gap-2">
                <LucideCode className="h-4 w-4" />
                <span>Python Script</span>
              </TabsTrigger>
              <TabsTrigger value="instructions" className="flex items-center gap-2">
                <LucideInfo className="h-4 w-4" />
                <span>Instructions</span>
              </TabsTrigger>
            </TabsList>
          </div>
          
          <CardContent className="px-6 pb-2">
            <TabsContent value="code" className="mt-0">
              <div className="relative">
                <pre className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-md p-4 overflow-x-auto text-sm font-mono text-gray-800 dark:text-gray-200 h-[600px] overflow-y-auto">
                  <code>{pythonCode}</code>
                </pre>
                <Button 
                  variant="secondary"
                  className="absolute top-4 right-4 bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 z-10"
                  size="sm"
                  onClick={() => {
                    navigator.clipboard.writeText(pythonCode);
                    toast.success("Code copied to clipboard");
                  }}
                >
                  Copy Code
                </Button>
              </div>
            </TabsContent>
            
            <TabsContent value="instructions" className="mt-0">
              <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-md p-6 h-[600px] overflow-y-auto">
                <div className="prose dark:prose-invert max-w-none">
                  <div dangerouslySetInnerHTML={{ __html: instructionsText.replace(/\n/g, '<br/>') }} />
                </div>
              </div>
            </TabsContent>
          </CardContent>
          
          <div className="px-6 py-4">
            <Separator className="mb-4" />
            <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <LucideFileCog className="h-4 w-4" />
                <span>website_scanner.py</span>
              </div>
              
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  size="sm"
                  className="gap-1 transition-all duration-300"
                  onClick={handleDownload}
                >
                  <LucideDownload className="h-4 w-4 mr-1" />
                  Download Script
                </Button>
                
                <Button 
                  variant="default" 
                  size="sm"
                  className="gap-1 bg-green-600 hover:bg-green-700 text-white"
                  onClick={() => {
                    toast.info("To run the script", {
                      description: "Save the Python script and run with: python website_scanner.py input.csv"
                    });
                  }}
                >
                  <LucidePlay className="h-4 w-4 mr-1" />
                  How to Run
                </Button>
              </div>
            </div>
          </div>
        </Tabs>
      </Card>
      
      <div className="mt-8 max-w-4xl mx-auto">
        <Card className="border border-gray-200 dark:border-gray-800 shadow-md bg-white/90 dark:bg-black/80 backdrop-blur-sm transition-all duration-300 hover:shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-xl font-medium flex items-center gap-2">
              <LucideCheck className="h-5 w-5 text-green-500" />
              Features
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-start gap-3">
                <div className="bg-gray-100 dark:bg-gray-800 rounded-full p-2 mt-1">
                  <LucideGlobe className="h-4 w-4 text-blue-500" />
                </div>
                <div>
                  <h3 className="font-medium">Website Status Checking</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Identifies working and non-working websites</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="bg-gray-100 dark:bg-gray-800 rounded-full p-2 mt-1">
                  <LucidePlay className="h-4 w-4 text-purple-500" />
                </div>
                <div>
                  <h3 className="font-medium">Multithreaded Processing</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Handles 100,000+ rows efficiently</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="bg-gray-100 dark:bg-gray-800 rounded-full p-2 mt-1">
                  <LucideInfo className="h-4 w-4 text-amber-500" />
                </div>
                <div>
                  <h3 className="font-medium">Contact Data Extraction</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Finds emails, phones, and social media</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="bg-gray-100 dark:bg-gray-800 rounded-full p-2 mt-1">
                  <LucideFileCog className="h-4 w-4 text-teal-500" />
                </div>
                <div>
                  <h3 className="font-medium">CSV Integration</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Seamlessly updates your existing CSV files</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Index;
