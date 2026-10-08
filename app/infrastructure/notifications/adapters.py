import logging

from app.domain.exceptions import NotificationError
from app.domain.models import NotificationChannel, Track, UserWakeProfile
from app.infrastructure.notifications.mocks import EmailMock, PushMock, SmsMock

logger = logging.getLogger(__name__)


class EmailNotificationAdapter:
    def __init__(self, email_mock: EmailMock) -> None:
        self._email = email_mock

    @property
    def channel(self) -> NotificationChannel:
        return NotificationChannel.EMAIL

    async def notify(
        self, profile: UserWakeProfile, message: str, track: Track
    ) -> None:
        try:
            self._email.send(
                to=profile.email,
                subject=f"Réveil musical — {track.title}",
                body=message,
            )
        except RuntimeError as exc:
            raise NotificationError(self.channel.value, str(exc)) from exc


class SmsNotificationAdapter:
    def __init__(self, sms_mock: SmsMock) -> None:
        self._sms = sms_mock

    @property
    def channel(self) -> NotificationChannel:
        return NotificationChannel.SMS

    async def notify(
        self, profile: UserWakeProfile, message: str, track: Track
    ) -> None:
        try:
            self._sms.send_text(phone=profile.phone, text=message)
        except RuntimeError as exc:
            raise NotificationError(self.channel.value, str(exc)) from exc


class PushNotificationAdapter:
    def __init__(self, push_mock: PushMock) -> None:
        self._push = push_mock

    @property
    def channel(self) -> NotificationChannel:
        return NotificationChannel.PUSH

    async def notify(
        self, profile: UserWakeProfile, message: str, track: Track
    ) -> None:
        payload = {
            "title": "Réveil musical",
            "body": message,
            "track": track.title,
        }
        try:
            self._push.deliver(device_token=profile.device_token, payload=payload)
        except RuntimeError as exc:
            raise NotificationError(self.channel.value, str(exc)) from exc


class EmergencyConsoleAdapter:
    @property
    def channel(self) -> NotificationChannel:
        return NotificationChannel.EMERGENCY

    async def notify(
        self, profile: UserWakeProfile, message: str, track: Track
    ) -> None:
        logger.warning(
            "[EMERGENCY] user=%s track=%s — %s",
            profile.user_id,
            track.title,
            message,
        )
