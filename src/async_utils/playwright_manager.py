import asyncio
import random
from typing import Dict, List
from playwright.async_api import async_playwright, Browser, Playwright, Page
import threading

from async_utils.constants import REQUEST_DEFUALT_TIMEOUT, USER_AGENTS


class PlaywrightManager:
    _instance = None
    _lock = threading.Lock() # for singelton class

    # for singelton class (we want it to be singelton to limit memory consumed by playwright instances)
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, max_instances: int = 5):
        if not hasattr(self, 'initialized'):
            print("max_instance", max_instances)
            self._max_instances = max_instances
            self._instances_queue : asyncio.Queue = asyncio.Queue(maxsize=max_instances) # to store available instance
            self._worker_to_instance_mapping : Dict[str, Browser] = {} # to store which worker is using which instance
            self._acquire_lock = asyncio.Lock()
            self._release_lock = asyncio.Lock()
            self._semaphore = asyncio.Semaphore(max_instances) # to limit number of active instances

    async def _create_instance(self):
        """Create a new Playwright instance."""
        playwright = await async_playwright().start()
        return await playwright.chromium.launch()


    async def _get_available_instance(self) -> Browser:
        """Retrieve an available Playwright instance or create a new one if needed."""
        async with self._acquire_lock: # lock for isolation of this function calls
            if self._semaphore.locked(): # if all the instances are already created 
                return await self._instances_queue.get()
            else:
                await self._semaphore.acquire()
                instance = await self._create_instance()
                return instance

    async def __aenter__(self) -> Browser:
        """Enter the context manager and acquire a Playwright instance."""
        instance = await self._get_available_instance()
        worker_id = str(threading.current_thread().ident)
        self._worker_to_instance_mapping[worker_id] = instance # map worker with instance
        return instance

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Exit the context manager, return the Playwright instance to the pool."""
        worker_id = str(threading.current_thread().ident)

        instance = self._worker_to_instance_mapping.pop(worker_id, None) # getting instance used from worker
        async with self._release_lock:
            if not instance:
                pass
            elif not instance.is_connected(): # if instance is not working
                await instance.close()
                self._semaphore.release()
            else:
                await self._instances_queue.put(instance) # put instance back to queue

    async def _try_infinite_scrolling(self, page:Page) -> None:
        previous_height = await page.evaluate('document.body.scrollHeight')
        
        while True:
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)') # scroll to the bottom of the page

            await page.wait_for_load_state(state='networkidle', timeout=REQUEST_DEFUALT_TIMEOUT*1000)
            await asyncio.sleep(0.1) # waiting for content to render on DOM
            
            current_height = await page.evaluate('document.body.scrollHeight')

            if current_height == previous_height: # if height doesn't change
                break

            previous_height = current_height
    
    async def _get_paginated_html(self, page:Page) -> List[str]:
        page_html_list = []  # list to hold the HTML content of each page
        has_next_page = True  # flag to check if there is a next page

        while has_next_page:
            await page.wait_for_load_state(state='networkidle', timeout=REQUEST_DEFUALT_TIMEOUT*1000)
            await asyncio.sleep(0.1) # waiting for content to render on dom

            page_html = await page.content()
            page_html_list.append(page_html) # adding html in list

            # get all potential pagination elements (buttons, divs, etc.)
            pagination_buttons = await page.query_selector_all('button.next, .pagination-next, div.next, span.next')

            next_button = None
            for btn in pagination_buttons:
                # filter out any elements that have an href attribute
                href = await btn.get_attribute('href')
                if href is None and await btn.is_visible() and not await btn.is_disabled():
                    next_button = btn
                    break  # stop once we find the first valid next button without an href

            if not next_button:
                has_next_page = False
            else:
                await next_button.click()

        return page_html_list
    
    async def fetch_html(self, url: str) -> List[str]:
        async with self as browser:
            try:
                page = await browser.new_page(user_agent=random.choice(USER_AGENTS))
            except Exception as e:
                raise e
            content = []
            try:
                await page.goto(url, timeout=REQUEST_DEFUALT_TIMEOUT*1000, wait_until="networkidle")
                await self._try_infinite_scrolling(page) # trying infinite scroll on first page
                content = await self._get_paginated_html(page)
            except Exception as e:
                print(e)
            finally:
                await page.close()
            return content

