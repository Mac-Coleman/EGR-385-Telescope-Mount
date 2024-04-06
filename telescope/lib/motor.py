# Drivers for stepper motors...
# Who knows if I can actually do this correctly.

from rpi_hardware_pwm import HardwarePWM
import RPi.GPIO as GPIO
from telescope.consts import DUTY_CYCLE


class StepperMotor:
    def __init__(self, pwm_channel, pin_dir, max_speed, max_acceleration, min_speed=0.1, sign=1):
        self.__driver = HardwarePWM(pwm_channel=pwm_channel, hz=min_speed)
        self.__driver.stop()

        self.__pin_dir = pin_dir
        self.__min_speed = min_speed
        self.__max_speed = max_speed
        self.__max_acceleration = max_acceleration
        self.__sign = sign

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.__pin_dir, GPIO.OUT)

    def run(self, sensor_value, setpoint, tolerance=0.01):

        speed = 0

        error = setpoint - sensor_value

        out_of_range = abs(error) > tolerance

        if out_of_range:
            speed = self.__max_speed * (1 if error > 0 else -1)

        self.set_speed(speed)

        return not out_of_range, sensor_value, setpoint, speed

    def set_speed(self, speed):
        print(speed)
        speed *= self.__sign
        print("Corrected", speed)
        abs_speed = abs(speed)
        if abs_speed > self.__max_speed:
            raise ValueError(f"Speed too high: {speed}")

        direction = False if speed > 0.0 else True
        GPIO.output(self.__pin_dir, direction)

        if abs_speed > 0.1:
            print("Moving", abs_speed)
            self.__driver.change_frequency(abs_speed)
            self.__driver.start(DUTY_CYCLE)
        else:
            self.__driver.stop()

    def stop(self):
        self.__driver.change_frequency(self.__min_speed)
        self.__driver.stop()
