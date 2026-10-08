import pytest

from app.domain.models import Track
from app.infrastructure.music.cached_music_client import CachedMusicClient
from app.infrastructure.music.memory_music_cache import InMemoryMusicCache


class CountingDelegate:
    def __init__(self) -> None:
        self.calls = 0

    async def search_track(self, query: str) -> Track:
        self.calls += 1
        return Track(title=query, artist="Artist")


@pytest.mark.asyncio
async def test_cache_avoids_duplicate_delegate_calls():
    delegate = CountingDelegate()
    cached = CachedMusicClient(delegate=delegate, cache=InMemoryMusicCache())

    await cached.search_track("Here Comes The Sun")
    await cached.search_track("Here Comes The Sun")

    assert delegate.calls == 1
