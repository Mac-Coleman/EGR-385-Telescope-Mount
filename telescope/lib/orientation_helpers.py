import math
from telescope.consts import MAGNETOMETER_FORWARD, ACCELEROMETER_FORWARD

Vector3 = tuple[float, float, float]
Vector2 = tuple[float, float]


def signed_angle2(a: Vector2) -> float:
    ang = math.atan2(a[0], a[1])
    return ang * 180.0 / math.pi


def get_heading_from_magnetometer(magnetometer_reading: Vector3) -> float:
    # Return compass heading for now
    flattened_reading = (-magnetometer_reading[1], magnetometer_reading[0])
    h = signed_angle2(flattened_reading) * -1  # I clearly don't know my atan2 identities
    if h < 0:
        h += 360.0
    return h


def get_altitude_from_accelerometer(accelerometer_reading) -> float:
    flattened_reading = (accelerometer_reading[0], accelerometer_reading[2])
    return signed_angle2(flattened_reading)

def get_bearing_angle(point_a: Vector2, point_b: Vector2) -> float:
    # https://www.igismap.com/formula-to-find-bearing-or-heading-angle-between-two-points-latitude-longitude/
    a = point_a[0] * math.pi / 180.0, point_a[1] * math.pi / 180.0
    b = point_b[0] * math.pi / 180.0, point_b[1] * math.pi / 180.0
    delta_longitude = b[1] - a[1]
    x = math.cos(b[0]) * math.sin(delta_longitude)
    y = math.cos(a[0]) * math.sin(b[0]) - math.sin(a[0]) * math.cos(b[0]) * math.cos(delta_longitude)
    h = math.atan2(y, x) * 180 / math.pi
    return h
