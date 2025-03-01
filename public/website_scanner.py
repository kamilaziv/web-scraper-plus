
import logging
import time
import argparse
import os
import sys

# Add the current directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from csv_processor import CSVProcessor

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
