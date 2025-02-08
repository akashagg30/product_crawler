import asyncio
from datetime import datetime
from collections.abc import Iterable
from typing import List
from src.constants import MONGO_URI, URL_CACHE_TTL_DAYS
from pymongo import AsyncMongoClient

# MongoDB Client Setup with Connection Pooling
client = AsyncMongoClient(MONGO_URI, maxPoolSize=100)
db = client['ecommerce_crawler']

# Collections
domain_products = db['domain_products']
url_cache = db['url_cache']

# Create TTL index for URL cache collection
async def create_indexes():
    await url_cache.create_index("created_at", expireAfterSeconds=URL_CACHE_TTL_DAYS * 24 * 60 * 60)

# Ensure indexes are created on startup
asyncio.run(create_indexes())

async def store_domain_product(domain: str, product_url: str):
    if not domain or not product_url:
        return
    
    try:
        await domain_products.update_one(
            {"domain": domain},
            {
                "$addToSet": {"product_urls": product_url}
            },
        )
    except Exception as e:
        print(e)
        raise e

async def get_domain_products(domain: str) -> set:
    if not domain:
        return set()
    
    try:
        data = await domain_products.find_one({"domain": domain})
        if data:
            return set(data.get("product_urls", []))
        else:
            return set()
    except Exception:
        return set()

async def get_cached_url_data(url: str) -> dict:
    if not url:
        return None
    
    try:
        data = await url_cache.find_one({"url": url})
        return data
    except Exception as e:
        print(e)
        return None

async def cache_url_data(url: str, is_product: bool, outgoing_urls: List[str] = []):
    if not url:
        return
    
    if isinstance(outgoing_urls, Iterable) and not isinstance(outgoing_urls, list):
        outgoing_urls = list(outgoing_urls)
    
    try:
        await url_cache.insert_one({
            "url": url,
            "is_product": is_product,
            "created_at": datetime.utcnow(),
            "outgoing_urls": outgoing_urls
        })
    except Exception as e:
        print(e)

async def delete_all():
    try:
        await domain_products.delete_many({})
        await url_cache.delete_many({})
    except Exception as e:
        raise e
