class DomainError(Exception):
    pass


class UserNotFoundError(DomainError):
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        super().__init__(f"User not found: {user_id}")


class TrackNotFoundError(DomainError):
    def __init__(self, query: str) -> None:
        self.query = query
        super().__init__(f"No track found for query: {query}")


class ExternalServiceError(DomainError):
    def __init__(self, service: str, detail: str) -> None:
        self.service = service
        self.detail = detail
        super().__init__(f"{service} error: {detail}")


class NotificationError(DomainError):
    def __init__(self, channel: str, detail: str) -> None:
        self.channel = channel
        self.detail = detail
        super().__init__(f"Notification failed on {channel}: {detail}")
