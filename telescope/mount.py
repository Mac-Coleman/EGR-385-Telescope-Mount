import adafruit_adxl34x
import adafruit_mmc56x3
import adafruit_gps
import busio
import board

from telescope.consts import AZ_PULSE_PIN, AZ_DIR_PIN, AL_PULSE_PIN, AL_DIR_PIN
from telescope.lib.motor import StepperMotor
from telescope.lib.orientation_helpers import get_altitude_from_accelerometer, get_heading_from_magnetometer


class Mount:
    def __init__(self, i2c_bus):
        # Setup:
        #   Accelerometer
        #   Magnetometer
        #   GPS
        #   Azimuth Motor
        #   Altitude Motor
        self.__accelerometer = adafruit_adxl34x.ADXL343(i2c_bus)
        self.__magnetometer = adafruit_mmc56x3.MMC5603(i2c_bus)

        # self.__uart = busio.UART(board.UART_TX, board.UART_RX)
        # self.__gps = adafruit_gps.GPS(self.__uart, debug=False)

        self.__az_motor = StepperMotor(AZ_PULSE_PIN, AZ_DIR_PIN)
        self.__al_motor = StepperMotor(AL_PULSE_PIN, AL_DIR_PIN)

        self.__setpoint = (0.0, 0.0)  # Azimuth, Altitude Setpoint

    def update(self):
        # Take care of telescope tasks
        # For now we will just print the heading and altitude

        m_reading = self.__magnetometer.magnetic
        a_reading = self.__accelerometer.acceleration

        print("H: ", get_heading_from_magnetometer(m_reading))
        print("A: ", get_altitude_from_accelerometer(a_reading))
