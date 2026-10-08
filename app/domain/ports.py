from typing import Protocol

from app.domain.models import (
    NotificationChannel,
    NotificationDelivery,
    ResolvedTrack,
    Track,
    UserWakeProfile,
)


class UserProfilePort(Protocol):
    async def get_profile(self, user_id: str) -> UserWakeProfile: ...


class MusicSearchPort(Protocol):
    async def search_track(self, query: str) -> Track: ...


class MusicCachePort(Protocol):
    async def get(self, query: str) -> Track | None: ...

    async def set(self, query: str, track: Track) -> None: ...


class MusicResolverPort(Protocol):
    async def resolve(self, query: str) -> ResolvedTrack: ...


class LocalMusicFallbackPort(Protocol):
    async def lookup(self, query: str) -> Track | None: ...

    async def minimal_track(self, query: str) -> Track: ...


class ChannelNotifierPort(Protocol):
    @property
    def channel(self) -> NotificationChannel: ...

    async def notify(
        self, profile: UserWakeProfile, message: str, track: Track
    ) -> None: ...


class NotificationDeliveryPort(Protocol):
    async def deliver(
        self, profile: UserWakeProfile, message: str, track: Track
    ) -> NotificationDelivery: ...
