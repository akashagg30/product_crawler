from typing import Dict, List
from asyncio import Queue
from urllib.parse import urlparse, urlunparse
from src.database.mongo_models import cache_url_data, get_cached_url_data, get_domain_products, store_domain_product
from src.async_utils.workers import Workers
from src.async_utils.playwright_manager import PlaywrightManager
from src.parsers.product_identifier import ProductPageDetector
from src.parsers.url_extractor import UrlExtractor


class EcommerceCrawler:
    _product_page_detector = ProductPageDetector
    _playwright_manager = PlaywrightManager
    _url_extractor = UrlExtractor

    def __init__(self, domains: List[str], max_concurrent: int = 10):
        self._domains = domains
        self._visited_urls = set()
        self._product_urls = {domain: set() for domain in domains}
        self._max_concurrent = max_concurrent
        self._playwright = self._playwright_manager(max_concurrent)
        self._queue = Queue()
        self._workers = Workers(self._queue, max_concurrent)
        

    def _is_domain_url(self, url: str) -> bool:
        parsed_url = urlparse(url)
        return parsed_url.netloc in self._domains

    async def _crawl_url(self, url: str, domain: str):
        url = urlunparse(urlparse(url)._replace(fragment=''))

        if url in self._visited_urls:
            return
            
        self._visited_urls.add(url)

        cached_data = await get_cached_url_data(url)
        if cached_data:
            print("skipping", url)
            if self._is_domain_url(url):
                self._product_urls[domain] = await get_domain_products(domain)
            outgoing_urls = cached_data.get("outgoing_urls", [])
        else:
            print("crawling", url)
            htmls : List[str] = await self._playwright.fetch_html(url)
            if not htmls:
                return
            outgoing_urls = []
            for html in htmls:
                outgoing_urls += self._url_extractor.extract_urls(html, url)
            
            base_page = htmls[0]
            is_product = self._product_page_detector(base_page, url).is_product_page()
            await cache_url_data(url, is_product, outgoing_urls)
            
            if is_product:
                print("found product", url)
                self._product_urls[domain].add(url)
                await store_domain_product(domain, url)
            
        for new_url in outgoing_urls:
            if new_url in self._visited_urls:
                continue
            await self._queue.put((self._crawl_url, new_url, domain))

    async def crawl(self) -> Dict[str, List[str]]:
        # add initial URLs to queue
        for domain in self._domains:
            url = f"https://{domain}"
            await self._queue.put((self._crawl_url, url, domain))
        await self._workers.process_queue()
        return self._product_urls
    