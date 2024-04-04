import adafruit_adxl34x
import adafruit_mmc56x3
import adafruit_gps
import serial

from telescope.consts import AZ_PWM_CHANNEL, AZ_DIR_PIN, AL_PWM_CHANNEL, AL_DIR_PIN
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
        self.__magnetometer.set_reset()
        self.__magnetometer.reset()

        self.__uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=10)
        self.__gps = adafruit_gps.GPS(self.__uart, debug=False)

        # Turn on RMC/GGA messages.
        # https://receiverhelp.trimble.com/alloy-gnss/en-us/NMEA-0183messages_MessageOverview.html
        self.__gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
        # One second update period
        self.__gps.send_command(b"PMTK220,1000")

        self.__az_motor = StepperMotor(AZ_PWM_CHANNEL, AZ_DIR_PIN)
        self.__al_motor = StepperMotor(AL_PWM_CHANNEL, AL_DIR_PIN)

        self.__setpoint = (0.0, 0.0)  # Azimuth, Altitude Setpoint

    def poll_gps(self):
        self.__gps.update()
        return (
            self.__gps.has_fix,
            self.__gps.satellites,
            self.__gps.timestamp_utc,
            self.__gps.latitude_degrees,
            self.__gps.latitude_minutes,
            self.__gps.longitude_degrees,
            self.__gps.longitude_minutes
        )

    def update(self):
        # Take care of telescope tasks
        # For now we will just print the heading and altitude

        pass
