import board
import time
import adafruit_adxl34x

i2c = board.I2C()
accelerometer = adafruit_adxl34x.ADXL343(i2c)

while True:
    print(accelerometer.acceleration)
    time.sleep(0.1)
