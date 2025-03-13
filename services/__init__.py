from services.deviantart import DeviantArtService
from services.duckduckgo import DuckDuckGoService
from services.github import GithubService
from services.google import GoogleService
from services.gravatar import GravatarService
from services.instagram import InstagramService
from services.reddit import RedditService
from services.twitter import TwitterService
from services.youtube import YouTubeService


def get_service(service_name=None):
    """
    Get the service adapter for the given service name.
    If service_name is None, return a dictionary of all services.
    """
    services = {
        "github": GithubService(),
        "twitter": TwitterService(),
        "instagram": InstagramService(),
        "reddit": RedditService(),
        "youtube": YouTubeService(),
        "deviantart": DeviantArtService(),
        "google": GoogleService(),
        "duckduckgo": DuckDuckGoService(),
        "gravatar": GravatarService(),
    }

    if service_name is None:
        return services

    return services.get(service_name.lower())
