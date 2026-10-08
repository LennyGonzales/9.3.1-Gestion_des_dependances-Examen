from app.domain.exceptions import ExternalServiceError, TrackNotFoundError
from app.domain.models import ResolvedTrack, Track
from app.domain.ports import LocalMusicFallbackPort, MusicSearchPort


class CompositeMusicResolver:
    def __init__(
        self,
        primary: MusicSearchPort,
        secondary: MusicSearchPort,
        local_fallback: LocalMusicFallbackPort,
        primary_source: str,
        secondary_source: str,
    ) -> None:
        self._primary = primary
        self._secondary = secondary
        self._local_fallback = local_fallback
        self._primary_source = primary_source
        self._secondary_source = secondary_source

    async def resolve(self, query: str) -> ResolvedTrack:
        for source, client in (
            (self._primary_source, self._primary),
            (self._secondary_source, self._secondary),
        ):
            try:
                track = await client.search_track(query)
                return ResolvedTrack(track=track, music_source=source, degraded=False)
            except (ExternalServiceError, TrackNotFoundError):
                continue

        local = await self._local_fallback.lookup(query)
        if local is not None:
            return ResolvedTrack(track=local, music_source="local", degraded=True)

        minimal = await self._local_fallback.minimal_track(query)
        return ResolvedTrack(track=minimal, music_source="minimal", degraded=True)


class DemoMusicResolver:
    async def resolve(self, query: str) -> ResolvedTrack:
        return ResolvedTrack(
            track=Track(title=query, artist="Demo Artist", listen_url=None),
            music_source="demo",
            degraded=False,
        )
