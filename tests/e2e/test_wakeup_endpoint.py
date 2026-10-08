import pytest
import respx
from httpx import AsyncClient

from tests.constants import ITUNES_TEST_BASE_URL, MUSICBRAINZ_TEST_BASE_URL
from tests.e2e.helpers import assert_wakeup_response_shape

TRIGGER_PATH = "/wakeup/trigger"

SOLEIL_BODY = {
    "userId": "user-soleil",
    "dayOfWeek": "MONDAY",
    "weather": "SOLEIL",
}


@pytest.mark.asyncio
async def test_wakeup_trigger_demo_mode(client: AsyncClient):
    response = await client.post(f"{TRIGGER_PATH}?demo=true", json=SOLEIL_BODY)
    assert response.status_code == 200
    body = response.json()
    assert_wakeup_response_shape(body)
    assert body["userId"] == "user-soleil"
    assert body["musicSource"] == "demo"
    assert body["notification"]["delivered"] is True
    assert body["notification"]["channel"] == "push"


@pytest.mark.asyncio
async def test_wakeup_trigger_unknown_user_returns_404(client: AsyncClient):
    response = await client.post(
        f"{TRIGGER_PATH}?demo=true",
        json={
            "userId": "missing",
            "dayOfWeek": "MONDAY",
            "weather": "SOLEIL",
        },
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_wakeup_trigger_invalid_weather_returns_422(client: AsyncClient):
    response = await client.post(
        f"{TRIGGER_PATH}?demo=true",
        json={
            "userId": "user-soleil",
            "dayOfWeek": "MONDAY",
            "weather": "ORAGE",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_wakeup_track_depends_on_day_and_weather_in_demo(client: AsyncClient):
    monday = await client.post(
        f"{TRIGGER_PATH}?demo=true",
        json={**SOLEIL_BODY, "dayOfWeek": "MONDAY"},
    )
    saturday = await client.post(
        f"{TRIGGER_PATH}?demo=true",
        json={**SOLEIL_BODY, "dayOfWeek": "SATURDAY"},
    )
    assert monday.status_code == 200
    assert saturday.status_code == 200
    assert monday.json()["track"]["title"] == "Here Comes The Sun"
    assert saturday.json()["track"]["title"] == "Walking on Sunshine"


@pytest.mark.asyncio
async def test_wakeup_preferred_notification_channel_from_profile(client: AsyncClient):
    pluie = await client.post(
        f"{TRIGGER_PATH}?demo=true",
        json={
            "userId": "user-pluie",
            "dayOfWeek": "TUESDAY",
            "weather": "PLUIE",
        },
    )
    sms = await client.post(
        f"{TRIGGER_PATH}?demo=true",
        json={
            "userId": "user-sms",
            "dayOfWeek": "WEDNESDAY",
            "weather": "SOLEIL",
        },
    )
    assert pluie.json()["notification"]["channel"] == "email"
    assert pluie.json()["notification"]["preferredChannel"] == "email"
    assert sms.json()["notification"]["channel"] == "sms"
    assert sms.json()["notification"]["preferredChannel"] == "sms"


@pytest.mark.asyncio
@respx.mock
async def test_wakeup_demo_mode_does_not_call_itunes(client: AsyncClient):
    itunes_route = respx.get(f"{ITUNES_TEST_BASE_URL}/search").respond(json={})

    response = await client.post(f"{TRIGGER_PATH}?demo=true", json=SOLEIL_BODY)

    assert response.status_code == 200
    assert itunes_route.call_count == 0


@pytest.mark.asyncio
@respx.mock
async def test_wakeup_without_demo_calls_itunes(client: AsyncClient):
    respx.get(f"{ITUNES_TEST_BASE_URL}/search").respond(
        json={
            "results": [
                {
                    "trackName": "Here Comes the Sun",
                    "artistName": "The Beatles",
                    "trackViewUrl": "https://music.apple.com/track/1",
                }
            ]
        }
    )

    response = await client.post(TRIGGER_PATH, json=SOLEIL_BODY)

    assert response.status_code == 200
    body = response.json()
    assert_wakeup_response_shape(body)
    assert body["musicSource"] == "itunes"
    assert body["track"]["title"] == "Here Comes the Sun"
    assert body["track"]["listenUrl"] == "https://music.apple.com/track/1"


@pytest.mark.asyncio
@respx.mock
async def test_wakeup_falls_back_to_local_when_apis_fail(client: AsyncClient):
    respx.get(f"{ITUNES_TEST_BASE_URL}/search").respond(status_code=503)
    respx.get(f"{MUSICBRAINZ_TEST_BASE_URL}/recording").respond(status_code=503)
    # Requête distincte de test_wakeup_without_demo_calls_itunes (cache singleton partagé).
    payload = {
        "userId": "user-pluie",
        "dayOfWeek": "TUESDAY",
        "weather": "PLUIE",
    }

    response = await client.post(TRIGGER_PATH, json=payload)

    assert response.status_code == 200
    body = response.json()
    assert_wakeup_response_shape(body)
    assert body["musicSource"] == "local"
    assert body["degraded"] is True
    assert body["track"]["title"] == "Singin' in the Rain"
