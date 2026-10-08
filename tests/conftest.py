import pytest
from httpx import ASGITransport, AsyncClient

from app.domain.exceptions import NotificationError, TrackNotFoundError
from app.domain.models import (
    DayOfWeek,
    NotificationChannel,
    NotificationDelivery,
    ResolvedTrack,
    Track,
    UserWakeProfile,
    WeatherType,
)
from app.main import app, lifespan
from app.services.wakeup_service import WakeupService


class FakeProfiles:
    def __init__(self, profile: UserWakeProfile | None = None) -> None:
        self._profile = profile or UserWakeProfile(
            user_id="user-test",
            tracks_by_weather={WeatherType.SOLEIL: "Here Comes The Sun"},
            fallback_track_query="Wake Up",
            preferred_channel=NotificationChannel.PUSH,
            email="test@example.com",
            phone="+33600000099",
            device_token="token-test",
        )

    async def get_profile(self, user_id: str) -> UserWakeProfile:
        return self._profile


class FakeMusicResolver:
    def __init__(
        self,
        track: Track | None = None,
        fail: bool = False,
        music_source: str = "fake",
    ) -> None:
        self._track = track or Track(
            title="Here Comes The Sun", artist="The Beatles", listen_url="https://x"
        )
        self.fail = fail
        self._music_source = music_source

    async def resolve(self, query: str) -> ResolvedTrack:
        if self.fail:
            raise TrackNotFoundError(query)
        return ResolvedTrack(
            track=self._track, music_source=self._music_source, degraded=False
        )


class FailingMusicResolver:
    async def resolve(self, query: str) -> ResolvedTrack:
        return ResolvedTrack(
            track=Track(title=query, artist="Inconnu"),
            music_source="minimal",
            degraded=True,
        )


class FakeNotifier:
    def __init__(
        self,
        channel: NotificationChannel = NotificationChannel.PUSH,
        fail: bool = False,
    ) -> None:
        self.channel = channel
        self.fail = fail
        self.messages: list[str] = []

    async def deliver(self, profile, message: str, track: Track) -> NotificationDelivery:
        if self.fail:
            raise NotificationError("push", "down")
        self.messages.append(message)
        return NotificationDelivery(
            channel=self.channel,
            preferred_channel=profile.preferred_channel,
            delivered=True,
            degraded=False,
        )


@pytest.fixture
def fake_wakeup_service() -> WakeupService:
    return WakeupService(
        profiles=FakeProfiles(),
        music_resolver=FakeMusicResolver(),
        demo_music_resolver=FakeMusicResolver(
            Track(title="Demo", artist="Demo Artist"),
            music_source="demo",
        ),
        notifier=FakeNotifier(),
    )


@pytest.fixture
async def client() -> AsyncClient:
    async with lifespan(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
