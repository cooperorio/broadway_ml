import subprocess
import sys
import os
from datetime import datetime
from data_collection.upload_to_s3 import upload_to_s3

# Configuration
CSV_PATH = r"C:\Users\coope\OneDrive\Desktop\broadway_ml\database\broadway_league_data.csv"
BUCKET_NAME = "broadway-data-raw"  # Change to your bucket name
SCRAPER_PATH = "data_collection/scraper.py"

def run_scraper():
    """Execute the scraper script"""
    print("Starting Broadway data scrape...")
    start_time = datetime.now()
    
    result = subprocess.run(
        [sys.executable, SCRAPER_PATH],
        capture_output=True,
        text=True
    )
    
    # Print output
    print("\n" + "="*50)
    print("SCRAPER OUTPUT:")
    print(result.stdout)
    if result.stderr:
        print("ERRORS:")
        print(result.stderr)
    
    print("\n" + "="*50)
    print(f"Scraping completed in {datetime.now() - start_time}")
    return result.returncode == 0

def main():
    # Run scraper
    success = run_scraper()
    
    # Upload to S3 if successful
    if success and os.path.exists(CSV_PATH):
        print("\nUploading to S3...")
        if upload_to_s3(BUCKET_NAME, CSV_PATH):
            print("Hooray! Pipeline completed successfully!")
        else:
            print("Oof... S3 upload failed")
    else:
        print("Inner oof: Pipeline failed - no upload attempted")

if __name__ == "__main__":
    main()