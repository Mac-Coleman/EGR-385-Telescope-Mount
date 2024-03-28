import RPi.GPIO as GPIO
import time
import math

pulse_pin = 18
dir_pin = 23

duty_cycle = 50

dir = True

def lerp(a, b, x):
    if not 0.0 <= x <= 1.0:
        raise ValueError('You used it wrong!')
    return a + (b-a) * x

freqs = [lerp(0, 58000, x/100) for x in range(1, 100)]

try:

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pulse_pin, GPIO.OUT)
    GPIO.setup(dir_pin, GPIO.OUT)
    GPIO.output(dir_pin, dir)

    pwm = GPIO.PWM(pulse_pin, 32)
    pwm.start(50)

    while True:
        for freq in freqs:
            pwm.ChangeFrequency(freq)
            print(freq)
            time.sleep(0.05)
        for freq in reversed(freqs):
            pwm.ChangeFrequency(freq)
            print(freq)
            time.sleep(0.05)
        dir = not dir
        GPIO.output(dir_pin, dir)
except Exception as e:
    print(e)
    GPIO.cleanup()
finally:
    GPIO.cleanup()
