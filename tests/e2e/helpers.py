def assert_wakeup_response_shape(data: dict) -> None:
    assert set(data.keys()) == {
        "userId",
        "dayOfWeek",
        "weather",
        "track",
        "notification",
        "degraded",
        "musicSource",
    }
    assert set(data["track"].keys()) == {"title", "artist", "listenUrl"}
    assert set(data["notification"].keys()) == {
        "channel",
        "preferredChannel",
        "delivered",
    }
