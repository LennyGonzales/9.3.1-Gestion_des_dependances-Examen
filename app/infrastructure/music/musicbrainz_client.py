import httpx

from app.domain.exceptions import ExternalServiceError, TrackNotFoundError
from app.domain.models import Track


class MusicBrainzMusicClient:
    def __init__(
        self, http: httpx.AsyncClient, base_url: str, user_agent: str
    ) -> None:
        self._http = http
        self._base_url = base_url.rstrip("/")
        self._headers = {
            "User-Agent": user_agent,
            "Accept": "application/json",
        }

    async def search_track(self, query: str) -> Track:
        try:
            response = await self._http.get(
                f"{self._base_url}/recording",
                params={"query": query, "fmt": "json", "limit": 5},
                headers=self._headers,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalServiceError("MusicBrainz", str(exc)) from exc

        recordings = response.json().get("recordings", [])
        if not recordings:
            raise TrackNotFoundError(query)

        recording = recordings[0]
        artist = "Unknown"
        credits = recording.get("artist-credit", [])
        if credits:
            artist = credits[0].get("name", artist)

        return Track(
            title=str(recording.get("title", query)),
            artist=artist,
            listen_url=None,
        )
