import httpx

from app.config import Settings


def create_http_client(settings: Settings) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=settings.http_timeout,
        headers={"User-Agent": settings.app_user_agent},
    )
