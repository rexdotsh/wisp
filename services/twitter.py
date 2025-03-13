import requests
from bs4 import BeautifulSoup

from services.avatar_provider import AvatarProvider
from utils.html import get_meta_content


class TwitterService(AvatarProvider):
    """
    Service adapter for Twitter/X.
    """

    def get_avatar_url(self, username):
        """
        Get the Twitter avatar URL for the given username.

        Args:
            username (str): The Twitter username

        Returns:
            str: The avatar URL or None if not found
        """
        try:
            url = f"https://x.com/{username}"

            # use slackbot user agent
            headers = {"User-Agent": "Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)"}

            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                avatar_url = get_meta_content(soup, "og:image")

                # get larger image if available
                if avatar_url and avatar_url.endswith("_200x200.jpg"):
                    avatar_url = avatar_url.replace("_200x200.jpg", "_400x400.jpg")

                return avatar_url

            return None
        except Exception:
            return None
