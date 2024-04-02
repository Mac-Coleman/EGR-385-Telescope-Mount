import adafruit_adxl34x
import adafruit_mmc56x3
import adafruit_gps
import serial

from telescope.consts import GPS_UART, GPS_BAUDRATE, GPS_TIMEOUT


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

        self.__uart = serial.Serial(GPS_UART, baudrate=GPS_BAUDRATE, timeout=GPS_TIMEOUT)
        self.__gps = adafruit_gps.GPS(self.__uart, debug=False)