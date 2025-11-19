from typing import Any
import yt_dlp


def scrape_youtube(url):
    """Return metadata for a YouTube video."""
    ydl_opts: Any = {
        'quiet': True,
        'skip_download': True,
        'forcejson': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        return {
            'platform': 'YouTube',
            'url': url,
            'title': info.get('title', 'N/A'),
            'views': info.get('view_count', 'N/A'),
            'likes': info.get('like_count', 'N/A'),
            'comments': info.get('comment_count', 'N/A')
        }
    except Exception as e:
        return {
            'platform': 'YouTube',
            'url': url,
            'error': str(e),
            'title': 'Error',
            'views': 'N/A',
            'likes': 'N/A',
            'comments': 'N/A'
        }
