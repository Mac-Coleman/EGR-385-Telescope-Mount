# Test program to read and write data to PICAXE 20X2 over I2C bus.

import smbus
import time
import sys

bus = smbus.SMBus(1) #Use I2C bus 1.

pic_address = 0x30 #Don't multiply by 2, seven bit address space.

print("Began reading!")
while True:
    character = chr(bus.read_byte_data(pic_address, 0)) #Read character.
    adc_value = bus.read_byte_data(pic_address, 1) #Read adc (byte 1)

    if (ord(character) != 0):
        print("Key read: " + character + ", ADC: " + str(adc_value))
    else:
        print("No key read. ADC: " + str(adc_value))

    time.sleep(0.025)
