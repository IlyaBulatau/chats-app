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

    async def get_object_url(self, path: str, expiration: int = 3600) -> str:
        """Получить ссылку на файл в S3 хранилище.

        :param `str` path: Путь к файлу.

        :param `int` expiration: Время жизни ссылки в секундах.

        :return `str`: Полная ссылка на файл в S3 хранилище.
        """
        async with self._client.client(service_name="s3", endpoint_url=S3_SETTINGS.url) as client:
            return await client.generate_presigned_url(
                "get_object", Params={"Key": path, "Bucket": self._bucket}, ExpiresIn=expiration
            )

    async def delete_object(self, path: str) -> None:
        """Удалить файл из S3 хранилища.

        :param `str` path: Путь к файлу.
        """
        async with self._client.client(service_name="s3", endpoint_url=S3_SETTINGS.url) as client:
            await client.delete_object(Bucket=self._bucket, Key=path)

    async def get_object_info(self, path: str) -> dict:
        """Получить информацию о файле в S3 хранилище.

        :param `str` path: Путь к файлу.

        :return `dict`: Информация о файле.
        """
        async with self._client.client(service_name="s3", endpoint_url=S3_SETTINGS.url) as client:
            return await client.head_object(Bucket=self._bucket, Key=path)
