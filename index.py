import requests
from bs4 import BeautifulSoup
import threading
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

class ComicScraper:
    def __init__(self, url, max_threads=8):
        self.url = url
        self.max_threads = max_threads
    
    def scrapeChapters(self):
        """
        Scrapes the comic page and returns a list of chapters with their titles and URLs
        """
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
    
    def scrapePages(self, chapter_url):
        """
        Scrapes all pages from a chapter and returns a list of page URLs
        """
        print(f"Scraping pages from chapter: {chapter_url}")
        
        # Send a GET request to the chapter URL
        response = requests.get(chapter_url)
        
        pages = []
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')
            
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
                    future = executor.submit(self.scrapeImage, page['page_url'])
                    results[i] = future
                
                # Collect results as they complete
                for i, future in results.items():
                    pages[i]['img_url'] = future.result()
            
            print(f"Found {len(pages)} pages in chapter.")
            return pages
        else:
            print(f"Failed to retrieve the chapter page. Status code: {response.status_code}")
            return []
    
    def scrapeImage(self, page_url):
        """
        Scrapes all images from a page and returns a list of image URLs
        """
        print(f"Scraping images from page: {page_url}")
        
        # Send a GET request to the page URL
        response = requests.get(page_url)
             
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all image tags in the page that start with the specified URL
            for img_tag in soup.find_all('img'):
                img_url = img_tag['src']
                # Check if the image URL starts with the desired prefix
                if img_url.startswith('https://img.comicfury.com/comics/'):
                    return img_url
            return None
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return None