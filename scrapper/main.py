import os
from bookmarks_reader import read_bookmarks
from youtube_scraper import scrape_youtube
from tiktok_scraper import scrape_tiktok
from instagram_scraper import scrape_instagram
from sheets_writer import write_to_sheet
import json


CONFIG_FILE = os.path.join('..', 'config', 'settings.json')
DATA_FILE = os.path.join('..', 'data', 'bookmarks_export.html')
OUTPUT_FILE = os.path.join('..', 'data', 'output.json')


# Load configuration
import json
with open(CONFIG_FILE, 'r') as f:
    config = json.load(f)


# Read bookmarks
links = read_bookmarks(DATA_FILE)


results = []
for link in links:
    if 'youtube.com' in link:
        results.append(scrape_youtube(link))
    elif 'tiktok.com' in link:
        results.append(scrape_tiktok(link, headless=config['scraping_options']['headless']))
    elif 'instagram.com' in link:
        results.append(scrape_instagram(link, headless=config['scraping_options']['headless']))


# Save to local JSON
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4)


# Write to Google Sheets
write_to_sheet(results, config['google_sheets']['credentials_file'], config['google_sheets']['spreadsheet_id'])