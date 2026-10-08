from dataclasses import dataclass
from enum import StrEnum


class WeatherType(StrEnum):
    SOLEIL = "SOLEIL"
    PLUIE = "PLUIE"
    NEIGE = "NEIGE"
    NUAGEUX = "NUAGEUX"


class DayOfWeek(StrEnum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class NotificationChannel(StrEnum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    EMERGENCY = "emergency"


@dataclass(frozen=True)
class Track:
    title: str
    artist: str
    listen_url: str | None = None


@dataclass(frozen=True)
class UserWakeProfile:
    user_id: str
    tracks_by_weather: dict[WeatherType, str]
    fallback_track_query: str
    preferred_channel: NotificationChannel
    email: str
    phone: str
    device_token: str


@dataclass(frozen=True)
class ResolvedTrack:
    track: Track
    music_source: str
    degraded: bool


@dataclass(frozen=True)
class NotificationDelivery:
    channel: NotificationChannel
    preferred_channel: NotificationChannel
    delivered: bool
    degraded: bool


@dataclass(frozen=True)
class WakeupResult:
    user_id: str
    day_of_week: DayOfWeek
    weather: WeatherType
    track: Track
    notification: NotificationDelivery
    music_source: str
    degraded: bool
