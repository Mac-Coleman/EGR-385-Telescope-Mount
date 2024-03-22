import lcddriver
import as5600driver
from time import *

lcd = lcddriver.lcd()
lcd.lcd_clear()

encoder = as5600driver.as5600()

objects = ["The Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "Makemake", "Haumea", "Quaoar"]

selection = 0
window = 0 # Offset from top of list

last_angle = encoder.read_angle_degrees()

while True:
    angle = encoder.read_angle_degrees()
    signed_angle = angle - last_angle
    signed_angle = (signed_angle + 180) % 360 - 180
    diff = int(signed_angle/10)
    if diff != 0:
        last_angle = angle
    selection = (selection + diff) % len(objects)
    if selection < window:
        window = max(0, selection)
    if selection > window + 3:
        window = min(selection-3, len(objects))
    # lcd.lcd_clear()
    for i in range(window, min(window + 4, len(objects))):
        s = "> " if i == selection else "  "
        s += objects[i]
        lcd.lcd_display_string(s, i - window + 1)
    sleep(0.01)
