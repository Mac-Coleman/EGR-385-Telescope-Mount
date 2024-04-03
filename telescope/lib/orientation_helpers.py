import math
from telescope.consts import MAGNETOMETER_FORWARD, ACCELEROMETER_DOWN

Vector3 = tuple[float, float, float]


def dot(a: Vector3, b: Vector3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def mag(a: Vector3) -> float:
    return math.sqrt(a[0]**2 + a[1] ** 2 + a[2] ** 2)


def get_heading_from_magnetometer(magnetometer_reading: Vector3) -> float:
    # Return compass heading for now
    return math.acos(dot(MAGNETOMETER_FORWARD,magnetometer_reading) / (mag(magnetometer_reading))) * 180.0 / math.pi


def get_altitude_from_accelerometer(accelerometer_reading) -> float:
    return math.acos(dot(ACCELEROMETER_DOWN,accelerometer_reading) / (mag(accelerometer_reading))) * 180.0 / math.pi