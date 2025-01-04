from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse


async def http_unauthorized_api_handler(request: Request, *args, **kwargs):  # noqa: ARG001
    return JSONResponse(
        content=None,
        status_code=status.HTTP_401_UNAUTHORIZED,
    )
