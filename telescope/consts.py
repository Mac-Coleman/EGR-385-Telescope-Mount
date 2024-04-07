# Overall stuff
DEBUG_TIMEOUT = 15

# World stuff
TRUE_NORTH = (90, 0)  # Lat, Long
MAGNETIC_NORTH_2024 = (86.0, 142.0)  # Lat, Long
MOUNT_VERNON_IOWA = (41.9220, -91.4168, 267.919)
# https://wdc.kugi.kyoto-u.ac.jp/poles/polesexp.html
METERS_TO_FEET = 3.28084

# Accelerometer Stuff
ACCELEROMETER_FORWARD = (1, 0, 0)

# Magnetometer STUFF
MAGNETOMETER_FORWARD = (0, 1, 0)

# GPS Stuff
GPS_UART = "/dev/ttyAMA0"
GPS_BAUDRATE = 9600
GPS_TIMEOUT = 10

# Motor Stuff
AZ_DIR_PIN = 24
AZ_PWM_CHANNEL = 1  # GPIO 19
AZ_MAX_SPEED = 4800  # Pulses per second
AZ_MAX_ACCELERATION = 1000  # Pulses per second squared
AZ_DIRECTION_SIGN = 1  # Pulsing while AZ_DIR_PIN is low causes azimuth to INCREASE

AL_DIR_PIN = 23
AL_PWM_CHANNEL = 0  # GPIO 18
AL_MAX_SPEED = 3000  # Pulses per second
AL_MAX_ACCELERATION = 1000  # Pulses per second squared
AL_DIRECTION_SIGN = -1 # Pulsing while AL_DIR_PIN is low causes altitude to DECREASE

DUTY_CYCLE = 50

# SQLITE3 Stuff
ALL_STARS = "SELECT * FROM stars"
FAVORITE_STARS = "SELECT * FROM stars WHERE favorite = TRUE"

ALL_MESSIER = "SELECT * FROM messier_objects"
FAVORITE_MESSIER = "SELECT * FROM messier_objects WHERE favorite = TRUE"

ALL_PLANETS = "SELECT * FROM solarsystem_objects"
FAVORITE_PLANETS = "SELECT * FROM solarsystem_objects WHERE favorite = TRUE"