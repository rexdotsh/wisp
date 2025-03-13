from services.avatar_provider import AvatarProvider


class DeviantArtService(AvatarProvider):
    """
    Service adapter for DeviantArt.
    """

    def get_avatar_url(self, username):
        """
        Get the DeviantArt avatar URL for the given username.

        Args:
            username (str): The DeviantArt username

        Returns:
            str: The avatar URL or None if not found
        """
        try:
            return self.get_html_avatar(f"https://www.deviantart.com/{username}", meta_property="og:image")
        except Exception:
            return None
