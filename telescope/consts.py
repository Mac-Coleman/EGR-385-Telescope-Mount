# Overall stuff
DEBUG_TIMEOUT = 15

# World stuff
TRUE_NORTH = (0, 0)  # Lat, Long
MAGNETIC_NORTH_2024 = (86.0, 142.0)  # Lat, Long
# https://wdc.kugi.kyoto-u.ac.jp/poles/polesexp.html

# Accelerometer Stuff
ACCELEROMETER_FORWARD = (1, 0, 0)

# Magnetometer STUFF
MAGNETOMETER_FORWARD = (0, 1, 0)

# GPS Stuff
GPS_UART = "/dev/ttyAMA0"
GPS_BAUDRATE = 9600
GPS_TIMEOUT = 10

# Motor Stuff
AZ_DIR_PIN = None
AZ_PULSE_PIN = None

AL_DIR_PIN = None
AL_PULSE_PIN = None
