# ------- SERVO TRANSPORT ---------------------------------------------------
# Narrow interface for commanding servos: connect(), send_angle(), close().
# Three servos: "shoulder", "elbow1", "elbow2". Anything else is refused.
#
# Wire protocol expected on the Arduino side (plain text line, 9600 baud):
#     "<JOINT>:<ANGLE>\n"   e.g.  "SHOULDER:90.0\n"
# See arduino/arm_control/arm_control.ino.

import logging
import time
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Per-joint safe range in degrees. These are placeholders (0-180, the servo's
# own physical limit) - tighten them once you know how far each joint can
# actually move without the arm binding or the cardboard/frame fouling.
SAFE_RANGE_DEG = {
    "shoulder": (0, 180),
    "elbow1": (0, 180),
    "elbow2": (0, 180),
}


def _in_safe_range(joint: str, degrees: float) -> Optional[Tuple[float, float]]:
    """Returns the (low, high) range if `degrees` is safe for `joint`,
    otherwise logs a warning and returns None."""
    if joint not in SAFE_RANGE_DEG:
        logger.warning("Refusing to command %r: no servo on this joint", joint)
        return None
    low, high = SAFE_RANGE_DEG[joint]
    if not (low <= degrees <= high):
        logger.warning(
            "Refusing out-of-range angle %.1f for %s (safe range %d-%d)",
            degrees, joint, low, high,
        )
        return None
    return (low, high)


class ServoLink:
    """Real servo link over a serial connection to an Arduino."""

    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial = None

    def connect(self) -> None:
        import serial  # imported here so DummyServoLink needs no pyserial install

        self._serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        time.sleep(2)  # Arduino resets when the serial port opens; let the sketch boot
        logger.info("Connected to %s at %d baud", self.port, self.baudrate)

    def send_angle(self, joint: str, degrees: float) -> None:
        if self._serial is None:
            raise RuntimeError("ServoLink.connect() must be called before send_angle()")
        if _in_safe_range(joint, degrees) is None:
            return
        line = f"{joint.upper()}:{degrees:.1f}\n"
        self._serial.write(line.encode("utf-8"))
        print(f"[ServoLink] sent: {line.strip()}")

    def close(self) -> None:
        if self._serial is not None:
            self._serial.close()
            self._serial = None


class DummyServoLink:
    """No hardware attached. Logs to stdout so the rest of the system runs standalone."""

    def __init__(self, *args, **kwargs):
        pass

    def connect(self) -> None:
        print("[DummyServoLink] connected (no hardware)")

    def send_angle(self, joint: str, degrees: float) -> None:
        if _in_safe_range(joint, degrees) is None:
            return
        print(f"[DummyServoLink] {joint} -> {degrees:.1f} deg")

    def close(self) -> None:
        print("[DummyServoLink] closed")
