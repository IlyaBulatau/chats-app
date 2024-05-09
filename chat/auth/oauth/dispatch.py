from auth.oauth.constants import Providers
from auth.oauth.providers import BaseOAuthProdiver, GoogleOAuthProvider


def get_oauth_provider(name: str) -> BaseOAuthProdiver:
    providers = {Providers.GOOGLE.value: GoogleOAuthProvider}

    return providers[name]
