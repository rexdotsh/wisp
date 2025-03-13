from services.avatar_provider import AvatarProvider


class InstagramService(AvatarProvider):
    """
    Service adapter for Instagram.
    """

    def get_avatar_url(self, username):
        """
        Get the Instagram avatar URL for the given username.

        Args:
            username (str): The Instagram username

        Returns:
            str: The avatar URL or None if not found
        """
        try:
            return self.get_html_avatar(f"https://www.instagram.com/{username}/", meta_property="og:image")
        except Exception:
            return None
