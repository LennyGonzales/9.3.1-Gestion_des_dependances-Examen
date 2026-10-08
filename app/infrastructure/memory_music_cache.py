from app.domain.models import Track
from app.domain.ports import MusicCachePort


class InMemoryMusicCache(MusicCachePort):
    def __init__(self) -> None:
        self._store: dict[str, Track] = {}

    async def get(self, query: str) -> Track | None:
        return self._store.get(query.casefold())

    async def set(self, query: str, track: Track) -> None:
        self._store[query.casefold()] = track
