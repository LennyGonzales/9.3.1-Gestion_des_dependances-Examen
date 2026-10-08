import pytest

from app.domain.exceptions import UserNotFoundError
from app.domain.models import (
    DayOfWeek,
    NotificationChannel,
    NotificationDelivery,
    ResolvedTrack,
    Track,
    UserWakeProfile,
    WeatherType,
)
from app.services.wakeup_service import WakeupService
from tests.conftest import FakeMusicResolver, FakeNotifier, FakeProfiles


class MissingProfile:
    async def get_profile(self, user_id: str) -> UserWakeProfile:
        raise UserNotFoundError(user_id)


class DegradedMusicResolver:
    async def resolve(self, query: str) -> ResolvedTrack:
        return ResolvedTrack(
            track=Track(title="Local", artist="Artist"),
            music_source="local",
            degraded=True,
        )


class DegradedNotifier:
    async def deliver(self, profile, message: str, track: Track) -> NotificationDelivery:
        return NotificationDelivery(
            channel=NotificationChannel.EMAIL,
            preferred_channel=profile.preferred_channel,
            delivered=True,
            degraded=True,
        )


def make_service(**kwargs) -> WakeupService:
    defaults = {
        "profiles": FakeProfiles(),
        "music_resolver": FakeMusicResolver(),
        "demo_music_resolver": FakeMusicResolver(
            Track(title="Demo Song", artist="Demo Artist"),
            music_source="demo",
        ),
        "notifier": FakeNotifier(),
    }
    defaults.update(kwargs)
    return WakeupService(**defaults)


@pytest.mark.asyncio
async def test_trigger_wakeup_success():
    service = make_service()
    result = await service.trigger_wakeup(
        "user-test", DayOfWeek.MONDAY, WeatherType.SOLEIL
    )

    assert result.track.title == "Here Comes The Sun"
    assert result.notification.delivered is True
    assert result.degraded is False


@pytest.mark.asyncio
async def test_trigger_wakeup_demo_mode():
    service = make_service()
    result = await service.trigger_wakeup(
        "user-test", DayOfWeek.FRIDAY, WeatherType.PLUIE, demo=True
    )

    assert result.music_source == "demo"
    assert result.track.artist == "Demo Artist"


@pytest.mark.asyncio
async def test_trigger_wakeup_user_not_found():
    service = make_service(profiles=MissingProfile())

    with pytest.raises(UserNotFoundError):
        await service.trigger_wakeup(
            "unknown", DayOfWeek.MONDAY, WeatherType.SOLEIL
        )


@pytest.mark.asyncio
async def test_trigger_wakeup_marked_degraded():
    service = make_service(
        music_resolver=DegradedMusicResolver(),
        notifier=DegradedNotifier(),
    )
    result = await service.trigger_wakeup(
        "user-test", DayOfWeek.TUESDAY, WeatherType.NEIGE
    )
    assert result.degraded is True
    assert result.music_source == "local"
