# Social Media Scraper

A Python automation tool for collecting viral reels and videos from Instagram, TikTok, and YouTube.  
It reads bookmarked video links, gathers metadata (views, likes, shares), and exports results to Google Sheets.

## Features

- Import bookmarks from HTML exports or browser databases
- Scrape YouTube with `yt-dlp`
- Scrape TikTok and Instagram using Playwright
- Automatically update Google Sheets with collected data
- Modular structure for easy extension to more platforms

## Project Structure

social-media-scraper/
├── scraper/
│   ├── bookmarks_reader.py
│   ├── youtube_scraper.py
│   ├── tiktok_scraper.py
│   ├── instagram_scraper.py
│   ├── sheets_writer.py
│   └── main.py
├── config/
│   └── settings.example.json
├── data/
│   ├── bookmarks_export.html
│   └── output.json
├── requirements.txt
└── README.md

## Setup

1. **Clone the repository:**

    git clone <https://github.com/yohantse/social-media-scraper.git>
    cd social-media-scraper

2. **Install Python dependencies:**

    pip install -r requirements.txt

3. **Configure credentials:**
    - Copy `config/settings.example.json` to `config/settings.json`
    - Fill in Google Sheets API credentials, Instagram cookies, etc.

4. **Export your bookmarks:**
    - Export your saved videos folder from your browser to `data/bookmarks_export.html`

## Usage

Run the main script:

python scraper/main.py

This will:

- Read bookmarks
- Identify platform (YouTube, TikTok, Instagram)
- Scrape video metadata
- Export results to Google Sheets and `data/output.json`

## Dependencies

- Python 3.10+
- Playwright
- yt-dlp
- gspread (Google Sheets API)
- Other standard Python libraries

## Notes

- Instagram scraping requires login cookies
- Use throttling to avoid being blocked
- Playwright may require browser drivers:
  playwright install

## License

MIT License
