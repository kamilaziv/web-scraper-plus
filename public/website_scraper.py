
import re
import logging
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

logger = logging.getLogger("WebsiteScanner.Scraper")

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
