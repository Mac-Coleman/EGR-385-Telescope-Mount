import time
import board
import adafruit_mmc56x3

i2c = board.I2C()
magnetometer = adafruit_mmc56x3.MMC5603(i2c)

while True:
    print(magnetometer.magnetic, magnetometer.temperature)
    time.sleep(0.1)
