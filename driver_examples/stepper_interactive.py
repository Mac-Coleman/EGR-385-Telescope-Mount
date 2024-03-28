
import traceback
from time import *
import keyboard
import RPi.GPIO as GPIO
from rpi_hardware_pwm import HardwarePWM

speed = 0
pulse_pin = 18
dir_pin = 23

def right_arrow(arg):
    global speed
    speed += 200

def left_arrow(arg):
    global speed
    speed -= 200

keyboard.on_press_key('left arrow', left_arrow)
keyboard.on_press_key('right arrow', right_arrow)

def main(pwm):
    while True:
        speed_hyst = speed
        if abs(speed_hyst) < 0.5:
            pwm.stop()
        else:
            pwm.start(50)
            GPIO.output(dir_pin, speed_hyst <= 0)
            print(speed_hyst)
            pwm.change_frequency(abs(speed_hyst))
        sleep(0.01)


try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(dir_pin, GPIO.OUT)

    pwm = HardwarePWM(pwm_channel=0, hz=32, chip=0)
    main(pwm)
except Exception as e:
    print(f"Halting due to {e}")
    print(traceback.format_exc())
finally:
    pwm = HardwarePWM(pwm_channel=0, hz=32, chip=0)
    pwm.stop()
    GPIO.cleanup()
