from telescope.lib.lcddriver import lcd
from telescope.consts import DEBUG_TIMEOUT
from telescope.interface import Interface
from telescope.mount import Mount

import time
import board
from adafruit_seesaw import seesaw, digitalio
from rpi_hardware_pwm import HardwarePWM
import RPi.GPIO as GPIO

print("The telescope is now running...")


def main():
    start_time = time.time()
    start = False

    i2c = board.I2C()
    wheel = seesaw.Seesaw(i2c, addr=0x49)
    display = lcd()
    display.lcd_clear()

    display.lcd_display_string("Loading...".center(20), 1)
    display.lcd_display_string("SELECT to start".center(20), 2)
    display.lcd_display_string("OR".center(20), 3)
    display.lcd_display_string(f"wait {DEBUG_TIMEOUT}s to debug".center(20), 4)

    wheel_product = (wheel.get_version() >> 16) & 0xFFFF
    print("Found product: ", wheel_product)

    if wheel_product != 5740:
        raise ValueError("Wrong seesaw model!")

    wheel.pin_mode(1, wheel.INPUT_PULLUP)
    select = digitalio.DigitalIO(wheel, 1)

    while time.time() < (start_time + DEBUG_TIMEOUT):
        display.lcd_display_string(f"wait {int((start_time+DEBUG_TIMEOUT) - time.time())}s to debug".center(20), 4)
        time.sleep(0.1)
        if not select.value:
            start = True
            break

    if start:
        display.lcd_clear()
        display.lcd_display_string("Starting...".center(20), 1)
        # Clean these up for now
        del display
        del wheel
        del i2c
        run_telescope()
    else:
        print("Telescope escaped")
        display.lcd_clear()
        display.lcd_display_string("CANCELLED".center(20), 1)
        display.lcd_display_string("Telescope did not".center(20), 3)
        display.lcd_display_string("start".center(20), 4)


def run_telescope():
    print("running telescope")
    i2c = board.I2C()
    interface = Interface(i2c)
    # Perform setup routine for user interface.

    try:
        interface.setup()
    except Exception as e:
        print(f"Halting due to {e}")
        print(traceback.format_exc())
    finally:
        HardwarePWM(pwm_channel=0, hz=10).stop()
        HardwarePWM(pwm_channel=1, hz=10).stop()
        GPIO.cleanup



if __name__ == "__main__":
    main()
