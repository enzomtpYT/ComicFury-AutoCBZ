from unittest.mock import MagicMock
import requests
from comicfuryscraper import ComicScraper


def test_import():
    assert ComicScraper is not None


def test_session_initialization():
    scraper = ComicScraper("https://comicfury.com/read/test/archive", id="test")
    assert isinstance(scraper.session, requests.Session)
    assert "User-Agent" in scraper.session.headers


def test_download_image_uses_session(tmp_path):
    scraper = ComicScraper("https://comicfury.com/read/test/archive", id="test")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.iter_content.return_value = [b"fake_image_bytes"]
    scraper.session.get = MagicMock(return_value=mock_resp)

    dest = tmp_path / "page_001.jpg"
    success = scraper.download_image("https://img.comicfury.com/comics/123.jpg", str(dest))

    assert success is True
    scraper.session.get.assert_called_once_with("https://img.comicfury.com/comics/123.jpg", stream=True)
    assert dest.read_bytes() == b"fake_image_bytes"
