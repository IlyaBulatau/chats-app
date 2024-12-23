from infrastructure.storages.client import s3_client
from settings import S3_SETTINGS


class FileStorage:
    _client = s3_client
    _bucket = S3_SETTINGS.bucket

    async def upload(self, file: bytes, path: str, **options) -> None:
        """Загрузить файл в S3 хранилище.

        :param `bytes` file: Файл для загрузки.

        :param: `str` path: Путь к загружаемому файлу.

        :param: `dict` options: Дополнительные параметры загрузки.
        """
        async with self._client.client(service_name="s3", endpoint_url=S3_SETTINGS.url) as client:
            await client.put_object(Body=file, Bucket=self._bucket, Key=path, **options)
