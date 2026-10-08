from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.domain.models import NotificationChannel


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    music_provider: Literal["itunes", "musicbrainz"] = "itunes"
    itunes_url: str = "https://itunes.apple.com"
    musicbrainz_url: str = "https://musicbrainz.org/ws/2"
    app_user_agent: str = "ReveilMusical/1.0 (prenom.nom@ecole.fr)"
    http_timeout: float = 10.0
    notification_fallback_order: str = "push,email,sms"

    @field_validator("notification_fallback_order", mode="before")
    @classmethod
    def parse_fallback_order(cls, value: str) -> str:
        return value

    def fallback_channels(self) -> list[NotificationChannel]:
        channels: list[NotificationChannel] = []
        for part in self.notification_fallback_order.split(","):
            name = part.strip().lower()
            if name:
                channels.append(NotificationChannel(name))
        return channels


@lru_cache
def get_settings() -> Settings:
    return Settings()
