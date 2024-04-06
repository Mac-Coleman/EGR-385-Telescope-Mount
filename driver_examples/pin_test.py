import RPi.GPIO as GPIO
import time


pin_to_test = 18
try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_to_test, GPIO.OUT)

    val = False
    while True:
        val = not val
        GPIO.output(pin_to_test, val)
        time.sleep(1)
except Exception as e:
    print(e)
finally:
    GPIO.cleanup()
