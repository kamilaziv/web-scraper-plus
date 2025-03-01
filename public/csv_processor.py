
import os
import csv
import logging
import concurrent.futures
from tqdm import tqdm
from website_checker import WebsiteChecker
from website_scraper import WebsiteScraper

logger = logging.getLogger("WebsiteScanner.CSVProcessor")

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
                row['Status'] = 'Not Working'
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
                row['Status'] = 'Not Working'
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
            
            # Get the actual working URL (that may include http or https)
            working_url = response.url
            
            # Scrape website
            scrape_results = self.website_scraper.scrape_website(working_url)
            
            # Update row with scraped information
            row['Email'] = '; '.join(scrape_results['email']) if scrape_results['email'] else ''
            row['Phone'] = '; '.join(scrape_results['phone']) if scrape_results['phone'] else ''
            row['LinkedIn'] = '; '.join(scrape_results['linkedin']) if scrape_results['linkedin'] else ''
            row['Instagram'] = '; '.join(scrape_results['instagram']) if scrape_results['instagram'] else ''
            
            logger.info(f"Processed {url}: Email={row['Email']}, Phone={row['Phone']}, LinkedIn={row['LinkedIn']}, Instagram={row['Instagram']}")
            
            return row
            
        except Exception as e:
            logger.error(f"Error processing row: {str(e)}", exc_info=True)
            row['Status'] = 'Not Working'
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
