import lcddriver
import as5600driver
from time import *

lcd = lcddriver.lcd()
lcd.lcd_clear()

encoder = as5600driver.as5600()

selection = 0

last_angle = encoder.read_angle_degrees()

while True:
    angle = encoder.read_angle_degrees()
    signed_angle = angle - last_angle
    signed_angle = (signed_angle + 180) % 360 - 180
    diff = int(signed_angle/10)
    if diff != 0:
        last_angle = angle
    selection = (selection + diff)
    # lcd.lcd_clear()
    lcd.lcd_display_string(str(selection), 1)
    lcd.lcd_display_string(chr(selection), 2)
    sleep(0.01)
