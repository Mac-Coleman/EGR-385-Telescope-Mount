
class DMS:
    def __init__(self, angle, limit=180):
        signed_angle = (angle + limit) % (2*limit) - limit
        self.deg = round(signed_angle)
        m = (signed_angle % 1) * 60 # This feels sketchy
        self.min = round(m)
        s = ((m * 100) % 1) * 60 # This feels even sketchier
        self.sec = s

    def __format__(self, spec):
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

