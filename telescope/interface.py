from telescope.lib.lcddriver import lcd

import time
import textwrap
from adafruit_seesaw import seesaw, digitalio, rotaryio


class Interface:
    def __init__(self, i2c_bus):
        # Setup:
        #   LCD
        #   Keypad
        #   Rotary Encoder/Buttons
        self.__lcd = lcd()
        self.__wheel = seesaw.Seesaw(i2c_bus, addr=0x49)

        wheel_product = (self.__wheel.get_version() >> 16) & 0xFFFF

        if wheel_product != 5740:
            raise ValueError("Wrong seesaw model!")

        self.__wheel.pin_mode(1, self.__wheel.INPUT_PULLUP)
        self.__wheel.pin_mode(2, self.__wheel.INPUT_PULLUP)
        self.__wheel.pin_mode(3, self.__wheel.INPUT_PULLUP)
        self.__wheel.pin_mode(4, self.__wheel.INPUT_PULLUP)
        self.__wheel.pin_mode(5, self.__wheel.INPUT_PULLUP)

        self.__wheel_select = digitalio.DigitalIO(self.__wheel, 1)
        self.__wheel_up = digitalio.DigitalIO(self.__wheel, 2)
        self.__wheel_left = digitalio.DigitalIO(self.__wheel, 3)
        self.__wheel_down = digitalio.DigitalIO(self.__wheel, 4)
        self.__wheel_right = digitalio.DigitalIO(self.__wheel, 1)

        self.__wheel_encoder = rotaryio.IncrementalEncoder(self.__wheel)

    def select_pressed(self):
        return not self.__wheel_select.value

    def up_pressed(self):
        return not self.__wheel_up.value

    def left_pressed(self):
        return not self.__wheel_left.value

    def down_pressed(self):
        return not self.__wheel_down.value

    def right_pressed(self):
        return not self.__wheel_right.value

    def setup(self):
        print("Setup started.")

        self.__lcd.lcd_clear()
        self.__lcd.lcd_display_string("Zeroing altitude".center(20), 1)
        self.__lcd.lcd_display_string("Please wait".center(20), 4)

        time.sleep(5)

        calibrate = self.yes_or_no("Calibration found. Use calib data?")

        if calibrate:

            self.__lcd.lcd_clear()
            self.__lcd.lcd_display_string("Calibrating".center(20), 1)
            self.__lcd.lcd_display_string("Magnetometer...".center(20), 2)
            self.__lcd.lcd_display_string("Please wait".center(20), 4)

            time.sleep(5)

    def yes_or_no(self, question: str):
        self.__lcd.lcd_clear()
        s = textwrap.fill(question, 20).split("\n")[0:3]

        for lcd_line, line in enumerate(s):
            self.__lcd.lcd_display_string(line.center(20), lcd_line)

        selection = False
        last_encoder = self.__wheel_encoder.position

        headers = ("   ", " > ")

        while True:
            pos = self.__wheel_encoder.position
            if pos != last_encoder:
                selection = not selection
                last_encoder = pos

            prompt = "{ }Yes   { }No".center(20)
            prompt.format(headers[int(selection)], headers[int(not selection)])  # Ough
            self.__lcd.lcd_display_string(prompt, 4)

            if self.select_pressed():
                break
            time.sleep(0.1)

        return selection

    def update(self):
        pass
