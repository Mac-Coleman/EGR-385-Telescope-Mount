
import traceback
from time import *
import keyboard
import RPi.GPIO as GPIO
from rpi_hardware_pwm import HardwarePWM

az_speed = 4800
al_speed = 2000

az_pulse_pin = 19
az_dir_pin = 24
al_pulse_pin = 18
al_dir_pin = 23


def main(az_pwm, al_pwm):
    while True:
        az_direction = 0 if keyboard.is_pressed("left arrow") else None
        az_direction = 1 if keyboard.is_pressed("right arrow") else az_direction

        al_direction = 0 if keyboard.is_pressed("up arrow") else None
        al_direction = 1 if keyboard.is_pressed("down arrow") else al_direction

        if az_direction is not None:
            GPIO.output(az_dir_pin, az_direction)
            az_pwm.start(50)
            print("Az:", az_direction)
        else:
            az_pwm.stop()

        if al_direction is not None:
            GPIO.output(al_dir_pin, al_direction)
            al_pwm.start(50)
            print("Al:", al_direction)
        else:
            al_pwm.stop()
        sleep(0.01)


try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(al_dir_pin, GPIO.OUT)
    GPIO.setup(az_dir_pin, GPIO.OUT)

    al_pwm = HardwarePWM(pwm_channel=0, hz=al_speed, chip=0)
    az_pwm = HardwarePWM(pwm_channel=1, hz=az_speed, chip=0)
    main(az_pwm, al_pwm)
except Exception as e:
    print(f"Halting due to {e}")
    print(traceback.format_exc())
finally:
    al_pwm = HardwarePWM(pwm_channel=0, hz=200, chip=0)
    al_pwm.stop()
    az_pwm = HardwarePWM(pwm_channel=1, hz=200, chip=0)
    az_pwm.stop()
    GPIO.cleanup()
