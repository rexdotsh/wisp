from abc import ABC, abstractmethod

import requests


class BaseService(ABC):
    """
    Base class for all service adapters.
    """

    def __init__(self):
        self.name = self.__class__.__name__.replace("Service", "").lower()

    @abstractmethod
    def get_profile_picture(self, username):
        """
        Get the profile picture for the given username.

        Args:
            username (str): The username to get the profile picture for.

        Returns:
            tuple: (image_data, image_url, error)
                - image_data: The binary image data or None if error
                - image_url: The URL of the image or None if error
                - error: Error message or None if success
        """
        pass

    def download_image(self, url):
        """
        Download an image from the given URL.

        Args:
            url (str): The URL to download the image from.

        Returns:
            bytes: The binary image data or None if error.
        """
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.content
            return None
        except Exception:
            return None

    def handle_error(self, status_code, message=None):
        """
        Handle error responses.

        Args:
            status_code (int): The HTTP status code.
            message (str, optional): Custom error message.

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
