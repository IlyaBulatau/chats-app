from asyncio import run
import logging

from infrastructure.storages.s3 import s3_client
from settings import S3_SETTINGS


logger = logging.getLogger("uvicorn")


async def init_bucket() -> None:
    try:
        async with s3_client.client(service_name="s3", endpoint_url=S3_SETTINGS.url) as client:
            await client.create_bucket(Bucket=S3_SETTINGS.bucket)
            logger.info(f"Bucket {S3_SETTINGS.bucket} created")
    except client.exceptions.BucketAlreadyOwnedByYou:
        logger.error(f"Bucket {S3_SETTINGS.bucket} already exists")


if __name__ == "__main__":
    run(init_bucket())
