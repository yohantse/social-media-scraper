from typing import Any
import yt_dlp

def scrape_youtube(url):
    """Return metadata for a YouTube video."""
    ydl_opts: Any = {
    'quiet': True,
    'skip_download': True,
    'forcejson': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return {
    'title': info.get('title'),
    'views': info.get('view_count'),
    'likes': info.get('like_count'),
    'url': url
    }

