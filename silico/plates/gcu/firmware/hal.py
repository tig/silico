"""Product HAL contract — pure shape, no hardware.

Domain logic talks to this surface only. Host sim implements the same methods
with boring values. Device backends live in ``hal_board`` (may import machine).

v1 does not prescribe product-specific pin methods as a silico API. Extend this
class (or a Protocol) with your GCU's reads/writes; keep time helpers stable.
"""


class Hal:
    """Minimal HAL surface every GCU plate starts with."""

    def set_led(self, on: bool) -> None:
        """Drive status LED. ``on=True`` means illuminated (backend maps polarity)."""
        raise NotImplementedError

    def ticks_ms(self) -> int:
        """Monotonic milliseconds (wrap-safe diffs are the caller's problem)."""
        raise NotImplementedError

    def sleep_ms(self, ms: int) -> None:
        """Block for approximately ``ms`` milliseconds."""
        raise NotImplementedError
