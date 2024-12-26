from aioboto3 import Session

from settings import S3_SETTINGS
from shared.meta_ import Singleton


class S3Client(Session, metaclass=Singleton):
    """S3 клиент для работы с хранилищем."""

    @property
    def _client(self):
        """Получение клиента S3."""
        return self.client("s3", endpoint_url=S3_SETTINGS.url)

    async def __aenter__(self):
        return await self._client.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.__aexit__(exc_type, exc_val, exc_tb)


s3_client = S3Client(
    aws_access_key_id=S3_SETTINGS.access_key,
    aws_secret_access_key=S3_SETTINGS.secret_key,
    region_name=S3_SETTINGS.region,
)
