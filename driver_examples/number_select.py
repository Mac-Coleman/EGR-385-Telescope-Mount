
import lcddriver
import as5600driver
from time import *

lcd = lcddriver.lcd()
lcd.lcd_clear()

encoder = as5600driver.as5600()

selection = 0

last_angle = encoder.read_angle_degrees()

class DMS:
    def __init__(self, angle):
        signed_angle = (angle + 180) % 360 - 180
        self.deg = round(signed_angle)
        m = (signed_angle % 1) * 60 # This feels sketchy
        self.min = round(m)
        s = ((m * 100) % 1) * 60 # This feels even sketchier
        self.sec = s

    def __format__(self, spec):
        return "{}{} {:02}' {:04.1f}\"".format(str(self.deg).rjust(4), chr(223), self.min, self.sec)

while True:
    angle = encoder.read_angle_degrees()
    signed_angle = angle - last_angle
    signed_angle = (signed_angle + 180) % 360 - 180
    diff = signed_angle/10
    if abs(diff) >= 0.05:
        last_angle = angle
    else:
        diff = 0.0
    selection = (selection + diff)
    # lcd.lcd_clear()
    lcd.lcd_display_string("Enter coordinates", 1)
    lcd.lcd_display_string(">RA: {}".format(DMS(selection)), 2)
    lcd.lcd_display_string(" DE: {}".format(DMS(-18.9567)), 3)
    lcd.lcd_display_string("OK              BACK", 4)
    sleep(0.01)
