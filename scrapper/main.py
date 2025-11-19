import os
import json
from bookmarks_reader import read_bookmarks
from youtube_scraper import scrape_youtube
from tiktok_scraper import scrape_tiktok
from instagram_scraper import scrape_instagram
from sheets_writer import write_to_sheet


def main():
    """Main orchestrator for social media scraping."""
    # File paths
    CONFIG_FILE = os.path.join('..', 'config', 'settings.json')
    DATA_FILE = os.path.join('..', 'data', 'bookmarks_export.html')
    OUTPUT_FILE = os.path.join('..', 'data', 'output.json')

    # Load configuration
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {CONFIG_FILE}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in configuration file {CONFIG_FILE}")
        return

    # Read bookmarks
    try:
        links = read_bookmarks(DATA_FILE)
        print(f"Found {len(links)} bookmarked links")
    except FileNotFoundError:
        print(f"Error: Bookmarks file not found at {DATA_FILE}")
        return
    except Exception as e:
        print(f"Error reading bookmarks: {e}")
        return

    # Scrape each link
    results = []
    for i, link in enumerate(links, 1):
        print(f"\nProcessing {i}/{len(links)}: {link}")
        
        try:
            if 'youtube.com' in link or 'youtu.be' in link:
                print("  -> Scraping YouTube...")
                result = scrape_youtube(link)
                results.append(result)
            elif 'tiktok.com' in link:
                print("  -> Scraping TikTok...")
                result = scrape_tiktok(link, headless=config.get('scraping_options', {}).get('headless', True))
                results.append(result)
            elif 'instagram.com' in link:
                print("  -> Scraping Instagram...")
                result = scrape_instagram(link, headless=config.get('scraping_options', {}).get('headless', True))
                results.append(result)
            else:
                print(f"  -> Skipping unsupported platform")
                results.append({
                    'platform': 'Unknown',
                    'url': link,
                    'error': 'Unsupported platform',
                    'title': 'N/A',
                    'views': 'N/A',
                    'likes': 'N/A'
                })
        except Exception as e:
            print(f"  -> Error: {e}")
            results.append({
                'platform': 'Error',
                'url': link,
                'error': str(e),
                'title': 'N/A',
                'views': 'N/A',
                'likes': 'N/A'
            })

    # Save to local JSON
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)
        print(f"\n✓ Results saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"\nError saving results to JSON: {e}")

    # Write to Google Sheets
    try:
        sheets_config = config.get('google_sheets', {})
        credentials_file = sheets_config.get('credentials_file')
        spreadsheet_id = sheets_config.get('spreadsheet_id')
        
        if credentials_file and spreadsheet_id:
            print(f"\nWriting to Google Sheets...")
            write_to_sheet(results, credentials_file, spreadsheet_id)
            print("✓ Data written to Google Sheets successfully")
        else:
            print("\nSkipping Google Sheets export (credentials or spreadsheet ID not configured)")
    except Exception as e:
        print(f"\nError writing to Google Sheets: {e}")

    print(f"\n{'='*50}")
    print(f"Scraping complete! Processed {len(results)} links")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()