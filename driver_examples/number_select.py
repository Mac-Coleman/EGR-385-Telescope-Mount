
import lcddriver
import as5600driver
from time import *
import keyboard

lcd = lcddriver.lcd()
lcd.lcd_clear()

encoder = as5600driver.as5600()

right_ascension = 0
declination = 0

editing_ra = True

last_angle = encoder.read_angle_degrees()

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

def flip(arg):
    global editing_ra
    editing_ra = not editing_ra

keyboard.on_press_key('space', flip)

while True:
    angle = encoder.read_angle_degrees()
    signed_angle = angle - last_angle
    signed_angle = (signed_angle + 180) % 360 - 180
    diff = signed_angle/10
    if abs(diff) >= 0.05:
        last_angle = angle
    else:
        diff = 0.0

    if editing_ra:
        right_ascension = (right_ascension + diff)
    else:
        declination = (declination + diff)

    # lcd.lcd_clear()
    lcd.lcd_display_string("Enter coordinates", 1)
    lcd.lcd_display_string("{}RA: {}".format(">" if editing_ra else " ", HMS(right_ascension)), 2)
    lcd.lcd_display_string("{}DE: {}".format(" " if editing_ra else ">", DMS(declination, limit=90)), 3)
    lcd.lcd_display_string("OK <          > BACK", 4)
    sleep(0.01)
