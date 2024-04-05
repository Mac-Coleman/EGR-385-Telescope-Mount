
class DMS:
    def __init__(self, angle=None, limit=180, d: int = 0, m: int = 0, s: int = 0.0, sign: int = 1):
        self.sign = sign
        self.deg = d
        self.min = m
        self.sec = s
        if angle is not None:
            signed_angle = (angle + limit) % (2*limit) - limit
            if signed_angle >= 0:
                self.sign = 1
            else:
                self.sign = 0
            self.deg = round(abs(signed_angle))
            m = (signed_angle % 1) * 60 # This feels sketchy
            self.min = round(m)
            s = ((m * 100) % 1) * 60 # This feels even sketchier
            self.sec = s

    def __format__(self, spec):
        return "{}{}{} {:02}' {:04.1f}\"".format(" " if self.sign == 1 else "-", str(self.deg).rjust(4), chr(223), self.min, self.sec)

    def __str__(self):
       return "{}{} {:02}' {:04.1f}\"".format(str(self.deg).rjust(4), chr(223), self.min, self.sec)

class HMS:
    def __init__(self, angle):
        signed_angle = angle/360 * 24
        self.hours = round(signed_angle)
        m = (signed_angle % 1) * 60
        self.min = round(m)
        s = ((m * 100) % 1) * 60
        self.sec = s

    def __format__(self, spec):
        return "{}h {:02}m {:04.1f}s".format(str(self.hours).rjust(4), self.min, self.sec)

    def __str__(self):
        return "{}h {:02}m {:04.1f}s".format(str(self.hours).rjust(4), self.min, self.sec)

