# Drivers for stepper motors...
# Who knows if I can actually do this correctly.

from rpi_hardware_pwm import HardwarePWM
import RPi.GPIO as GPIO


class StepperMotor:
    def __init__(self, pwm_channel, pin_dir, max_speed, max_acceleration, min_speed=10):
        pass

    def update(self, sensor_value, setpoint):
        pass
