from services.avatar_provider import AvatarProvider


class GravatarService(AvatarProvider):
    """
    Service adapter for Gravatar.
    """

    def get_avatar_url(self, email):
        """
        Get the Gravatar avatar URL for the given email.

        Args:
            email (str): The email address

        Returns:
            str: The avatar URL or None if not found
        """
        try:
            email_hash = self.md5(email.strip().lower())
            return f"https://gravatar.com/avatar/{email_hash}?d=404"
        except Exception:
            return None
