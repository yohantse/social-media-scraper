# Social Media Scraper

A Python automation tool for collecting viral reels and videos from Instagram, TikTok, and YouTube. It reads bookmarked video links, gathers metadata (views, likes, shares), and exports results to Google Sheets.

## Features

- 📊 Scrapes metadata from Instagram, TikTok, and YouTube videos
- 📑 Reads bookmarked links from exported HTML files
- 📈 Exports data to Google Sheets automatically
- 💾 Saves results locally as JSON
- 🔄 Handles errors gracefully without stopping the batch

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

## Configuration

1. Copy `config/settings.example.json` to `config/settings.json`
2. Update the configuration:
   - Add your Google Sheets spreadsheet ID
   - Add path to your Google service account credentials file
   - Adjust scraping options as needed

### Google Sheets Setup

1. Create a Google Cloud Project
2. Enable Google Sheets API
3. Create a service account and download the JSON credentials
4. Share your spreadsheet with the service account email
5. Copy the spreadsheet ID from the URL

## Usage

1. Export your browser bookmarks as HTML (usually from browser's bookmark manager)
2. Place the exported file at `data/bookmarks_export.html`
3. Run the scraper:
```bash
cd scrapper
python main.py
```

## Output

- **JSON**: Results are saved to `data/output.json`
- **Google Sheets**: Data is automatically appended to your configured spreadsheet with headers:
  - Platform
  - Title
  - URL
  - Views
  - Likes
  - Comments
  - Shares
  - Error (if any)

## Supported Platforms

- ✅ YouTube (via yt-dlp)
- ✅ TikTok (via Playwright)
- ✅ Instagram (via Playwright)

## Notes

- Instagram and TikTok scraping may be affected by anti-bot measures
- Selectors may need updating if platforms change their HTML structure
- For best results, use `headless: false` in settings to see what's happening
- Rate limiting is recommended to avoid being blocked

## License

MIT License - see LICENSE file for details
