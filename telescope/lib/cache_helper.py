from pathlib import Path
from typing import Optional, Tuple


def cache_path() -> Path:
    p = Path.home() / ".cache" / "telescope"
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_cached_magnetometer_offsets() -> Optional[Tuple[float, float]]:
    p = cache_path() / "offsets.csv"
    offsets = None

    try:
        with open(p) as cache_file:
            offsets_string = cache_file.read().strip().split(",")
            offsets = float(offsets_string[0]), float(offsets_string[1])
    except FileNotFoundError as e:
        print("No cached data found")
    except ValueError as e:
        print("Cache file found but could not be read")

    return offsets


def cache_magnetometer_offsets(offset_x, offset_y):
    p = cache_path() / "offsets.csv"
    offsets_string = str(offset_x) + "," + str(offset_y)
    with open(p, "w") as cache_file:
        cache_file.write(offsets_string)
