from urllib.parse import urlencode

from services.avatar_provider import AvatarProvider


class GoogleService(AvatarProvider):
    """
    Service adapter for Google Favicons.
    """

    def get_avatar_url(self, domain):
        """
        Get the favicon URL for the given domain using Google's favicon service.

        Args:
            domain (str): The domain to get the favicon for

        Returns:
            str: The favicon URL
        """
        try:
            params = {
                "domain_url": domain,
                "sz": "128",
            }
            return f"https://www.google.com/s2/favicons?{urlencode(params)}"
        except Exception:
            return None
