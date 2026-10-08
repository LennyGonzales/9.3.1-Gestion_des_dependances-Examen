from app.domain.models import Track


class LocalFallbackMusicProvider:
    _CATALOG: dict[str, Track] = {
        "here comes the sun": Track(
            title="Here Comes The Sun",
            artist="The Beatles",
            listen_url=None,
        ),
        "singin' in the rain": Track(
            title="Singin' in the Rain",
            artist="Gene Kelly",
            listen_url=None,
        ),
        "let it snow": Track(
            title="Let It Snow",
            artist="Dean Martin",
            listen_url=None,
        ),
        "cloudy day": Track(
            title="Both Sides Now",
            artist="Joni Mitchell",
            listen_url=None,
        ),
        "wake up": Track(
            title="Wake Up",
            artist="Arcade Fire",
            listen_url=None,
        ),
    }

    async def lookup(self, query: str) -> Track | None:
        key = query.casefold().strip()
        if key in self._CATALOG:
            return self._CATALOG[key]
        for catalog_key, track in self._CATALOG.items():
            if catalog_key in key or key in catalog_key:
                return track
        return None

    async def minimal_track(self, query: str) -> Track:
        return Track(title=query, artist="Inconnu", listen_url=None)
