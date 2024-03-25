from skyfield.api import load, wgs84, N, W
from time import sleep

import lcddriver

stations_url = 'http://celestrak.org/NORAD/elements/stations.txt'
satellites = load.tle_file(stations_url)

print("Loaded", len(satellites), 'satellites')

by_name = {sat.name: sat for sat in satellites}
satellite = by_name['ISS (ZARYA)']
print(satellite)

ts = load.timescale()

mount_vernon = wgs84.latlon(41.922 * N, 91.4168 * W)

difference = satellite - mount_vernon
topocentric = difference.at(ts.now())

alt, az, distance = topocentric.altaz()
print(alt)
print(az)
print(distance.km)

lcd = lcddriver.lcd()

while True:
    alt, az, distance = difference.at(ts.now()).altaz()
    lcd.lcd_display_string("ISS (ZARYA)", 1)
    lcd.lcd_display_string("AL: {}".format(str(alt).rjust(16)), 2)
    lcd.lcd_display_string("AZ: {}".format(str(az).rjust(16)), 3)
    lcd.lcd_display_string("Distance: {:>8.2f}km".format(distance.km), 4)
    sleep(1)
