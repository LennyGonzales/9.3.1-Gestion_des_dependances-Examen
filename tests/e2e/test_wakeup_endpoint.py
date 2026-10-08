import pytest


@pytest.mark.asyncio
async def test_wakeup_trigger_demo_mode(client):
    response = await client.post(
        "/wakeup/trigger?demo=true",
        json={
            "userId": "user-soleil",
            "dayOfWeek": "MONDAY",
            "weather": "SOLEIL",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["userId"] == "user-soleil"
    assert body["musicSource"] == "demo"
    assert body["notification"]["delivered"] is True


@pytest.mark.asyncio
async def test_wakeup_trigger_unknown_user_returns_404(client):
    response = await client.post(
        "/wakeup/trigger?demo=true",
        json={
            "userId": "missing",
            "dayOfWeek": "MONDAY",
            "weather": "SOLEIL",
        },
    )
    assert response.status_code == 404
