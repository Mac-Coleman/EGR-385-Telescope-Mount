
class DMS:
    def __init__(self, angle=None, limit=180, d: int = 0, m: int = 0, s: int = 0.0, sign: int = 1):
        self.sign = sign
        self.sign *= 1 if d >= 0 else -1
        self.deg = abs(d)
        self.min = abs(m)
        self.sec = abs(s)
        if angle is not None:
            signed_angle = (angle + limit) % (2*limit) - limit
            if signed_angle >= 0:
                self.sign = 1
            else:
                self.sign = -1
            self.deg = int(abs(signed_angle))
            decimal_minutes = (signed_angle % 1) * 60  # This feels sketchy
            self.min = int(decimal_minutes)
            decimal_seconds = (decimal_minutes % 1) * 60  # This feels even sketchier
            self.sec = decimal_seconds

    def __format__(self, spec):
        return "{}{} {:02}' {:04.1f}\"".format(str(self.sign * self.deg).rjust(4), chr(223), self.min, self.sec)

    def __str__(self):
        return "{}{} {:02}' {:04.1f}\"".format(str(self.sign * self.deg).rjust(4), chr(223), self.min, self.sec)

    def dec_deg(self) -> float:
        return self.deg + self.min / 60 + self.sec / (60 * 60)


class HMS:
    def __init__(self, angle=None, h: int = 0, m: int = 0, s: int = 0.0):
        self.hours = abs(h)
        self.min = abs(m)
        self.sec = abs(s)
        if angle is not None:
            decimal_hours = angle/360 * 24
            self.hours = int(decimal_hours)
            decimal_minutes = (decimal_hours % 1) * 60
            self.min = int(decimal_minutes)
            decimal_seconds = (decimal_minutes % 1) * 60
            self.sec = decimal_seconds

    def __format__(self, spec):
        return "{}h {:02}m {:04.1f}s".format(str(self.hours).rjust(4), self.min, self.sec)

    def __str__(self):
        return "{}h {:02}m {:04.1f}s".format(str(self.hours).rjust(4), self.min, self.sec)

    def dec_hours(self):
        return self.hours + self.min/60 + self.sec/(60 * 60)

    def dec_deg(self) -> float:
        return (self.hours/24 * 360) + (self.min/60 * 15) + (self.sec/(60 * 60) * 15)
