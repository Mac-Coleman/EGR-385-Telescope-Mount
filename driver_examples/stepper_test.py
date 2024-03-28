import RPi.GPIO as GPIO
import time
import math

pin = 18

duty_cycle = 50

freqs = [60000 / x for x in reversed(range(1, 101))]

try:

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)

    pwm = GPIO.PWM(pin, 32)
    pwm.start(50)

    while True:
        for freq in freqs:
            pwm.ChangeFrequency(freq)
            print(freq)
            time.sleep(0.25)
        for freq in reversed(freqs):
            pwm.ChangeFrequency(freq)
            print(freq)
            time.sleep(0.25)
except Exception as e:
    print(e)
    GPIO.cleanup()
finally:
    GPIO.cleanup()
