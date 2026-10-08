from app.domain.models import (
    DayOfWeek,
    Track,
    UserWakeProfile,
    WakeupResult,
    WeatherType,
)
from app.domain.ports import MusicResolverPort, NotificationDeliveryPort, UserProfilePort


class WakeupService:
    def __init__(
        self,
        profiles: UserProfilePort,
        music_resolver: MusicResolverPort,
        demo_music_resolver: MusicResolverPort,
        notifier: NotificationDeliveryPort,
    ) -> None:
        self._profiles = profiles
        self._music_resolver = music_resolver
        self._demo_music_resolver = demo_music_resolver
        self._notifier = notifier

    async def trigger_wakeup(
        self,
        user_id: str,
        day_of_week: DayOfWeek,
        weather: WeatherType,
        *,
        demo: bool = False,
    ) -> WakeupResult:
        profile = await self._profiles.get_profile(user_id)
        query = self._pick_track_query(profile, weather)
        resolver = self._demo_music_resolver if demo else self._music_resolver
        resolved = await resolver.resolve(query)
        message = self._build_message(day_of_week, weather, resolved.track)
        delivery = await self._notifier.deliver(profile, message, resolved.track)
        degraded = resolved.degraded or delivery.degraded
        return WakeupResult(
            user_id=user_id,
            day_of_week=day_of_week,
            weather=weather,
            track=resolved.track,
            notification=delivery,
            music_source=resolved.music_source,
            degraded=degraded,
        )

    @staticmethod
    def _pick_track_query(profile: UserWakeProfile, weather: WeatherType) -> str:
        return profile.tracks_by_weather.get(weather, profile.fallback_track_query)

    @staticmethod
    def _build_message(
        day_of_week: DayOfWeek, weather: WeatherType, track: Track
    ) -> str:
        url_part = f" — {track.listen_url}" if track.listen_url else ""
        return (
            f"Bon {day_of_week.value}! Météo: {weather.value}. "
            f"Votre réveil: {track.title} — {track.artist}{url_part}"
        )
