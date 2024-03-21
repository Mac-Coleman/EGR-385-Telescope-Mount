import lcddriver
from time import *

lcd = lcddriver.lcd()
lcd.lcd_clear()

lcd.lcd_display_string(" 1. Moon", 1)
lcd.lcd_display_string(chr(1) + " 2. Mercury", 2)
lcd.lcd_display_string(" 3. Venus", 3)
lcd.lcd_display_string(" 4. Mercury", 4)

sleep(1)

lcd.lcd_clear()

for i in range(100):
    
    lcd.lcd_clear()
    lcd.lcd_display_string(str(i), 1)
    lcd.lcd_display_string([chr(i)], 2)
    sleep(1)
