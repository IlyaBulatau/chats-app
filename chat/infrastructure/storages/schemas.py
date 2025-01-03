from datetime import datetime
from typing import TypedDict


class StorageObjectInfoResponse(TypedDict):
    ResponseMetadata: dict
    LastModified: datetime
    ContentLength: int
    ETag: str
    CacheControl: str
    ContentType: str
    Metadata: dict
