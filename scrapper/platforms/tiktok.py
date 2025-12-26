from .base_scraper import BaseScraper
from ..utils.normalization import normalize_metric
from ..services.logger import setup_logger

logger = setup_logger('tiktok_scraper')

class TikTokScraper(BaseScraper):
    async def scrape(self, url: str) -> dict:
        if not self.context:
            await self.start_browser(headless=self.scraping_ops['headless'])

        try:
            logger.info(f"Navigating to {url}")
            await self.page.goto(url, timeout=self.config['platforms']['tiktok']['timeout'])
            await self.human_delay()
            
            # TikTok often has a captcha or login, hard to bypass fully without stealth
            # But for public videos, it often works.
            
            views = 0
            likes = 0
            
            selectors = self.config['platforms']['tiktok']['selectors']
            
            # Extract Views
            for selector in selectors['views']:
                try:
                    elem = await self.page.query_selector(selector)
                    if elem:
                        text = await elem.inner_text()
                        logger.debug(f"Found views text: {text}")
                        views = normalize_metric(text)
                        if views > 0: break
                except Exception:
                    continue
                    
            # Extract Likes
            for selector in selectors['likes']:
                try:
                    elem = await self.page.query_selector(selector)
                    if elem:
                        text = await elem.inner_text()
                        logger.debug(f"Found likes text: {text}")
                        likes = normalize_metric(text)
                        if likes > 0: break
                except Exception:
                    continue
            
            logger.info(f"Scraped: {views} views, {likes} likes")
            
            return {
                'views': views,
                'likes': likes,
                'error': None
            }

        except Exception as e:
            logger.error(f"TikTok scrape failed: {e}")
            return {
                'views': 0,
                'likes': 0,
                'error': str(e)
            }
