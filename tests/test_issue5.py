from unittest.mock import MagicMock

from comicfuryscraper import ComicScraper  # ty: ignore[unresolved-import]
from comicfuryscraper.cli import parse_comic_target  # ty: ignore[unresolved-import]


def test_parse_comic_target_thecomicseries():
    # Various thecomicseries.com formats
    urls = [
        "https://starting-over.thecomicseries.com",
        "http://starting-over.thecomicseries.com/",
        "starting-over.thecomicseries.com",
        "https://starting-over.thecomicseries.com/archive",
        "https://starting-over.thecomicseries.com/archive/",
        "https://starting-over.thecomicseries.com/comics/1",
    ]
    for u in urls:
        cid, canonical_url = parse_comic_target(url=u)
        assert cid == "starting-over", f"Failed for {u}"
        assert canonical_url == "https://comicfury.com/read/starting-over/archive"


def test_parse_comic_target_comicfury_urls():
    # Profile URL
    cid, canonical_url = parse_comic_target(url="https://comicfury.com/comicprofile.php?url=acrossthedivide")
    assert cid == "acrossthedivide"
    assert canonical_url == "https://comicfury.com/read/acrossthedivide/archive"

    # Read archive URL
    cid, canonical_url = parse_comic_target(url="https://comicfury.com/read/acrossthedivide/archive")
    assert cid == "acrossthedivide"
    assert canonical_url == "https://comicfury.com/read/acrossthedivide/archive"

    # Bare read URL
    cid, canonical_url = parse_comic_target(url="https://comicfury.com/read/acrossthedivide")
    assert cid == "acrossthedivide"
    assert canonical_url == "https://comicfury.com/read/acrossthedivide/archive"


def test_parse_comic_target_id():
    cid, canonical_url = parse_comic_target(comic_id="acrossthedivide")
    assert cid == "acrossthedivide"
    assert canonical_url == "https://comicfury.com/read/acrossthedivide/archive"


def test_content_warning_auto_submission():
    scraper = ComicScraper("https://comicfury.com/read/sample/archive", id="sample")
    
    # Mock warning response
    warning_html = """
    <html>
      <head><title>Content Warning - Comic Fury</title></head>
      <body>
        <form action="/read/sample/archive" method="post">
          <input type="hidden" name="token" value="987654" />
          <input type="submit" name="proceed" value="View Webcomic" />
        </form>
      </body>
    </html>
    """
    warning_resp = MagicMock()
    warning_resp.status_code = 200
    warning_resp.text = warning_html

    success_resp = MagicMock()
    success_resp.status_code = 200
    success_resp.text = "<html><body><div class='archive-chapter'></div></body></html>"

    scraper.session.get = MagicMock(return_value=warning_resp)
    scraper.session.post = MagicMock(return_value=success_resp)

    final_resp = scraper._fetch_url("https://comicfury.com/read/sample/archive")

    scraper.session.get.assert_called_once_with("https://comicfury.com/read/sample/archive")
    scraper.session.post.assert_called_once_with(
        "https://comicfury.com/read/sample/archive",
        data={"token": "987654", "proceed": "View Webcomic"}
    )
    assert final_resp == success_resp
