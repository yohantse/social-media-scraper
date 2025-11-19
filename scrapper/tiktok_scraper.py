from playwright.sync_api import sync_playwright
import time


def scrape_tiktok(url, headless=True):
    """Scrape TikTok video metadata."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        
        try:
            page.goto(url, timeout=30000)
            time.sleep(4)  # Wait for dynamic content to load
            
            # Extract title/description
            title = ""
            try:
                # TikTok video descriptions are usually in specific elements
                title_selectors = [
                    'h1[data-e2e="browse-video-desc"]',
                    'div[data-e2e="browse-video-desc"]',
                    'span[class*="desc"]'
                ]
                for selector in title_selectors:
                    elem = page.query_selector(selector)
                    if elem:
                        title = elem.inner_text().strip()
                        break
            except:
                pass
            
            # Extract views
            views = None
            try:
                views_selectors = [
                    'strong[data-e2e="video-views"]',
                    'strong[data-e2e="browse-video-views"]',
                    'div[class*="view-count"]'
                ]
                for selector in views_selectors:
                    elem = page.query_selector(selector)
                    if elem:
                        views = elem.inner_text().strip()
                        break
            except:
                pass
            
            # Extract likes
            likes = None
            try:
                likes_selectors = [
                    'strong[data-e2e="like-count"]',
                    'strong[data-e2e="browse-like-count"]',
                    'button[data-e2e="browse-like"] strong'
                ]
                for selector in likes_selectors:
                    elem = page.query_selector(selector)
                    if elem:
                        likes = elem.inner_text().strip()
                        break
            except:
                pass
            
            # Extract comments
            comments = None
            try:
                comments_selectors = [
                    'strong[data-e2e="comment-count"]',
                    'strong[data-e2e="browse-comment-count"]',
                    'button[data-e2e="browse-comment"] strong'
                ]
                for selector in comments_selectors:
                    elem = page.query_selector(selector)
                    if elem:
                        comments = elem.inner_text().strip()
                        break
            except:
                pass
            
            # Extract shares
            shares = None
            try:
                shares_selectors = [
                    'strong[data-e2e="share-count"]',
                    'strong[data-e2e="browse-share-count"]',
                    'button[data-e2e="browse-share"] strong'
                ]
                for selector in shares_selectors:
                    elem = page.query_selector(selector)
                    if elem:
                        shares = elem.inner_text().strip()
                        break
            except:
                pass
            
            data = {
                'platform': 'TikTok',
                'url': url,
                'title': title or 'N/A',
                'views': views or 'N/A',
                'likes': likes or 'N/A',
                'comments': comments or 'N/A',
                'shares': shares or 'N/A'
            }
            
        except Exception as e:
            data = {
                'platform': 'TikTok',
                'url': url,
                'error': str(e),
                'title': 'Error',
                'views': 'N/A',
                'likes': 'N/A',
                'comments': 'N/A',
                'shares': 'N/A'
            }
        finally:
            browser.close()
        
        return data