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
AZ_DIR_PIN = 24
AZ_PWM_CHANNEL = 1  # GPIO 19
AZ_MAX_SPEED = 4800  # Pulses per second
AZ_MAX_ACCELERATION = 1000  # Pulses per second squared

AL_DIR_PIN = 23
AL_PWM_CHANNEL = 0  # GPIO 18
AL_MAX_SPEED = 2000  # Pulses per second
AL_MAX_ACCELERATION = 1000  # Pulses per second squared
