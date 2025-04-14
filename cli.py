#!/usr/bin/env python3
import argparse
import sys
import json
from index import ComicScraper

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description="Comic web scraper CLI")
    parser.add_argument("-u", "--url", required=False, help="URL of the webpage to scrape")
    parser.add_argument("-i", "--id", required=False, help="Id of the comic to scrape")
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.url is None and args.id is None:
        parser.print_help()
        sys.exit(1)
    elif args.url is None:
        # If no URL is provided, use the ID to construct the URL
        url = f"https://comicfury.com/read/{args.id}/archive"
    else:
        url = args.url
    
    # Create a scraper instance
    scraper = ComicScraper(url)
    chapters = scraper.scrapeChapters()
    
    # Write chapters to a json file with indentation
    with open('chapters.json', 'w') as f:
        json.dump(chapters, f, indent=4)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())