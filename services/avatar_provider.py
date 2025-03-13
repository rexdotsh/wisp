import hashlib
from abc import ABC, abstractmethod
from urllib.parse import urlparse

import requests

from config import Config
from utils.html import get_html, get_image_from_selector, get_meta_content


class AvatarProvider(ABC):
    """
    Base class for all avatar providers.
    """

    def __init__(self):
        self.name = self.__class__.__name__.replace("Service", "").lower()
        self.timeout = Config.AVATAR_TIMEOUT / 1000  # Convert to seconds

    @abstractmethod
    def get_avatar_url(self, username):
        """
        Get the avatar URL for the given username.

        Args:
            username (str): The username to get the avatar for

        Returns:
            str: The avatar URL or None if not found
        """
        pass

    def get_profile_picture(self, username):
        """
        Get the profile picture for the given username.

        Args:
            username (str): The username to get the profile picture for

        Returns:
            tuple: (image_data, image_url, error)
                - image_data: The binary image data or None if error
                - image_url: The URL of the image or None if error
                - error: Error message or None if success
        """
        try:
            avatar_url = self.get_avatar_url(username)

            if not avatar_url:
                return self.handle_error(404, f"Avatar not found for {username} on {self.name}")

            image_data = self.download_image(avatar_url)
            return image_data, avatar_url, None

        except Exception as e:
            return self.handle_error(500, str(e))

    def download_image(self, url):
        """
        Download an image from the given URL.

        Args:
            url (str): The URL to download the image from

        Returns:
            bytes: The binary image data or None if error
        """
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return response.content
            return None
        except Exception:
            return None

    def handle_error(self, status_code, message=None):
        """
        Handle error responses.

        Args:
            status_code (int): The HTTP status code
            message (str, optional): Custom error message

        Returns:
            tuple: (None, None, error_message)
        """
        error_messages = {
            404: f"User not found on {self.name}",
            400: f"Invalid parameters for {self.name}",
            429: f"Rate limited by {self.name}",
            503: f"{self.name} service is unavailable",
            500: f"Internal server error while accessing {self.name}",
        }

        error_message = message or error_messages.get(status_code, f"Error accessing {self.name}")
        return None, None, error_message

    def get_html_avatar(self, url, meta_property=None, css_selector=None, headers=None):
        """
        Get avatar URL from HTML page using meta tags or CSS selectors.

        Args:
            url (str): The URL to fetch
            meta_property (str, optional): Meta property to look for (e.g., "og:image")
            css_selector (str, optional): CSS selector for the image element
            headers (dict, optional): Custom headers to use

        Returns:
            str: The avatar URL or None
        """
        soup, _ = get_html(url, headers, self.timeout)

        if not soup:
            return None

        # Try meta tag first if specified
        if meta_property:
            avatar_url = get_meta_content(soup, meta_property)
            if avatar_url:
                return avatar_url

        # Try CSS selector if specified
        if css_selector:
            avatar_url = get_image_from_selector(soup, css_selector)
            if avatar_url:
                return avatar_url

        return None

    @staticmethod
    def md5(text):
        """
        Generate MD5 hash of the given text.

        Args:
            text (str): The text to hash

        Returns:
            str: The MD5 hash
        """
        return hashlib.md5(text.encode("utf-8").strip().lower()).hexdigest()

    @staticmethod
    def is_valid_url(url):
        """
        Check if the given URL is valid.

        Args:
            url (str): The URL to check

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
