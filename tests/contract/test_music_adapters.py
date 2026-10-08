import httpx
import pytest
import respx

from app.domain.models import Track
from app.infrastructure.itunes_client import ItunesMusicClient
from app.infrastructure.musicbrainz_client import MusicBrainzMusicClient
from tests.constants import TEST_USER_AGENT


@pytest.mark.asyncio
@respx.mock
async def test_itunes_adapter_returns_domain_track():
    respx.get("https://itunes.apple.com/search").respond(
        json={
            "results": [
                {
                    "trackName": "Here Comes The Sun",
                    "artistName": "The Beatles",
                    "trackViewUrl": "https://music.apple.com/track/1",
                }
            ]
        }
    )
    async with httpx.AsyncClient() as http:
        track = await ItunesMusicClient(
            http=http, base_url="https://itunes.apple.com"
        ).search_track("Here Comes The Sun")

    assert isinstance(track, Track)
    assert track.title == "Here Comes The Sun"
    assert track.listen_url == "https://music.apple.com/track/1"
    assert "trackViewUrl" not in track.__dict__


@pytest.mark.asyncio
@respx.mock
async def test_musicbrainz_adapter_returns_domain_track():
    respx.get("https://musicbrainz.org/ws/2/recording").respond(
        json={
            "recordings": [
                {
                    "title": "Here Comes The Sun",
                    "artist-credit": [{"name": "The Beatles"}],
                }
            ]
        }
    )
    async with httpx.AsyncClient() as http:
        track = await MusicBrainzMusicClient(
            http=http,
            base_url="https://musicbrainz.org/ws/2",
            user_agent=TEST_USER_AGENT,
        ).search_track("Here Comes The Sun")

    assert isinstance(track, Track)
    assert track.artist == "The Beatles"
