# ComicFury Scraper

A powerful command-line tool to scrape and download comics from ComicFury.com, creating neatly organized CBZ files for offline reading.

## Features

- Scrape comic chapters and pages from ComicFury.com
- Multi-threaded downloading for improved performance
- Automatic CBZ file creation with proper ordering
- Simple command-line interface with multiple options
- Support for both URL and comic ID input methods
- Configurable output directories

## Installation

### Prerequisites

- Python 3.9 or higher
- Internet connection

### Dependencies

- requests
- beautifulsoup4
- argparse
- concurrent.futures (standard library)

### Installing

1. Clone this repository or download the source code:

```
git clone https://github.com/yourusername/ComicsInfiniteScroll.git
cd ComicsInfiniteScroll
```

2. Install the required dependencies:

```
pip install -r requirements.txt
cd src
```

or download the executable at the [release page](https://github.com/enzomtpYT/ComicFury-AutoCBZ/releases/latest)

## Usage

### Basic Usage

Get the comic ID from the profile page

![URL Bar](https://github.com/enzomtpYT/ComicFury-Scrape/assets/40535918/78a2e591-6b3a-4fc0-b32f-ac79fac628dc)

Then execute:

```
python cli.py -i COMIC_ID -d
```

OR

```
comicfuryscraper.exe -i COMIC_ID -d
```

### Command Line Arguments

| Argument | Description |
|----------|-------------|
| `-u, --url` | URL of the webpage to scrape |
| `-i, --id` | ID of the comic to scrape (alternative to URL) |
| `-t, --max-threads` | Maximum number of threads to use (default: 4) |
| `-d, --download` | Download the comic and create CBZ files |
| `-o, --output` | Output directory for downloaded files |
| `-v, --verbose` | Enable verbose output |

### Examples

1. Scrape comic information without downloading:

```
python cli.py -i yourcomicid
```

This will generate a `chapters.json` file with all chapters and pages information.

2. Download a comic using its ID and save to a specific folder:

```
python cli.py -i yourcomicid -d -o "My Comics/ComicName"
```

3. Download a comic using its URL with verbose output:

```
python cli.py -u "https://comicfury.com/read/yourcomicid/archive" -d -v
```

4. Increase download speed by using more threads:

```
python cli.py -i yourcomicid -d -t 8
```

## How It Works

1. The scraper first extracts all chapters from the comic's archive page
2. For each chapter, it finds all pages and their image URLs
3. When downloading, it creates a temporary directory for each chapter
4. Images are downloaded with proper ordering (001.jpg, 002.jpg, etc.)
5. A CBZ file is created for each chapter with numbered prefixes for proper ordering
6. Temporary directories are cleaned up automatically

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