from abc import ABC, abstractmethod
from playwright.async_api import async_playwright, BrowserContext, Page
import asyncio
import os
from ..services.logger import setup_logger

logger = setup_logger('base_scraper')

class BaseScraper(ABC):
    def __init__(self, config: dict):
        self.config = config
        self.scraping_ops = config['scraping_options']
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

    def _get_user_data_dir(self):
        """Resolve user data directory for consistent contexts."""
        base_dir = self.scraping_ops.get('user_data_dir', '../data/browser_context')
        return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                            base_dir.replace('../', '')))

    async def start_browser(self, headless=True):
        """Start Playwright browser with persistent context."""
        self.playwright = await async_playwright().start()
        user_data_dir = self._get_user_data_dir()
        
        # Ensure dir exists
        os.makedirs(user_data_dir, exist_ok=True)
        
        logger.info(f"Launching browser (Headless: {headless}) with context: {user_data_dir}")
        
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir,
            headless=headless,
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            args=['--disable-blink-features=AutomationControlled']
        )
        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()

    async def close(self):
        """Cleanup resources."""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
            
    async def human_delay(self):
        """Sleep for throttle_seconds."""
        await asyncio.sleep(self.scraping_ops.get('throttle_seconds', 3))

    @abstractmethod
    async def scrape(self, url: str) -> dict:
        """
        Scrape metrics from the given URL.
        Returns dict with: {'views': int, 'likes': int, 'error': str|None}
        """
        pass
