"""ComicFury Scraper package."""
try:
    from .index import ComicScraper
except ImportError:
    from index import ComicScraper

__version__ = "1.0.1"
__all__ = ["ComicScraper", "__version__"]
