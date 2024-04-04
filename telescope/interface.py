from telescope.lib.lcddriver import lcd

import time
import textwrap
import sys
from adafruit_seesaw import seesaw, digitalio, rotaryio
from datetime import datetime, timezone


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

        leveled = self.yes_or_no("Is the telescope level?")

        if not leveled:
            self.error("Error: Control Failure. Debug required.")

        skip_calibrate = self.yes_or_no("Calibration found. Use calib data?")

        if not skip_calibrate:

            self.__lcd.lcd_clear()
            self.__lcd.lcd_display_string("Calibrating".center(20), 1)
            self.__lcd.lcd_display_string("Magnetometer...".center(20), 2)
            self.__lcd.lcd_display_string("Please wait".center(20), 4)

            time.sleep(5)

        utc_time = self.get_gps_time()
        if utc_time is False:
            utc_time = datetime.fromtimestamp(self.int_selection("Time", 0, 0, 24))

        while not self.yes_or_no(f"Time found: {utc_time.isoformat()[:-6]} Use?"):
            utc_time = datetime.fromtimestamp(self.int_selection("Time", 0, 0, 24))

    def yes_or_no(self, question: str):
        self.__lcd.lcd_clear()
        s = textwrap.fill(question, 20).split("\n")[0:3]

        for lcd_line, line in enumerate(s):
            self.__lcd.lcd_display_string(line.center(20), lcd_line+1)

        selection = False
        last_encoder = self.__wheel_encoder.position

        headers = ("   ", " > ")

        while True:
            pos = self.__wheel_encoder.position
            if pos != last_encoder:
                selection = not selection
                last_encoder = pos

            prompt = " " + "{}Yes".format(headers[int(selection)]).rjust(8) + " "
            prompt += ("  " + "{}No".format(headers[int(not selection)]).rjust(6) + "  ") # Ough
            self.__lcd.lcd_display_string(prompt, 4)

            if self.select_pressed():
                break
            time.sleep(0.1)

        return selection

    def get_gps_time(self):
        self.__lcd.lcd_clear()
        self.__lcd.lcd_display_string("Getting UTC Time...".center(20), 1)

        start_time = time.time()
        while True:
            self.__lcd.lcd_display_string("Sats visible: {}".format(0).center(20), 2)
            self.__lcd.lcd_display_string("  T: {}s".format(int(time.time() - start_time)), 3)
            self.__lcd.lcd_display_string("SELECT to specify...".center(20), 4)

            if self.select_pressed():
                return False

            time.sleep(0.1)

        # Unreachable
        return datetime.now(timezone.utc)

    def lcd_three_line_message(self, message: str):
        self.__lcd.lcd_clear()
        s = textwrap.fill(message, 20).split("\n")[0:3]

        for lcd_line, line in enumerate(s):
            self.__lcd.lcd_display_string(line.center(20), lcd_line + 1)

    def error(self, message: str):
        self.__lcd.lcd_clear()
        s = textwrap.fill(message, 20).split("\n")[0:4]

        for lcd_line, line in enumerate(s):
            self.__lcd.lcd_display_string(line.center(20), lcd_line+1)

        sys.exit(1)


    def specify_utc_time(self):
        utc_default = datetime.now(timezone.utc) # Based on rpi clock

        default = [
            ("Year", utc_default.year),
            ("Month", utc_default.month),
            ("Day", utc_default.day),
            ("Hour", utc_default.hour),
            ("Minute", utc_default.second)
        ]

    def list_selection(self):
        pass


    def int_selection(self, title, start, min, max):
        # Use wheel to adjust number
        self.__lcd.lcd_clear()

        last_encoder = self.__wheel_encoder.position

        selection = start

        while True:
            pos = self.__wheel_encoder.position
            if pos != last_encoder:
                selection += pos - last_encoder
                last_encoder = pos
                selection %= max - min
                selection += min

            self.__lcd.lcd_display_string(title.center(20), 1)
            self.__lcd.lcd_display_string(f"> {selection}", 3)
            self.__lcd.lcd_display_string("SELECT to choose".center(20), 4)

            if self.select_pressed():
                return selection

            time.sleep(0.1)


    def update(self):
        pass
