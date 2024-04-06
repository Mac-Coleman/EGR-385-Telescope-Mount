# Drivers for stepper motors...
# Who knows if I can actually do this correctly.

from rpi_hardware_pwm import HardwarePWM
import RPi.GPIO as GPIO


class StepperMotor:
    def __init__(self, pwm_channel, pin_dir, max_speed, max_acceleration, min_speed=10):
        self.__driver = HardwarePWM(pwm_channel=pwm_channel, hz=min_speed)
        self.__driver.stop()

        self.__pin_dir = pin_dir
        self.__max_speed = max_speed
        self.__max_acceleration = max_acceleration

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.__pin_dir, GPIO.OUT)

    def run(self, sensor_value, setpoint, tolerance=0.01):
        direction = int(setpoint >= sensor_value)
        GPIO.output(self.__pin_dir, direction)

        condition = abs(setpoint - sensor_value) > tolerance

        if condition:
            self.__driver.change_frequency(self.__max_speed)
            self.__driver.start(50)
        else:
            self.__driver.stop()

        return not condition
