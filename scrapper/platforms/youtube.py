from .base_scraper import BaseScraper
import yt_dlp
from ..services.logger import setup_logger

logger = setup_logger('youtube_scraper')

class YouTubeScraper(BaseScraper):
    async def scrape(self, url: str) -> dict:
        """
        Scrape YouTube metrics using yt-dlp (reliable api-like).
        Fallback to browser if needed (not implemented yet as yt-dlp is very robust).
        """
        logger.info(f"Scraping YouTube URL: {url}")
        
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'forcejson': True,
            'no_warnings': True
        }

        try:
            # yt-dlp is sync, but fast enough. For strict async we could use asyncio.to_thread
            info = await asyncio.to_thread(self._run_ytdlp, url, ydl_opts)
                
            views = info.get('view_count', 0)
            likes = info.get('like_count', 0)
            
            logger.info(f"Found {views} views, {likes} likes")
            
            return {
                'views': views,
                'likes': likes,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"YouTube scrape failed: {e}")
            return {
                'views': 0,
                'likes': 0,
                'error': str(e)
            }

    def _run_ytdlp(self, url, opts):
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)
