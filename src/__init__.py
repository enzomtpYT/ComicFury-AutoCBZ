"""ComicFury Scraper package."""
try:
    from .index import ComicScraper
except ImportError:
    from index import ComicScraper

__version__ = "1.1.0"
__all__ = ["ComicScraper", "__version__"]
