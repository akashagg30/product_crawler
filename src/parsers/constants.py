PRODUCT_INDICATORS = {
    'add to cart',
    'buy now',
    'buy it now'
    'pay now',
    'out of stock',
    'add to basket',
    'add to bag',
    'checkout',
    'purchase',
}

PRODUCT_INDICATORS_REGEX = "|".join(PRODUCT_INDICATORS)

URL_PATTERNS = [
    r'/product/',
    r'/products/',
    r'/dp/',
    r'/item/',
    r'/p/',
    r'shop',
]

URL_PATTERN_REGEX = "|".join(URL_PATTERNS)