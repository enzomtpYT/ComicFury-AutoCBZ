import argparse, sys, json
from index import ComicScraper

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description="Comic web scraper CLI")
    parser.add_argument("-u", "--url", required=False, help="URL of the webpage to scrape")
    parser.add_argument("-i", "--id", required=False, help="Id of the comic to scrape")
    parser.add_argument("-t", "--max-threads", type=int, default=4, help="Maximum number of threads to use (default: 4)")
    parser.add_argument("-d", "--download", action="store_true", help="Download the comic and create CBZ files")
    parser.add_argument("-o", "--output", required=False, help="Output directory for downloaded files")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    
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
    
    # Create a scraper instance with specified max threads and verbose setting
    scraper = ComicScraper(url, max_threads=args.max_threads, download_dir=args.output, verbose=args.verbose, id=args.id)
    chapters = scraper.scrapeChapters()
    
    # Write chapters to a json file with indentation only if not downloading
    if not args.download:
        with open('chapters.json', 'w') as f:
            json.dump(chapters, f, indent=4)
        print("Chapter information saved to chapters.json")
    
    # If download flag is set, download all chapters and create CBZ files
    if args.download:
        print("Download flag detected. Downloading chapters and creating CBZ files...")
        scraper.download_chapters(chapters)
        print(f"All chapters have been downloaded to the '{scraper.download_dir}' directory.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())