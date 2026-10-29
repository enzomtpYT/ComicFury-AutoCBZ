# ComicFury Scraper

A powerful command-line tool to scrape and download comics from ComicFury.com, creating neatly organized CBZ files for offline reading.

## Features

- Scrape comic chapters and pages from ComicFury.com
- Multi-threaded downloading for improved performance
- Automatic CBZ file creation with proper ordering
- Simple command-line interface with multiple options
- Support for both URL and comic ID input methods
- Configurable output directories
- Use existing JSON files for faster downloads without re-scraping

## Installation

### Prerequisites

- Python 3.9 or higher
- Internet connection

### Dependencies

- requests
- beautifulsoup4
- argparse
- concurrent.futures (standard library)

### Installing & Running

You can run `comicfuryscraper` using any of the following methods:

#### Method 1: Instant run with `uvx` (Fastest, no installation needed)

Run directly from PyPI in an ephemeral, isolated environment:
```bash
uvx comicfuryscraper -h
```

Download a comic directly:
```bash
uvx comicfuryscraper -i COMIC_ID -d
```

#### Method 2: Global CLI tool with `uv tool` or `pipx`

Install `comicfuryscraper` as an isolated global CLI executable on your system:

**Using `uv`:**
```bash
# Install globally
uv tool install comicfuryscraper

# Run from anywhere
comicfuryscraper -h

# To upgrade later
uv tool upgrade comicfuryscraper
```

**Using `pipx`:**
```bash
# Run one-off without installing
pipx run comicfuryscraper -h

# Or install globally
pipx install comicfuryscraper
comicfuryscraper -h
```

#### Method 3: Pre-compiled standalone binaries (No Python required)

Download the standalone executable for your operating system from the [Releases page](https://github.com/enzomtpYT/ComicFury-AutoCBZ/releases/latest):
- **Linux**: `comicfuryscraper-linux-x86_64` (run `chmod +x comicfuryscraper-linux-x86_64`)
- **Windows**: `comicfuryscraper.exe`
- **macOS (Apple Silicon)**: `comicfuryscraper-macos-arm64`
- **macOS (Intel)**: `comicfuryscraper-macos-x86_64`

#### Method 4: Standard `pip install`

```bash
pip install comicfuryscraper
comicfuryscraper -h
```

#### Method 5: From source (for development)

1. Clone this repository:
```bash
git clone https://github.com/enzomtpYT/ComicFury-AutoCBZ.git
cd ComicFury-AutoCBZ
```

2. Run directly with `uv`:
```bash
uv run comicfuryscraper -h
```
Or install dependencies into a local venv using `uv sync` or `pip install -r requirements.txt`.

## Usage

### Basic Usage

You can scrape comics by **Comic ID**, standard **ComicFury URL**, or **`thecomicseries.com` URL**:

1. **By Comic ID** (found in the comic profile URL, e.g. `comicprofile.php?url=COMIC_ID`):
```bash
uvx comicfuryscraper -i COMIC_ID -d
```

2. **By URL** (supports `*.thecomicseries.com`, `comicprofile.php`, or canonical reader links):
```bash
uvx comicfuryscraper -u https://starting-over.thecomicseries.com -d
```

*(Replace `uvx comicfuryscraper` with `comicfuryscraper`, `comicfuryscraper.exe`, or `uv run comicfuryscraper` depending on your chosen installation method).*

### Command Line Arguments

| Argument | Description |
|----------|-------------|
| `-u, --url` | URL of the webpage to scrape |
| `-i, --id` | ID of the comic to scrape (alternative to URL) |
| `-t, --max-threads` | Maximum number of threads to use (default: 4) |
| `-d, --download` | Download the comic and create CBZ files |
| `-o, --output` | Output directory for downloaded files |
| `-v, --verbose` | Enable verbose output |
| `-j, --json` | Path to a JSON file with chapter data (skips scraping) |

### Examples

1. Scrape comic information without downloading:

```
python cli.py -i yourcomicid
```

This will generate a `yourcomicid-chapters.json` file with all chapters and pages information.

2. Download a comic using its ID and save to a specific folder:

```
python cli.py -i yourcomicid -d -o "My Comics/ComicName"
```

3. Download a comic using its URL with verbose output:

```
python cli.py -u "https://comicfury.com/comicprofile.php?url=yourcomicid" -d -v
```

4. Increase download speed by using more threads:

```
python cli.py -i yourcomicid -d -t 8
```

5. Use a previously generated JSON file to download without scraping:

```
python cli.py -j yourcomicid-chapters.json -d
```

6. Download a comic using an existing JSON file and save to a specific directory:

```
python cli.py -j yourcomicid-chapters.json -d -o "My Comics/ComicName"
```

## How It Works

1. The scraper first checks if a JSON file with chapter data exists
   - If specified with `-j` flag, it uses that file
   - Otherwise, it looks for a default file named `[comic-id]-chapters.json`
2. If no JSON file is found, it scrapes all chapters from the comic's archive page
3. For each chapter, it finds all pages and their image URLs
4. When downloading, it creates a temporary directory for each chapter
5. Images are downloaded with proper ordering (001.jpg, 002.jpg, etc.)
6. A CBZ file is created for each chapter with numbered prefixes for proper ordering
7. Temporary directories are cleaned up automatically

## Output

Downloaded comics are saved as CBZ files in the specified output directory (or a directory named after the comic ID by default). Files are named with numerical prefixes to ensure proper ordering, for example:

```
01_Chapter_Name.cbz
02_Another_Chapter.cbz
etc...
```

## Limitations

- Only works on Comic With Infinite Scroll if comic has infinite scroll disabled, please use [ComicFury-Scrape](https://github.com/enzomtpYT/comicFury-Scrape)

![Infinite Scroll Example](https://share.enzomtp.party/pBhm0HTQel23U3pCREQSNPwm.png)

## License

[MIT License](https://github.com/enzomtpYT/ComicFury-AutoCBZ/blob/main/LICENSE)

## Contributing

Contributions, issues, and feature requests are welcome!

### Development Setup

1. Install dependencies and dev tools using `uv`:
```bash
uv sync
```

2. Verify code quality and types before submitting a pull request:
```bash
# Run linting and code style checks
uv run ruff check .

# Run static type checking
uv run ty check .

# Check for unused code or dead imports
uv run vulture

# Run automated tests
uv run pytest
```