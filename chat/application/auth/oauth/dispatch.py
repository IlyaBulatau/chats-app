from application.auth.oauth.constants import Providers
from application.auth.oauth.providers import GoogleOAuthProvider
from application.auth.oauth.providers.base import Provider


def get_oauth_provider(name: str) -> Provider:
    """Получить провайдера приложения для авторизации.

    :param str name: Имя провайдера

    :return `Provider`: Обьект провайдера.
    """
    providers = {Providers.GOOGLE.value: GoogleOAuthProvider}

    return providers[name]
