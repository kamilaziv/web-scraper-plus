
import requests
import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger("WebsiteScanner.Checker")

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
            
        # Try both https and http if necessary
        error_message = None
        for scheme in ['https://', 'http://']:
            # Skip if URL already has this scheme
            if url.startswith(scheme):
                formatted_url = url
            elif url.startswith(('http://', 'https://')):
                # If URL already has a different scheme, skip to next iteration
                continue
            else:
                formatted_url = scheme + url
                
            try:
                logger.info(f"Trying to connect to {formatted_url}")
                response = self.session.get(formatted_url, timeout=self.timeout, allow_redirects=True)
                
                # Check if the site has content
                has_content = len(response.text) > 100  # Simple heuristic to check for content
                
                # Classify 404 or empty content as not working
                if response.status_code == 404 or not has_content:
                    error_message = f"Error {response.status_code}" if response.status_code == 404 else "No content found"
                    logger.warning(f"{formatted_url}: {error_message}")
                    continue
                
                # Otherwise, consider it working
                logger.info(f"Successfully connected to {formatted_url}")
                return True, response
                
            except requests.RequestException as e:
                error_message = str(e)
                logger.warning(f"Failed to connect to {formatted_url}: {error_message}")
                continue
                
        # If we've tried both schemes and neither worked, return the last error
        return False, error_message or "Unable to connect"
