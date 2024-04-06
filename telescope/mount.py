import adafruit_adxl34x
import adafruit_mmc56x3
import adafruit_gps
import serial

import telescope.consts as consts
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

        self.__az_motor = StepperMotor(consts.AZ_PWM_CHANNEL, consts.AZ_DIR_PIN, consts.AZ_MAX_SPEED, consts.AZ_MAX_ACCELERATION, sign=consts.AZ_DIRECTION_SIGN)
        self.__al_motor = StepperMotor(consts.AL_PWM_CHANNEL, consts.AL_DIR_PIN, consts.AL_MAX_SPEED, consts.AL_MAX_ACCELERATION, sign=consts.AL_DIRECTION_SIGN)

        self.__setpoint_altitude = 0.0
        self.__setpoint_azimuth = 0.0
        self.__offset_x = 0
        self.__offset_y = 0
        self.__altitude_offset = 0.0
        self.__magnetic_declination = 0

    def poll_gps(self):
        self.__gps.update()
        return (
            self.__gps.has_fix,
            self.__gps.has_3d_fix,
            self.__gps.satellites,
            self.__gps.timestamp_utc,
            self.__gps.latitude,
            self.__gps.latitude_degrees,
            self.__gps.latitude_minutes,
            self.__gps.longitude,
            self.__gps.longitude_degrees,
            self.__gps.longitude_minutes,
            self.__gps.altitude_m  # No idea if I should use this or geoidal separation
        )

    def get_altitude(self):
        return get_altitude_from_accelerometer(self.__accelerometer.acceleration) - self.__altitude_offset

    def get_azimuth(self):
        return self.get_heading() - self.__magnetic_declination

    def get_magnetic(self):
        return self.__magnetometer.magnetic

    def get_heading(self):
        x, y, z = self.__magnetometer.magnetic
        x -= self.__offset_x
        y -= self.__offset_y
        return get_heading_from_magnetometer((x, y, z))

    def set_offsets(self, offset_x, offset_y):
        self.__offset_x = offset_x
        self.__offset_y = offset_y

    def set_mag_declination(self, declination: float):
        self.__magnetic_declination = declination

    def set_altitude_offset(self, offset: float):
        self.__altitude_offset = offset

    def level_altitude(self):
        acceleration = self.__accelerometer.acceleration
        altitude = get_altitude_from_accelerometer(acceleration)
        return self.__al_motor.run(altitude, 0)[0]

    def stop(self):
        self.__az_motor.stop()
        self.__al_motor.stop()

    def spin_azimuth(self, speed):
        self.__az_motor.set_speed(speed)

    def spin_altitude(self, speed):
        self.__al_motor.set_speed(speed)

    def set_setpoint(self, altitude: float, azimuth: float):
        if altitude < -10:
            raise ValueError("Attempted to point telescope significantly below the horizon!")
        if altitude > 89:
            raise ValueError("Attempted to point telescope near the zenith singularity!")
        self.__setpoint_altitude = altitude
        self.__setpoint_azimuth = azimuth

    def go_to_setpoint(self):
        # Take care of telescope tasks
        # For now we will just print the heading and altitude

        al = self.__al_motor.run(self.get_altitude(), self.__setpoint_altitude)
        az = self.__az_motor.run(self.get_azimuth(), self.__setpoint_azimuth)
        return *al[1:], *az[1:]
