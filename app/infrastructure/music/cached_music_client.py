from app.domain.models import Track
from app.domain.ports import MusicCachePort, MusicSearchPort


class CachedMusicClient:
    def __init__(self, delegate: MusicSearchPort, cache: MusicCachePort) -> None:
        self._delegate = delegate
        self._cache = cache

    async def search_track(self, query: str) -> Track:
        cached = await self._cache.get(query)
        if cached is not None:
            return cached

        track = await self._delegate.search_track(query)
        await self._cache.set(query, track)
        return track
