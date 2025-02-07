
from typing import Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


class UrlExtractor:
    @classmethod
    def extract_urls(cls, html: str, base_url: str) -> Set[str]:
        soup = BeautifulSoup(html, 'html.parser')
        urls = set()

        for tag in soup.find_all(['a', 'img', 'script', 'link', 'area'], href=True):
            url = ""
            if tag.name in ['a', 'area', 'link']:
                url = urljoin(base_url, tag['href'])
            if tag.name in ['img', 'script'] and tag.get('src'):
                url = urljoin(base_url, tag['src'])
            if url and urlparse(url).netloc == urlparse(base_url).netloc:
                urls.add(url)
        return urls