from services.avatar_provider import AvatarProvider


class GithubService(AvatarProvider):
    """
    Service adapter for GitHub.
    """

    def get_avatar_url(self, username):
        """
        Get the GitHub avatar URL for the given username.

        Args:
            username (str): The GitHub username

        Returns:
            str: The avatar URL or None if not found
        """
        try:
            return f"https://github.com/{username}.png"
        except Exception:
            return None
