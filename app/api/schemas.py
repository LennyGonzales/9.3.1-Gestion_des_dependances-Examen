from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from app.domain.models import DayOfWeek, NotificationChannel, WakeupResult, WeatherType


class WakeupTriggerRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(validation_alias=AliasChoices("userId", "user_id"))
    day_of_week: DayOfWeek = Field(
        validation_alias=AliasChoices("dayOfWeek", "day_of_week")
    )
    weather: WeatherType


class TrackResponse(BaseModel):
    title: str
    artist: str
    listen_url: str | None = Field(default=None, alias="listenUrl")

    model_config = {"populate_by_name": True}


class NotificationResponse(BaseModel):
    channel: NotificationChannel
    preferred_channel: NotificationChannel = Field(alias="preferredChannel")
    delivered: bool

    model_config = {"populate_by_name": True}


class WakeupResponse(BaseModel):
    user_id: str = Field(alias="userId")
    day_of_week: DayOfWeek = Field(alias="dayOfWeek")
    weather: WeatherType
    track: TrackResponse
    notification: NotificationResponse
    degraded: bool
    music_source: str = Field(alias="musicSource")

    model_config = {"populate_by_name": True}

    @classmethod
    def from_result(cls, result: WakeupResult) -> "WakeupResponse":
        return cls(
            userId=result.user_id,
            dayOfWeek=result.day_of_week,
            weather=result.weather,
            track=TrackResponse(
                title=result.track.title,
                artist=result.track.artist,
                listenUrl=result.track.listen_url,
            ),
            notification=NotificationResponse(
                channel=result.notification.channel,
                preferredChannel=result.notification.preferred_channel,
                delivered=result.notification.delivered,
            ),
            degraded=result.degraded,
            musicSource=result.music_source,
        )
