import httpx
import pytest
import respx

from app.domain.exceptions import ExternalServiceError
from app.domain.models import Track
from app.infrastructure.itunes_client import ItunesMusicClient
from app.infrastructure.musicbrainz_client import MusicBrainzMusicClient
from tests.constants import (
    ITUNES_TEST_BASE_URL,
    MUSICBRAINZ_TEST_BASE_URL,
    TEST_USER_AGENT,
)


@pytest.mark.asyncio
@respx.mock
async def test_itunes_adapter_returns_domain_track():
    respx.get(f"{ITUNES_TEST_BASE_URL}/search").respond(
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
            http=http, base_url=ITUNES_TEST_BASE_URL
        ).search_track("Here Comes The Sun")

    assert isinstance(track, Track)
    assert track.title == "Here Comes The Sun"
    assert track.listen_url == "https://music.apple.com/track/1"
    assert "trackViewUrl" not in track.__dict__


@pytest.mark.asyncio
@respx.mock
async def test_itunes_adapter_raises_on_rate_limit():
    respx.get(f"{ITUNES_TEST_BASE_URL}/search").respond(status_code=429)
    async with httpx.AsyncClient() as http:
        client = ItunesMusicClient(http=http, base_url=ITUNES_TEST_BASE_URL)
        with pytest.raises(ExternalServiceError, match="rate_limited"):
            await client.search_track("Here Comes The Sun")


@pytest.mark.asyncio
@respx.mock
async def test_musicbrainz_adapter_returns_domain_track():
    respx.get(f"{MUSICBRAINZ_TEST_BASE_URL}/recording").respond(
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
            base_url=MUSICBRAINZ_TEST_BASE_URL,
            user_agent=TEST_USER_AGENT,
        ).search_track("Here Comes The Sun")

    assert isinstance(track, Track)
    assert track.artist == "The Beatles"
