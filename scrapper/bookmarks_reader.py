import bs4

def read_bookmarks(file_path):
    """Parse exported bookmarks HTML and return list of URLs."""
    with open(file_path, 'r', encoding='utf-8') as f:
     soup = bs4.BeautifulSoup(f, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True) if isinstance(a, bs4.element.Tag)]
    return links
