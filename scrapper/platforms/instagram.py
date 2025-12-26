from .base_scraper import BaseScraper
from ..utils.normalization import normalize_metric
from ..services.logger import setup_logger
from datetime import datetime
import json
import re
import os

logger = setup_logger('instagram_scraper')

class InstagramScraper(BaseScraper):
    async def scrape(self, url: str) -> dict:
        if not self.context:
            await self.start_browser(headless=self.scraping_ops['headless'])

        try:
            logger.info(f"Navigating to {url}")
            await self.page.goto(url, timeout=self.config['platforms']['instagram']['timeout'])
            await self.human_delay()
            
            # Check for login wall
            if "login" in self.page.url:
                logger.warning("Redirected to login page. Metrics might be hidden.")
            
            # Check for generic Instagram error
            try:
                error_elem = await self.page.query_selector('div:has-text("Sorry, we\'re having trouble playing this video")')
                if error_elem:
                     logger.error("Instagram Error: 'Trouble playing this video'. Likely IP/Bot detection.")
                     return {'views': 0, 'likes': 0, 'error': "INSTAGRAM_PLAYBACK_ERROR"}
            except:
                pass

            views = 0
            likes = 0
            
            # --- STRATEGY 1: JSON-LD (Structured Data) ---
            # Most reliable source if present
            try:
                # Instagram often includes a script tag with JSON-LD
                ld_json = await self.page.query_selector('script[type="application/ld+json"]')
                if ld_json:
                    json_text = await ld_json.inner_text()
                    data = json.loads(json_text)
                    logger.debug(f"Found JSON-LD: {str(data)[:200]}...") # Log start
                    
                    # Graph can be a list or dict
                    items = data if isinstance(data, list) else [data]
                    
                    for item in items:
                        # Look for interactionStatistic
                        stats = item.get('interactionStatistic', [])
                        if isinstance(stats, dict): stats = [stats]
                        
                        for stat in stats:
                            itype = stat.get('interactionType', '')
                            count = stat.get('userInteractionCount', 0)
                            
                            if 'WatchAction' in itype or 'ViewAction' in itype:
                                views = int(count) if count else views
                            elif 'LikeAction' in itype:
                                likes = int(count) if count else likes
                    
                    if views > 0 or likes > 0:
                        logger.info(f"Extracted from JSON-LD: views={views}, likes={likes}")
            except Exception as e:
                logger.debug(f"JSON-LD extraction failed: {e}")

            # --- STRATEGY 2: Meta Tags (Fallback) ---
            if views == 0 or likes == 0:
                try:
                    meta_desc = await self.page.get_attribute('meta[name="description"]', 'content')
                    if meta_desc:
                        logger.debug(f"Found meta description: {meta_desc}")
                        
                        # Try to find Views
                        # Pattern: "1.2M views" or "1234 views" or "Play count: 1.2M" or "1.2M plays"
                        if views == 0:
                            views_match = re.search(r'([\d,.]+[KMB]?)\s*(?:views|plays|count)', meta_desc, re.IGNORECASE)
                            if views_match:
                                 views = normalize_metric(views_match.group(1))

                        # Try to find Likes
                        if likes == 0:
                            likes_match = re.search(r'([\d,.]+[KMB]?)\s*likes', meta_desc, re.IGNORECASE)
                            if likes_match:
                                 likes = normalize_metric(likes_match.group(1))
                             
                        logger.debug(f"Extracted from meta: views={views}, likes={likes}")
                except Exception as e:
                    logger.warning(f"Meta extraction failed: {e}")

            # If still 0, try DOM selectors (DOM usually more accurate for real-time if visible)
            if views == 0:
                cfg_selectors = self.config['platforms']['instagram']['selectors']
                content = await self.page.content()
                
                for selector in cfg_selectors['views']:
                    try:
                        elem = await self.page.query_selector(selector)
                        if elem:
                            text = await elem.inner_text()
                            logger.debug(f"Found views text: {text}")
                            v = normalize_metric(text)
                            if v > 0:
                                views = v
                                break
                    except Exception:
                        continue
            
            if likes == 0:
                cfg_selectors = self.config['platforms']['instagram']['selectors']
                for selector in cfg_selectors['likes']:
                    try:
                        elem = await self.page.query_selector(selector)
                        if elem:
                            text = await elem.inner_text()
                            logger.debug(f"Found likes text: {text}")
                            if any(c.isdigit() for c in text):
                                l = normalize_metric(text)
                                if l > 0:
                                    likes = l
                                    break
                    except Exception:
                        continue
            
            # --- DEBUG SNAPSHOT IF FAILED ---
            if views == 0 and likes == 0:
                logger.warning(f"Zero metrics found for {url}. Taking debug snapshot.")
                timestamp = int(datetime.now().timestamp())
                debug_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs', 'debug')
                os.makedirs(debug_dir, exist_ok=True)
                
                screenshot_path = os.path.join(debug_dir, f"fail_insta_{timestamp}.png")
                html_path = os.path.join(debug_dir, f"fail_insta_{timestamp}.html")
                
                try:
                    await self.page.screenshot(path=screenshot_path)
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(await self.page.content())
                    logger.info(f"Saved debug snapshot to {screenshot_path}")
                except Exception as e:
                    logger.error(f"Failed to save debug snapshot: {e}")
            # --------------------------------

            logger.info(f"Scraped: {views} views, {likes} likes")
            
            return {
                'views': views,
                'likes': likes,
                'error': None
            }

        except Exception as e:
            logger.error(f"Instagram scrape failed: {e}")
            return {
                'views': 0,
                'likes': 0,
                'error': str(e)
            }
