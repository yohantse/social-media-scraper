from playwright.sync_api import sync_playwright
import time


def scrape_instagram(url, headless=True):
    """Scrape Instagram reel/video metadata."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        
        try:
            page.goto(url, timeout=30000)
            time.sleep(3)  # Wait for dynamic content to load
            
            # Extract title/caption
            title = ""
            try:
                title_elem = page.query_selector('h1')
                if title_elem:
                    title = title_elem.inner_text().strip()
            except:
                pass
            
            # Extract views - Instagram shows views on reels
            views = None
            try:
                # Try multiple selectors for views
                views_selectors = [
                    'span:has-text("views")',
                    'span:has-text("view")',
                    'div[class*="view"]'
                ]
                for selector in views_selectors:
                    elem = page.query_selector(selector)
                    if elem:
                        text = elem.inner_text()
                        # Extract number from text like "1.2M views" or "1,234 views"
                        import re
                        match = re.search(r'([\d,.]+[KMB]?)', text)
                        if match:
                            views = match.group(1)
                            break
            except:
                pass
            
            # Extract likes
            likes = None
            try:
                # Look for like button or like count
                like_selectors = [
                    'button[aria-label*="like"] span',
                    'span[class*="like"]',
                    'section button span'
                ]
                for selector in like_selectors:
                    elem = page.query_selector(selector)
                    if elem:
                        text = elem.inner_text().strip()
                        if text and any(c.isdigit() for c in text):
                            likes = text
                            break
            except:
                pass
            
            # Extract comments count
            comments = None
            try:
                comment_selectors = [
                    'span:has-text("comment")',
                    'a[href*="comments"] span'
                ]
                for selector in comment_selectors:
                    elem = page.query_selector(selector)
                    if elem:
                        text = elem.inner_text()
                        import re
                        match = re.search(r'([\d,.]+[KMB]?)', text)
                        if match:
                            comments = match.group(1)
                            break
            except:
                pass
            
            data = {
                'platform': 'Instagram',
                'url': url,
                'title': title or 'N/A',
                'views': views or 'N/A',
                'likes': likes or 'N/A',
                'comments': comments or 'N/A'
            }
            
        except Exception as e:
            data = {
                'platform': 'Instagram',
                'url': url,
                'error': str(e),
                'title': 'Error',
                'views': 'N/A',
                'likes': 'N/A',
                'comments': 'N/A'
            }
        finally:
            browser.close()
        
        return data