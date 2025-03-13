from services.avatar_provider import AvatarProvider


class YouTubeService(AvatarProvider):
    """
    Service adapter for YouTube.
    """

    def get_avatar_url(self, username):
        """
        Get the YouTube avatar URL for the given username.

        Args:
            username (str): The YouTube username

        Returns:
            str: The avatar URL or None if not found
        """
        try:
            return self.get_html_avatar(f"https://www.youtube.com/@{username}", meta_property="og:image")
        except Exception:
            return None
