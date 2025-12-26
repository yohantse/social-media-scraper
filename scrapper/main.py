import os
import json
import time
from datetime import datetime
from .services.sheet_service import GoogleSheetClient
from .services.logger import setup_logger
from .platforms.youtube import YouTubeScraper
from .platforms.instagram import InstagramScraper
from .platforms.tiktok import TikTokScraper
import asyncio
import nest_asyncio

# We still use nest_asyncio just in case gspread or other libs have internal loops,
# though we are now running a proper top-level loop.
nest_asyncio.apply()

logger = setup_logger('main_controller')

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def get_scraper_for_url(url, config, active_scrapers):
    scraper_instance = None
    platform_name = None

    if 'youtube.com' in url or 'youtu.be' in url:
        platform_name = 'YouTubeScraper'
        if platform_name in active_scrapers:
            scraper_instance = active_scrapers[platform_name]
        else:
            scraper_instance = YouTubeScraper(config)
            active_scrapers[platform_name] = scraper_instance
    elif 'instagram.com' in url:
        platform_name = 'InstagramScraper'
        if platform_name in active_scrapers:
            scraper_instance = active_scrapers[platform_name]
        else:
            scraper_instance = InstagramScraper(config)
            active_scrapers[platform_name] = scraper_instance
    elif 'tiktok.com' in url:
        platform_name = 'TikTokScraper'
        if platform_name in active_scrapers:
            scraper_instance = active_scrapers[platform_name]
        else:
            scraper_instance = TikTokScraper(config)
            active_scrapers[platform_name] = scraper_instance
    return scraper_instance

async def main():
    logger.info("Starting Social Media Scraper...")

    # 1. Load Config
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return

    # 2. Connect to Google Sheet
    try:
        sheet_client = GoogleSheetClient(os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.json'))
        sheet_client.connect()
        logger.info("Successfully connected to Google Sheet")
    except Exception as e:
        logger.error(f"Failed to connect to Google Sheets: {e}")
        return

    # 3. Read Rows
    rows = sheet_client.get_rows()
    if not rows:
        logger.warning("No rows found in sheet.")
        return

    logger.info(f"Found {len(rows)} rows to process.")

    # Check for required columns
    required_cols = config['google_sheets']['columns'].values()
    if rows and not all(col in rows[0] for col in required_cols if col != "Video URL"): # video url key varies
        # We do a loose check or rely on the get_rows dict keys
        # The sheet_client already maps them? No, sheet_service uses dictreader which uses header row.
        # Use first row keys to validate
        available_headers = list(rows[0].keys())
        missing = [col for col in required_cols if col not in available_headers and col != config['google_sheets']['columns']['url']]
        if missing:
             logger.warning(f"Missing columns in sheet: {missing}. Update sheet headers to match settings.json.")

    active_scrapers = {}

    for i, row in enumerate(rows):
        row_num = i + 2 # 1-based index, +1 for header
        
        url_col = config['google_sheets']['columns']['url']
        url = row.get(url_col)

        if not url:
            logger.warning(f"Row {row_num} has no URL. Skipping.")
            continue

        logger.info(f"Processing Row {row_num}: {url}")

        try:
            scraper = get_scraper_for_url(url, config, active_scrapers)
            if not scraper:
                logger.warning(f"No scraper found for URL: {url}")
                sheet_client.update_row(row_num, {'status': 'UNSUPPORTED_PLATFORM'})
                continue

            # Scrape
            result = await scraper.scrape(url)
            
            if result.get('error'):
                logger.error(f"Error scraping row {row_num}: {result['error']}")
                sheet_client.update_row(row_num, {'status': f"ERROR: {result['error']}"})
                continue

            # Update Sheet
            update_data = {
                'views': result['views'],
                'likes': result['likes'],
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'status': 'SUCCESS',
                'platform': scraper.__class__.__name__.replace('Scraper', '')
            }
            sheet_client.update_row(row_num, update_data)

        except Exception as e:
            logger.error(f"Unexpected error processing row {row_num}: {e}")
            try:
                sheet_client.update_row(row_num, {'status': f"CRITICAL_ERROR: {str(e)}"})
            except:
                pass # If update fails, just log it.

    # Cleanup
    logger.info("Cleaning up scrapers...")
    for scraper in active_scrapers.values():
        await scraper.close()
    
    logger.info("Scraping run complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Scraper stopped by user.")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")