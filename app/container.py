import httpx
from dependency_injector import containers, providers
from dependency_injector.resources import AsyncResource

from app.config import Settings, get_settings
from app.infrastructure.http.http_client import create_http_client
from app.infrastructure.music.cached_music_client import CachedMusicClient
from app.infrastructure.music.composite_music_resolver import (
    CompositeMusicResolver,
    DemoMusicResolver,
)
from app.infrastructure.music.itunes_client import ItunesMusicClient
from app.infrastructure.music.local_fallback_music import LocalFallbackMusicProvider
from app.infrastructure.music.memory_music_cache import InMemoryMusicCache
from app.infrastructure.music.musicbrainz_client import MusicBrainzMusicClient
from app.infrastructure.users.in_memory_user_profile import InMemoryUserProfileClient
from app.infrastructure.notifications.adapters import (
    EmailNotificationAdapter,
    EmergencyConsoleAdapter,
    PushNotificationAdapter,
    SmsNotificationAdapter,
)
from app.infrastructure.notifications.mocks import EmailMock, PushMock, SmsMock
from app.infrastructure.notifications.resilient_sender import ResilientNotificationSender
from app.services.wakeup_service import WakeupService


def build_notification_sender(
    email_notifier: EmailNotificationAdapter,
    sms_notifier: SmsNotificationAdapter,
    push_notifier: PushNotificationAdapter,
    emergency_notifier: EmergencyConsoleAdapter,
    settings: Settings,
) -> ResilientNotificationSender:
    return ResilientNotificationSender(
        notifiers=[email_notifier, sms_notifier, push_notifier],
        fallback_order=settings.fallback_channels(),
        emergency=emergency_notifier,
    )


class HttpClientResource(AsyncResource[httpx.AsyncClient]):
    async def init(self, settings: Settings) -> httpx.AsyncClient:
        return create_http_client(settings)

    async def shutdown(self, resource: httpx.AsyncClient | None) -> None:
        if resource is not None:
            await resource.aclose()


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["app.api.routes.wakeup"],
    )

    config = providers.Singleton(get_settings)

    http_client = providers.Resource(
        HttpClientResource,
        settings=config,
    )

    music_cache = providers.Singleton(InMemoryMusicCache)

    itunes_client = providers.Factory(
        ItunesMusicClient,
        http=http_client,
        base_url=config.provided.itunes_url,
    )

    musicbrainz_client = providers.Factory(
        MusicBrainzMusicClient,
        http=http_client,
        base_url=config.provided.musicbrainz_url,
        user_agent=config.provided.app_user_agent,
    )

    cached_itunes = providers.Factory(
        CachedMusicClient,
        delegate=itunes_client,
        cache=music_cache,
    )

    cached_musicbrainz = providers.Factory(
        CachedMusicClient,
        delegate=musicbrainz_client,
        cache=music_cache,
    )

    local_fallback = providers.Singleton(LocalFallbackMusicProvider)

    music_resolver_itunes_primary = providers.Factory(
        CompositeMusicResolver,
        primary=cached_itunes,
        secondary=cached_musicbrainz,
        local_fallback=local_fallback,
        primary_source="itunes",
        secondary_source="musicbrainz",
    )

    music_resolver_musicbrainz_primary = providers.Factory(
        CompositeMusicResolver,
        primary=cached_musicbrainz,
        secondary=cached_itunes,
        local_fallback=local_fallback,
        primary_source="musicbrainz",
        secondary_source="itunes",
    )

    music_resolver = providers.Selector(
        config.provided.music_provider,
        itunes=music_resolver_itunes_primary,
        musicbrainz=music_resolver_musicbrainz_primary,
    )

    demo_music_resolver = providers.Factory(DemoMusicResolver)

    user_profiles = providers.Singleton(InMemoryUserProfileClient)

    email_mock = providers.Singleton(EmailMock)
    sms_mock = providers.Singleton(SmsMock)
    push_mock = providers.Singleton(PushMock)

    email_notifier = providers.Factory(EmailNotificationAdapter, email_mock=email_mock)
    sms_notifier = providers.Factory(SmsNotificationAdapter, sms_mock=sms_mock)
    push_notifier = providers.Factory(PushNotificationAdapter, push_mock=push_mock)
    emergency_notifier = providers.Factory(EmergencyConsoleAdapter)

    notification_sender = providers.Factory(
        build_notification_sender,
        email_notifier=email_notifier,
        sms_notifier=sms_notifier,
        push_notifier=push_notifier,
        emergency_notifier=emergency_notifier,
        settings=config,
    )

    wakeup_service = providers.Factory(
        WakeupService,
        profiles=user_profiles,
        music_resolver=music_resolver,
        demo_music_resolver=demo_music_resolver,
        notifier=notification_sender,
    )


container = Container()
