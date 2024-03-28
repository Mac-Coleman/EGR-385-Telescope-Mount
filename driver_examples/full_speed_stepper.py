import RPi.GPIO as GPIO
import time
import math

pin = 18

duty_cycle = 50

freq = 32000

try:

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)

    pwm = GPIO.PWM(pin, freq)
    pwm.start(50)

    input("Press enter to stop")

except Exception as e:
    print(e)
    GPIO.cleanup()
finally:
    GPIO.cleanup()
