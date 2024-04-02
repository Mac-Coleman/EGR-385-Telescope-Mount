from telescope.lib.lcddriver import lcd

import time
import board
from adafruit_seesaw import seesaw, digitalio

print("The telescope is now running...")


def main():
    start_time = time.time()
    start = False

    i2c = board.I2C()
    wheel = seesaw.Seesaw(i2c, addr=0x49)
    display = lcd()
    display.lcd_clear()

    display.lcd_display_string("Loading...".center(20), 1)
    display.lcd_display_string("Press SELECT to start".center(20), 2)
    display.lcd_display_string("OR".center(20), 3)
    display.lcd_display_string("wait 5s to debug".center(20), 4)

    wheel_product = (wheel.get_version() >> 16) & 0xFFFF
    print("Found product: ", wheel_product)

    if wheel_product != 5740:
        raise ValueError("Wrong seesaw model!")

    wheel.pin_mode(1, wheel.INPUT_PULLUP)
    select = digitalio.DigitalIO(wheel, 1)

    while time.time() > (start_time + 5):
        display.lcd_display_string(f"wait {int((start_time+5) - time.time())}s to debug", 4)
        if not select.value:
            start = True
            break

    if start:
        run_telescope()
    else:
        print("Telescope escaped")



def run_telescope():
    print("running telescope")


if __name__ == "__main__":
    main()
