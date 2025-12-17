import requests, re, shutil, os, zipfile, json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

class ComicScraper:
    def __init__(self, url, max_threads=4, download_dir="downloads", verbose=False, id=None):
        self.url = url
        self.max_threads = max_threads
        self.download_dir = download_dir or f"{id}"
        self.verbose = verbose
        self.id = id
        self.json_path = f"{id}-chapters.json" if id else "chapters.json"
    
    def log(self, message):
        """
        Print message only if verbose is enabled
        """
        if self.verbose:
            print(message)
    
    def load_chapters_from_json(self):
        """
        Attempts to load chapters from a JSON file if it exists
        Returns the chapters if successful, None otherwise
        """
        if os.path.exists(self.json_path):
            try:
                print(f"Found existing chapters JSON file: {self.json_path}")
                with open(self.json_path, 'r') as f:
                    chapters = json.load(f)
                print(f"Loaded {len(chapters)} chapters from JSON file.")
                return chapters
            except Exception as e:
                print(f"Error loading chapters from JSON: {str(e)}")
                return None
        return None
    
    def scrapeChapters(self):
        """
        Scrapes the comic page and returns a list of chapters with their titles and URLs
        If a JSON file with chapters data exists, loads from there instead
        """
        # Try to load chapters from JSON first
        chapters = self.load_chapters_from_json()
        if chapters is not None:
            return chapters
            
        # If no JSON file or loading failed, scrape from website
        print(f"Scraping chapters from: {self.url}")
        
        # Send a GET request to the URL
        response = requests.get(self.url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all chapters links in the archive
            chapter_el = []
            for a_tag in soup.find_all('a'):
                if a_tag.find('div', class_='archive-chapter'):
                    chapter_el.append(a_tag)
            
            chapters = []
            # Extract chapters titles and URLs
            for element in chapter_el:
                title = element.text.strip()
                chapter_url = element['href']
                # Check if the URL is relative and prepend the base URL if necessary
                if chapter_url.startswith('/'):
                    chapter_url = 'https://comicfury.com' + chapter_url                
                # Append the chapter title and URL to the list
                chapters.append({"title": title, "url": chapter_url})
            
            print(f"Found {len(chapters)} chapters.")
            
            # Use ThreadPoolExecutor to scrape pages in parallel
            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                # Create a dictionary to store results with chapter index as key
                results = {}
                # Submit tasks to the executor
                for i, chapter in enumerate(chapters):
                    future = executor.submit(self.scrapePages, chapter['url'])
                    results[i] = future
                
                # Collect results as they complete
                for i, future in results.items():
                    chapters[i]['pages'] = future.result()
                
            return chapters
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return []
    
    def scrapePages(self, chapter_url, recursive = False):
        """
        Scrapes all pages from a chapter and returns a list of page URLs
        """
        self.log(f"Scraping pages from chapter: {chapter_url}")
        
        # Send a GET request to the chapter URL
        response = requests.get(chapter_url)
        pages = []
        # Collect extra pages separately so as not to mess up the order
        extra_pages = []
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            extra_vfpages = []
            # Also add pages that are hidden behind pagination
            if not recursive:
                for vfpage in soup.find_all('a', class_='vfpage'):
                    vfpage_url = vfpage['href']
                    if vfpage_url.startswith('/'):
                        vfpage_url = 'https://comicfury.com' + vfpage_url
                    # Pagination links appear twice (top and bottom); deduplicate
                    if vfpage_url not in extra_vfpages:
                        extra_vfpages.append(vfpage_url)
                
                for vfpage in extra_vfpages:
                    extra_pages.extend(self.scrapePages(vfpage_url, recursive = True))
            
            # Find all chapters links in the archive
            pages_el = []
            for a_tag in soup.find_all('a'):
                if a_tag.find('div', class_='archive-comic'):
                    pages_el.append(a_tag)
            
            # Extract pages URLs without images first
            for element in pages_el:
                page_url = element['href']
                title = element.find('span').text.strip() if element.find('span') else ''
                # Check if the URL is relative and prepend the base URL if necessary
                if page_url.startswith('/'):
                    page_url = 'https://comicfury.com' + page_url
                # Add page without image URL for now
                pages.append({"page_url": page_url, "page_title": title, "img_url": None})
            
            # Use threads to scrape images in parallel
            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                # Create a dictionary to store results with page index as key
                results = {}
                # Submit tasks to the executor
                for i, page in enumerate(pages):
                    future = executor.submit(self.scrapeImages, page['page_url'])
                    results[i] = future
                
                # Collect results as they complete
                for i, future in results.items():
                    pages[i]['img_url'] = future.result()
            
            if not recursive:
                print(f"Found {len(pages + extra_pages)} pages in chapter.")
            return pages + extra_pages
        else:
            print(f"Failed to retrieve the chapter page. Status code: {response.status_code}")
            return []
    
    def scrapeImages(self, page_url):
        """
        Scrapes all images from a page and returns a list of image URLs
        """
        self.log(f"Scraping images from page: {page_url}")
        
        # Send a GET request to the page URL
        response = requests.get(page_url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find the first page, since ComicFury loads multiple pages
            comic = soup.find('div', class_='is--comic-page')
            
            img_urls = []
            # Find all image tags in the page that start with the specified URL
            for img_tag in comic.find_all('img'):
                img_url = img_tag['src']
                # Check if the image URL starts with the desired prefix
                if img_url.startswith('https://img.comicfury.com/comics/'):
                    img_urls.append(img_url)
            return img_urls
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return []
    
    def download_chapters(self, chapters):
        """
        Downloads all chapters one by one and creates CBZ files
        """
        print("Starting sequential download of all chapters...")
        
        # Create base download directory if it doesn't exist
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            
        # Download chapters one by one
        total_chapters = len(chapters)
        for i, chapter in enumerate(chapters):
            print(f"\nProcessing chapter {i+1} of {total_chapters}: {chapter['title']}")
            # Pass the chapter index to use for ordering
            self.download_chapter(chapter, chapter_index=i+1, total_chapters=total_chapters)
                
        print("\nAll chapters downloaded and packaged as CBZ files.")
    
    def download_chapter(self, chapter, chapter_index=1, total_chapters=1):
        """
        Downloads a single chapter and creates a CBZ file with a number prefix for ordering
        """
        if not chapter.get('pages'):
            print(f"No pages found for chapter: {chapter['title']}")
            return
            
        # Create a safe filename from chapter title
        safe_title = self.get_safe_filename(chapter['title'])
        chapter_dir = os.path.join(self.download_dir, safe_title)
        
        # Create chapter directory
        if os.path.exists(chapter_dir):
            shutil.rmtree(chapter_dir)  # Remove if exists to start fresh
        os.makedirs(chapter_dir)
        
        print(f"Downloading chapter: {chapter['title']}")
        
        # Download all pages in the chapter
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = []
            for page_idx, page in enumerate(chapter['pages']):
                for img_idx, img_url in enumerate(page['img_url']):
                    # Use zero-padded index to ensure correct order
                    page_filename = f"{page_idx:03d}-{img_idx:02d}.jpg"
                    page_path = os.path.join(chapter_dir, page_filename)
                    futures.append(executor.submit(self.download_image, img_url, page_path))
            
            # Wait for all downloads to complete
            for future in futures:
                future.result()
        
        # Determine the number of digits needed for proper zero-padding
        digits = len(str(total_chapters))
        
        # Create CBZ file with number prefix for proper ordering
        cbz_filename = f"{chapter_index:0{digits}d}_{safe_title}.cbz"
        cbz_path = os.path.join(self.download_dir, cbz_filename)
        
        print(f"Creating CBZ file: {cbz_filename}")
        with zipfile.ZipFile(cbz_path, 'w') as zipf:
            for file in sorted(os.listdir(chapter_dir)):
                file_path = os.path.join(chapter_dir, file)
                if os.path.isfile(file_path):
                    zipf.write(file_path, os.path.basename(file_path))
        
        # Remove the temporary directory
        shutil.rmtree(chapter_dir)
        
        print(f"Completed: {cbz_filename}")
    
    def download_image(self, img_url, save_path):
        """
        Downloads an image from a URL and saves it to the specified path
        """
        try:
            response = requests.get(img_url, stream=True)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return True
            else:
                print(f"Failed to download image: {img_url}. Status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error downloading image {img_url}: {str(e)}")
            return False
    
    def get_safe_filename(self, filename):
        """
        Converts a string to a safe filename by removing invalid characters
        """
        # Remove invalid filename characters and replace spaces with underscores
        safe_name = re.sub(r'[\\/*?:"<>|]', "", filename)
        safe_name = safe_name.replace(' ', '_')
        # Ensure filename isn't too long
        if len(safe_name) > 100:
            safe_name = safe_name[:100]
        return safe_name
