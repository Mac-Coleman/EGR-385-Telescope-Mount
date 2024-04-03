import math
from telescope.consts import MAGNETOMETER_FORWARD, ACCELEROMETER_FORWARD

Vector3 = tuple[float, float, float]


def dot(a: Vector3, b: Vector3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a: Vector3, b: Vector3) -> Vector3:
    return a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]


def unit(a: Vector3) -> Vector3:
    magnitude = mag(a)
    return a[0] / magnitude, a[1] / magnitude, a[2] / magnitude


def mag(a: Vector3) -> float:
    return math.sqrt(a[0]**2 + a[1] ** 2 + a[2] ** 2)


def signed_angle(a: Vector3, b: Vector3) -> float:
    # https://stackoverflow.com/questions/5188561/signed-angle-between-two-3d-vectors-with-same-origin-within-the-same-plane
    n = unit(cross(a, b))
    return math.atan2(dot(cross(a, b), n), dot(a, b)) * 180.0 / math.pi


def get_heading_from_magnetometer(magnetometer_reading: Vector3) -> float:
    # Return compass heading for now
    return signed_angle(magnetometer_reading, MAGNETOMETER_FORWARD)


def get_altitude_from_accelerometer(accelerometer_reading) -> float:
    return signed_angle(accelerometer_reading, ACCELEROMETER_FORWARD)