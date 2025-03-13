import random
from functools import lru_cache

import requests
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
]


def get_random_user_agent():
    """Get a random user agent from the list."""
    return random.choice(USER_AGENTS)


@lru_cache(maxsize=100)
def get_html(url, headers=None, timeout=10):
    """
    Get HTML content from a URL and parse it with BeautifulSoup.

    Args:
        url (str): The URL to fetch
        headers (dict, optional): Custom headers to use
        timeout (int, optional): Request timeout in seconds

    Returns:
        tuple: (BeautifulSoup object, response)
    """
    default_headers = {
        "User-Agent": get_random_user_agent(),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

    if headers:
        default_headers.update(headers)

    try:
        response = requests.get(url, headers=default_headers, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup, response
    except Exception:
        return None, None


def get_meta_content(soup, property_name):
    """
    Get content from a meta tag with the specified property.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object
        property_name (str): The meta property to look for

    Returns:
        str: The content of the meta tag or None
    """
    if not soup:
        return None

    meta_tag = soup.find("meta", property=property_name)
    if meta_tag:
        return meta_tag.get("content")
    return None


def get_image_from_selector(soup, selector):
    """
    Get image URL from an element matching the CSS selector.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object
        selector (str): CSS selector for the image element

    Returns:
        str: The image URL or None
    """
    if not soup:
        return None

    element = soup.select_one(selector)
    if element:
        # Try to get src attribute first, then srcset if available
        src = element.get("src")
        if src:
            return src

        srcset = element.get("srcset")
        if srcset:
            # Get the highest resolution image from srcset
            parts = srcset.split(",")
            if parts:
                # Get the last part which typically has the highest resolution
                last_part = parts[-1].strip()
                # Extract the URL from the srcset format
                url = last_part.split(" ")[0]
                return url

    return None
