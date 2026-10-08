from app.domain.exceptions import UserNotFoundError
from app.domain.models import DayOfWeek, NotificationChannel, UserWakeProfile, WeatherType


def _grid_for_weather_on_all_days(
    weather: WeatherType, query: str
) -> dict[tuple[DayOfWeek, WeatherType], str]:
    return {(day, weather): query for day in DayOfWeek}


def _full_week_weather_grid(
    by_weather: dict[WeatherType, str],
    overrides: dict[tuple[DayOfWeek, WeatherType], str] | None = None,
) -> dict[tuple[DayOfWeek, WeatherType], str]:
    grid: dict[tuple[DayOfWeek, WeatherType], str] = {}
    for day in DayOfWeek:
        for weather, query in by_weather.items():
            grid[(day, weather)] = query
    if overrides:
        grid.update(overrides)
    return grid


class InMemoryUserProfileClient:
    def __init__(self) -> None:
        soleil_tracks = _full_week_weather_grid(
            {
                WeatherType.SOLEIL: "Here Comes The Sun",
                WeatherType.PLUIE: "Singin' in the Rain",
                WeatherType.NEIGE: "Let It Snow",
                WeatherType.NUAGEUX: "Cloudy Day",
            },
            overrides={
                (DayOfWeek.SATURDAY, WeatherType.SOLEIL): "Walking on Sunshine",
                (DayOfWeek.MONDAY, WeatherType.PLUIE): "Rainy Monday Blues",
            },
        )
        self._users: dict[str, UserWakeProfile] = {
            "user-soleil": UserWakeProfile(
                user_id="user-soleil",
                tracks_by_day_and_weather=soleil_tracks,
                fallback_track_query="Wake Up",
                preferred_channel=NotificationChannel.PUSH,
                email="soleil@example.com",
                phone="+33600000001",
                device_token="token-soleil",
            ),
            "user-pluie": UserWakeProfile(
                user_id="user-pluie",
                tracks_by_day_and_weather=_grid_for_weather_on_all_days(
                    WeatherType.PLUIE, "Singin' in the Rain"
                ),
                fallback_track_query="Wake Up",
                preferred_channel=NotificationChannel.EMAIL,
                email="pluie@example.com",
                phone="+33600000002",
                device_token="token-pluie",
            ),
            "user-sms": UserWakeProfile(
                user_id="user-sms",
                tracks_by_day_and_weather=_grid_for_weather_on_all_days(
                    WeatherType.SOLEIL, "Here Comes The Sun"
                ),
                fallback_track_query="Wake Up",
                preferred_channel=NotificationChannel.SMS,
                email="sms@example.com",
                phone="+33600000003",
                device_token="token-sms",
            ),
        }

    async def get_profile(self, user_id: str) -> UserWakeProfile:
        profile = self._users.get(user_id)
        if profile is None:
            raise UserNotFoundError(user_id)
        return profile
