import logging

import pytest

from app.domain.models import (
    DayOfWeek,
    NotificationChannel,
    Track,
    UserWakeProfile,
    WeatherType,
)
from app.infrastructure.notifications.adapters import (
    EmailNotificationAdapter,
    EmergencyConsoleAdapter,
    PushNotificationAdapter,
    SmsNotificationAdapter,
)
from app.infrastructure.notifications.mocks import EmailMock, PushMock, SmsMock
from app.infrastructure.notifications.resilient_sender import ResilientNotificationSender


def sample_profile(channel: NotificationChannel) -> UserWakeProfile:
    return UserWakeProfile(
        user_id="u1",
        tracks_by_day_and_weather={
            (DayOfWeek.MONDAY, WeatherType.SOLEIL): "Wake Up",
        },
        fallback_track_query="Wake Up",
        preferred_channel=channel,
        email="u@example.com",
        phone="+33600000000",
        device_token="tok",
    )


@pytest.mark.asyncio
async def test_resilient_uses_preferred_channel():
    sender = ResilientNotificationSender(
        notifiers=[
            EmailNotificationAdapter(EmailMock()),
            SmsNotificationAdapter(SmsMock()),
            PushNotificationAdapter(PushMock()),
        ],
        fallback_order=[
            NotificationChannel.PUSH,
            NotificationChannel.EMAIL,
            NotificationChannel.SMS,
        ],
        emergency=EmergencyConsoleAdapter(),
    )
    profile = sample_profile(NotificationChannel.EMAIL)
    delivery = await sender.deliver(
        profile, "hello", Track(title="T", artist="A")
    )
    assert delivery.channel == NotificationChannel.EMAIL
    assert delivery.degraded is False


@pytest.mark.asyncio
async def test_resilient_falls_back_when_preferred_fails():
    sender = ResilientNotificationSender(
        notifiers=[
            EmailNotificationAdapter(EmailMock()),
            SmsNotificationAdapter(SmsMock()),
            PushNotificationAdapter(PushMock(fail=True)),
        ],
        fallback_order=[
            NotificationChannel.PUSH,
            NotificationChannel.EMAIL,
            NotificationChannel.SMS,
        ],
        emergency=EmergencyConsoleAdapter(),
    )
    profile = sample_profile(NotificationChannel.PUSH)
    delivery = await sender.deliver(
        profile, "hello", Track(title="T", artist="A")
    )
    assert delivery.channel == NotificationChannel.EMAIL
    assert delivery.degraded is True


@pytest.mark.asyncio
async def test_resilient_emergency_when_all_fail(caplog: pytest.LogCaptureFixture):
    caplog.set_level(logging.WARNING)
    emergency = EmergencyConsoleAdapter()
    sender = ResilientNotificationSender(
        notifiers=[
            EmailNotificationAdapter(EmailMock(fail=True)),
            SmsNotificationAdapter(SmsMock(fail=True)),
            PushNotificationAdapter(PushMock(fail=True)),
        ],
        fallback_order=[
            NotificationChannel.PUSH,
            NotificationChannel.EMAIL,
            NotificationChannel.SMS,
        ],
        emergency=emergency,
    )
    profile = sample_profile(NotificationChannel.PUSH)
    delivery = await sender.deliver(
        profile, "hello", Track(title="T", artist="A")
    )
    assert delivery.channel == NotificationChannel.EMERGENCY
    assert delivery.delivered is True
    assert any("[EMERGENCY]" in record.message for record in caplog.records)
