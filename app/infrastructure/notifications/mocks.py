class EmailMock:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.sent: list[tuple[str, str, str]] = []

    def send(self, to: str, subject: str, body: str) -> None:
        if self.fail:
            raise RuntimeError("email provider unavailable")
        self.sent.append((to, subject, body))


class SmsMock:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.sent: list[tuple[str, str]] = []

    def send_text(self, phone: str, text: str) -> None:
        if self.fail:
            raise RuntimeError("sms gateway down")
        self.sent.append((phone, text))


class PushMock:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.sent: list[tuple[str, dict]] = []

    def deliver(self, device_token: str, payload: dict) -> None:
        if self.fail:
            raise RuntimeError("push service error")
        self.sent.append((device_token, payload))
