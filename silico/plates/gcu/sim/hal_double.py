"""Host double for the plate HAL — same method names as firmware/hal.py."""


class FakeHal:
    def __init__(self):
        self.led = None
        self._ticks = 0
        self.sleeps: list[int] = []

    def set_led(self, on: bool) -> None:
        self.led = bool(on)

    def ticks_ms(self) -> int:
        return self._ticks

    def sleep_ms(self, ms: int) -> None:
        self.sleeps.append(int(ms))
        self._ticks += int(ms)
