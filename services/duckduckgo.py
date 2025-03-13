from services.avatar_provider import AvatarProvider


class DuckDuckGoService(AvatarProvider):
    """
    Service adapter for DuckDuckGo Favicons.
    """

    def get_avatar_url(self, domain):
        """
        Get the favicon URL for the given domain using DuckDuckGo's favicon service.

        Args:
            domain (str): The domain to get the favicon for

        Returns:
            str: The favicon URL
        """
        try:
            return f"https://icons.duckduckgo.com/ip3/{domain}.ico"
        except Exception:
            return None
