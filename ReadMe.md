# E-commerce Crawler

A high-performance web crawler designed to extract product links from e-commerce websites using asynchronous browser automation.

## Features

- **Asynchronous Crawling**: Utilizes Playwright for concurrent browser automation
- **Resource Management**: Implements singleton pattern for browser instances
- **Smart Pagination**: Handles both infinite scroll and paginated layouts
- **Data Persistence**: MongoDB integration with TTL-based caching
- **Request Management**: Rotates user agents and manages request timeouts

## Architecture

### Browser Management
- Uses a singleton `PlaywrightManager` to control browser instances
- Implements connection pooling with configurable max instances
- Manages browser lifecycle through async context managers
- Handles worker-to-instance mapping for thread safety

### Crawling Strategy
1. **Instance Acquisition**
   - Retrieves available browser instance from pool
   - Creates new instance if pool limit not reached
   - Queues requests when all instances are busy

2. **Page Processing**
   - Attempts infinite scrolling for dynamic content
   - Falls back to pagination if infinite scroll fails
   - Extracts HTML content of each page

3. **Data Storage**
   - Caches processed URLs with TTL
   - Stores domain-product mappings
   - Uses MongoDB with connection pooling

## Quick Start
Run with Docker:
```bash
docker-compose up --build
```

# Project Structure
```
.
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── src/
    ├── async_utils/
    ├── database/
    ├── parsers/
    └── __main__.py
```