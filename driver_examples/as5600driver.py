
import sys
sys.path.append("./lib")

import i2c_lib
from time import *

# LCD Address
ADDRESS = 0x36

# commands
AS5600_ANGLE = 0x0E # + 0x0F

En = 0b00000100 # Enable bit
Rw = 0b00000010 # Read/Write bit
Rs = 0b00000001 # Register select bit

class as5600:
    #initializes objects and lcd
    def __init__(self):
        self.as5600_device = i2c_lib.i2c_device(ADDRESS)

    def read_angle_bits(self):
        high, low = self.as5600_device.read_block_data_length(AS5600_ANGLE, 2)
        return (high << 8) | low

    def read_angle_degrees(self):
        bits = self.read_angle_bits()
        return bits/4096 * 360.0
