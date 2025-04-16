import argparse, sys, json, os
from index import ComicScraper

def main():
    print("Comic Scraper CLI V1.0.1 by enzomtpYT\n\n")
    
    # Create argument parser
    parser = argparse.ArgumentParser(description="Comic web scraper CLI")
    parser.add_argument("-u", "--url", required=False, help="URL of the webpage to scrape")
    parser.add_argument("-i", "--id", required=False, help="Id of the comic to scrape")
    parser.add_argument("-t", "--max-threads", type=int, default=4, help="Maximum number of threads to use (default: 4)")
    parser.add_argument("-d", "--download", action="store_true", help="Download the comic and create CBZ files")
    parser.add_argument("-o", "--output", required=False, help="Output directory for downloaded files")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-j", "--json", required=False, help="Path to a JSON file with chapter data (skips scraping)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Default values
    url = None
    id = None
    
    # If a specific JSON file is provided, extract comic ID from it if possible
    if args.json and os.path.exists(args.json):
        print(f"Using provided JSON file: {args.json}")
        try:
            with open(args.json, 'r') as f:
                chapters = json.load(f)
            
            # Try to extract comic ID from the first chapter's URL if available
            if chapters and isinstance(chapters, list) and len(chapters) > 0:
                # Look for a URL in the first chapter
                if 'url' in chapters[0] and '/read/' in chapters[0]['url']:
                    comic_url = chapters[0]['url']
                    id = comic_url.split('/read/')[1].split('/')[0]
                    url = f"https://comicfury.com/read/{id}/archive"
                    print(f"Extracted comic ID from JSON: {id}")
                
                # If we have pages in the first chapter, try to get ID from there
                elif 'pages' in chapters[0] and chapters[0]['pages'] and 'page_url' in chapters[0]['pages'][0]:
                    page_url = chapters[0]['pages'][0]['page_url']
                    if '/read/' in page_url:
                        id = page_url.split('/read/')[1].split('/')[0]
                        url = f"https://comicfury.com/read/{id}/archive"
                        print(f"Extracted comic ID from JSON page: {id}")
            
            print(f"Loaded {len(chapters)} chapters from {args.json}")
        except Exception as e:
            print(f"Error loading JSON file: {str(e)}")
            sys.exit(1)
    
    # If no JSON file or we need URL/ID for other purposes
    elif args.url is None and args.id is None:
        parser.print_help()
        sys.exit(1)
    elif args.url is None and args.id is not None:
        # If no URL or JSON is provided, use the ID to construct the URL
        id = args.id
        url = f"https://comicfury.com/read/{id}/archive"
    elif args.url is not None:
        # If URL is provided extract id and use url
        if "/archive" in args.url:
            id = args.url.split("/")[-2]
            url = args.url
        elif "comicprofile.php" in args.url:
            id = args.url.split("url=")[-1]
            url = f"https://comicfury.com/read/{id}/archive"
        else:
            parser.print_help()
            sys.exit(1)
    
    # Create a scraper instance with specified max threads and verbose setting
    scraper = ComicScraper(url, max_threads=args.max_threads, download_dir=args.output, verbose=args.verbose, id=id)
    
    # If a specific JSON file is provided, use that instead of scraping or looking for default JSON
    if args.json and os.path.exists(args.json):
        try:
            with open(args.json, 'r') as f:
                chapters = json.load(f)
            print(f"Using chapters from {args.json}")
        except Exception as e:
            print(f"Error loading JSON file: {str(e)}")
            sys.exit(1)
    else:
        # Otherwise try to load from default location or scrape
        chapters = scraper.scrapeChapters()
    
    # Write chapters to a json file with indentation only if not downloading and not using existing JSON
    if not args.download and args.json is None:
        json_path = f'{id}-chapters.json' if id else "chapters.json"
        with open(json_path, 'w') as f:
            json.dump(chapters, f, indent=4)
        print(f"Chapter information saved to {json_path}")
    
    # If download flag is set, download all chapters and create CBZ files
    if args.download:
        print("Download flag detected. Downloading chapters and creating CBZ files...")
        scraper.download_chapters(chapters)
        print(f"All chapters have been downloaded to the '{scraper.download_dir}' directory.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())