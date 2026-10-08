import httpx

from app.domain.exceptions import ExternalServiceError, TrackNotFoundError
from app.domain.models import Track


class ItunesMusicClient:
    def __init__(self, http: httpx.AsyncClient, base_url: str) -> None:
        self._http = http
        self._base_url = base_url.rstrip("/")

    async def search_track(self, query: str) -> Track:
        try:
            response = await self._http.get(
                f"{self._base_url}/search",
                params={"term": query, "media": "music", "limit": 5},
            )
            if response.status_code == 429:
                raise ExternalServiceError("iTunes", "rate_limited")
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalServiceError("iTunes", str(exc)) from exc

        results = response.json().get("results", [])
        if not results:
            raise TrackNotFoundError(query)

        first = results[0]
        return Track(
            title=str(first.get("trackName", query)),
            artist=str(first.get("artistName", "Unknown")),
            listen_url=first.get("trackViewUrl"),
        )
