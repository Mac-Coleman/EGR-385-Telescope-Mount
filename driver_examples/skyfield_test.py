from angles import HMS, DMS

import lcddriver

from skyfield.api import load, wgs84, N, S, E, W
from time import sleep

ts = load.timescale()
t = ts.now()

planets = load('de421.bsp')
earth, mars = planets['earth'], planets['mars']

mount_vernon = earth + wgs84.latlon(41.9220 * N, 91.4168 * W)

lcd = lcddriver.lcd()
lcd.lcd_clear()

while True:
    t = ts.now()
    astrometric =  mount_vernon.at(t).observe(mars)
    apparent = astrometric.apparent()
    alt, az, distance = apparent.altaz()

    lcd.lcd_display_string("Mars", 1)
    lcd.lcd_display_string(f"AL: {alt.dstr()}", 2)
    lcd.lcd_display_string(f"AZ: {az.dstr()}", 3)
    lcd.lcd_display_string("Distance: " + str(distance).rjust(10), 4)
    sleep(1.0)
