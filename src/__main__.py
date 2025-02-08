import asyncio
from src.crawler.crawler import EcommerceCrawler

async def main():
    print("starting crawler")
    domains = [
        "www.maybellindia.com",
        # "in.iherb.com",
    ]
    crawler = EcommerceCrawler(domains)
    results = await crawler.crawl()
    
    print(domains, results)

asyncio.run(main())
