from bs4 import BeautifulSoup
import re

from src.parsers.constants import PRODUCT_INDICATORS_REGEX, URL_PATTERN_REGEX


class ProductPageDetector:
    def __init__(self, html:str, url:str):
        self._soup = BeautifulSoup(html, 'html.parser')
        self._url = url

    def is_product_page(self):
        if self._does_url_pattern_match() or self._has_add_to_cart_button():
            return True
        
        return False

    def _does_url_pattern_match(self):
        if re.search(URL_PATTERN_REGEX, self._url.lower()):
            return True
        return False

    def _has_add_to_cart_button(self):
        # Look for an "Add to Cart" or "Buy Now" button, typically a button or link
        add_to_cart = self._soup.find_all(['button', 'a'], text=re.compile(PRODUCT_INDICATORS_REGEX, re.I))
        return add_to_cart and len(add_to_cart)==1

