from auth.oauth.constants import Providers
from auth.oauth.providers import GoogleOAuthProvider
from auth.oauth.providers.base import Provider


def get_oauth_provider(name: str) -> Provider:
    providers = {Providers.GOOGLE.value: GoogleOAuthProvider}

    return providers[name]
