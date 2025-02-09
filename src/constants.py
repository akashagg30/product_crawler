import os

MONGO_URI =  os.getenv("MONGO_URI", "mongodb://localhost:27017/")
URL_CACHE_TTL_DAYS = int(os.getenv("URL_CACHE_TTL_DAYS", "7"))
REQUEST_DEFAULT_TIMEOUT = int(os.getenv("REQUEST_DEFAULT_TIMEOUT", "60"))
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "10"))