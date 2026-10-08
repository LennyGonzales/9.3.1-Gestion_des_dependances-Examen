from app.domain.exceptions import NotificationError
from app.domain.models import NotificationChannel, NotificationDelivery, Track, UserWakeProfile
from app.domain.ports import ChannelNotifierPort


class ResilientNotificationSender:
    def __init__(
        self,
        notifiers: list[ChannelNotifierPort],
        fallback_order: list[NotificationChannel],
        emergency: ChannelNotifierPort,
    ) -> None:
        self._by_channel = {notifier.channel: notifier for notifier in notifiers}
        self._fallback_order = fallback_order
        self._emergency = emergency

    async def deliver(
        self, profile: UserWakeProfile, message: str, track: Track
    ) -> NotificationDelivery:
        preferred = profile.preferred_channel
        order = self._build_attempt_order(preferred)
        degraded = False

        for channel in order:
            notifier = self._by_channel.get(channel)
            if notifier is None:
                continue
            try:
                await notifier.notify(profile, message, track)
                if channel != preferred:
                    degraded = True
                return NotificationDelivery(
                    channel=channel,
                    preferred_channel=preferred,
                    delivered=True,
                    degraded=degraded,
                )
            except NotificationError:
                degraded = True
                continue

        await self._emergency.notify(profile, message, track)
        return NotificationDelivery(
            channel=self._emergency.channel,
            preferred_channel=preferred,
            delivered=True,
            degraded=True,
        )

    def _build_attempt_order(
        self, preferred: NotificationChannel
    ) -> list[NotificationChannel]:
        order: list[NotificationChannel] = [preferred]
        for channel in self._fallback_order:
            if channel not in order and channel in self._by_channel:
                order.append(channel)
        return order
