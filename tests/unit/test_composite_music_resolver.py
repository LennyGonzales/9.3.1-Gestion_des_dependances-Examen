import pytest

from app.domain.exceptions import ExternalServiceError, TrackNotFoundError
from app.domain.models import Track
from app.infrastructure.music.composite_music_resolver import CompositeMusicResolver
from app.infrastructure.music.local_fallback_music import LocalFallbackMusicProvider


class StubMusic:
    def __init__(self, track: Track | None = None, error: Exception | None = None) -> None:
        self._track = track
        self._error = error

    async def search_track(self, query: str) -> Track:
        if self._error:
            raise self._error
        assert self._track is not None
        return self._track


@pytest.mark.asyncio
async def test_composite_uses_primary_when_available():
    resolver = CompositeMusicResolver(
        primary=StubMusic(Track(title="A", artist="B")),
        secondary=StubMusic(Track(title="C", artist="D")),
        local_fallback=LocalFallbackMusicProvider(),
        primary_source="itunes",
        secondary_source="musicbrainz",
    )
    result = await resolver.resolve("query")
    assert result.music_source == "itunes"
    assert result.degraded is False


@pytest.mark.asyncio
async def test_composite_falls_back_to_secondary():
    resolver = CompositeMusicResolver(
        primary=StubMusic(error=ExternalServiceError("iTunes", "down")),
        secondary=StubMusic(Track(title="MB", artist="Artist")),
        local_fallback=LocalFallbackMusicProvider(),
        primary_source="itunes",
        secondary_source="musicbrainz",
    )
    result = await resolver.resolve("query")
    assert result.music_source == "musicbrainz"


@pytest.mark.asyncio
async def test_composite_uses_local_then_minimal():
    resolver = CompositeMusicResolver(
        primary=StubMusic(error=TrackNotFoundError("q")),
        secondary=StubMusic(error=TrackNotFoundError("q")),
        local_fallback=LocalFallbackMusicProvider(),
        primary_source="itunes",
        secondary_source="musicbrainz",
    )
    result = await resolver.resolve("Here Comes The Sun")
    assert result.music_source == "local"

    minimal = await resolver.resolve("totally unknown song xyz")
    assert minimal.music_source == "minimal"
    assert minimal.track.artist == "Inconnu"
