import requests
from bs4 import BeautifulSoup

from services.avatar_provider import AvatarProvider
from utils.html import get_image_from_selector


class RedditService(AvatarProvider):
    """service adapter for reddit"""

    def get_avatar_url(self, username):
        """get reddit avatar url for username"""
        try:
            url = f"https://www.reddit.com/user/{username}"

            headers = {"accept-language": "en"}

            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                return get_image_from_selector(soup, 'img[alt*="avatar"]')

            return None
        except Exception:
            return None
