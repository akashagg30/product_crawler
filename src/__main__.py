import asyncio
import json
from crawler.crawler import EcommerceCrawler

async def main():
    domains = [
        # "www.maybellindia.com",
        # "in.iherb.com",
    ]
    crawler = EcommerceCrawler(domains)
    results = await crawler.crawl()
    
    print(domains, results)

asyncio.run(main())
