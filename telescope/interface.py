from telescope.lib.lcddriver import lcd
from telescope.mount import Mount

import time
import textwrap
import sys
from copy import deepcopy
from typing import Any, Optional, Union, Tuple, List, Callable
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

        self.__mount = Mount(i2c_bus)

        self.__wheel_encoder_last_position = self.__wheel_encoder.position

    def encoder_diff(self):
        pos = self.__wheel_encoder.position
        val = pos - self.__wheel_encoder_last_position
        self.__wheel_encoder_last_position = pos
        return val

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
        if utc_time is None:
            utc_time = self.specify_utc_time()

        while utc_time is None or self.yes_or_no(f"Time found: {utc_time.isoformat()[:-6]} Use?"):
            utc_time = self.specify_utc_time()

        gps_coords = self.get_gps_coords()
        if gps_coords is None:
            gps_coords = (0.0, 0.0, 0.0)

        question = f"Use {gps_coords[0]:.2f} {'N' if gps_coords[0] >= 0.0 else 'S'}, " \
                f"{gps_coords[1]:.2f} {'E' if gps_coords[1] >= 0.0 else 'W'}, " \
                f"{gps_coords[2]}m?"

        while not self.yes_or_no(question):
            gps_coords = (self.int_selection("Choose coord", 0, -90, 90), 0.0, 0.0)

    def yes_or_no(self, question: str):
        self.__lcd.lcd_clear()
        s = textwrap.fill(question, 20).split("\n")[0:3]

        for lcd_line, line in enumerate(s):
            self.__lcd.lcd_display_string(line.center(20), lcd_line+1)

        selection = False

        headers = ("   ", " > ")

        while True:
            if self.encoder_diff():
                selection = not selection

            prompt = " " + "{}Yes".format(headers[int(selection)]).rjust(8) + " "
            prompt += ("  " + "{}No".format(headers[int(not selection)]).rjust(6) + "  ")  # Ough
            self.__lcd.lcd_display_string(prompt, 4)

            if self.select_pressed():
                break
            time.sleep(0.1)

        return selection

    def get_gps_time(self) -> Optional[datetime]:
        self.__lcd.lcd_clear()
        self.__lcd.lcd_display_string("Getting UTC Time...".center(20), 1)

        utc_time = None

        start_time = time.time()
        while True:
            sats, utc_time = self.__mount.poll_gps()[2:4]

            self.__lcd.lcd_display_string("Sats visible: {}".format(sats).center(20), 2)
            self.__lcd.lcd_display_string("  T: {}s".format(int(time.time() - start_time)), 3)
            self.__lcd.lcd_display_string("SELECT to specify...".center(20), 4)

            if utc_time:
                print(utc_time)
                return datetime(*utc_time[:6])

            if self.select_pressed():
                return None

            time.sleep(0.1)

    def get_gps_coords(self) -> Optional[Tuple[float, float, float]]:
        self.__lcd.lcd_clear()
        self.__lcd.lcd_display_string("Getting coordinates", 1)

        start_time = time.time()
        while True:
            fix, fix_3d, sats, utc_time, lat, latd, latm, long, longd, longm, height = self.__mount.poll_gps()

            self.__lcd.lcd_display_string("Sats: {} Fix: {}".format(sats, "Yes" if fix_3d else "No").center(20), 2)
            self.__lcd.lcd_display_string("  T: {}s".format(int(time.time() - start_time)), 3)
            self.__lcd.lcd_display_string("SELECT to specify...".center(20), 4)

            if fix_3d and lat is not None and long is not None and height is not None:
                return lat, long, height

            if self.select_pressed():
                return None

            time.sleep(0.1)

    def lcd_three_line_message(self, message: str):
        self.__lcd.lcd_clear()
        s = textwrap.fill(message, 20).split("\n")[0:3]

        for lcd_line, line in enumerate(s):
            self.__lcd.lcd_display_string(line.center(20), lcd_line + 1)

        self.__lcd.lcd_display_string("> Okay".center(20), 4)

        while True:
            if self.select_pressed():
                return

            time.sleep(0.1)

    def error(self, message: str):
        self.__lcd.lcd_clear()
        s = textwrap.fill(message, 20).split("\n")[0:4]

        for lcd_line, line in enumerate(s):
            self.__lcd.lcd_display_string(line.center(20), lcd_line+1)

        sys.exit(1)

    def specify_utc_time(self) -> Optional[datetime]:
        utc_default = datetime.now(timezone.utc) # Based on rpi clock

        default = [
            ["Year", utc_default.year, self.int_selection, ["Select Year...", utc_default.year, utc_default.year - 100, utc_default.year + 100]],
            ["Month", utc_default.month, self.int_selection, ["Select Month...", utc_default.month, 1, 12]],
            ["Day", utc_default.day, self.int_selection, ["Select Day...", utc_default.day, 1, 31]],
            ["Hour", utc_default.hour, self.int_selection, ["Select Hour...", utc_default.hour, 0, 23]],
            ["Minute", utc_default.minute, self.int_selection, ["Select Minute...", utc_default.minute, 0, 59]],
            ["Second", utc_default.second, self.int_selection, ["Select Second...", utc_default.second, 0, 59]]
        ]

        keys = self.list_selection("Set UTC Time...", default, 6)
        d = None
        try:
            d = datetime(keys["Year"], keys["Month"], keys["Day"], keys["Hour"], keys["Minute"], keys["Second"])
        except ValueError:
            self.lcd_three_line_message("Error: Invalid date!")
        return d


    def list_selection(self, prompt: str, options: List[List[Union[str, Any, Callable[..., Any], List[Any]]]], cutoff: int):
        # Requires list  of value names, the default value, the function to set a new value, and a list of arguments for that function
        self.__lcd.lcd_clear()

        # options = deepcopy(options)
        options = options[:]
        options.append(("Done"))

        selection = 0
        window = 0

        while True:
            signed_angle = self.encoder_diff()
            selection += signed_angle

            if self.up_pressed():
                selection -= 1

            if self.down_pressed():
                selection += 1

            selection %= len(options)

            if selection < window:
                window = max(0, selection)

            if selection > window + 2:
                window = min(selection-2, len(options))

            self.__lcd.lcd_display_string(prompt.center(20), 1)

            for i in range(window, min(window + 3, len(options))):
                s = ">" if i == selection else " "
                if i == len(options) - 1:
                    s += "Done".center(19)
                else:
                    s += options[i][0][:cutoff] + ":"
                    s += str(options[i][1]).rjust(20 - len(s))
                self.__lcd.lcd_display_string(s, i-window+2)

            if self.select_pressed() or self.right_pressed():
                if selection == len(options) - 1:
                    values = {}
                    for value in options[:-1]:
                        values[value[0]] = value[1]
                    return values

                options[selection][1] = options[selection][2](*options[selection][3])

    def int_selection(self, title, start, min, max):
        # Use wheel to adjust number
        self.__lcd.lcd_clear()


        # TODO: Fix weird starting values
        start_index = start - min
        last_encoder = -start_index-1

        width = max - min + 1
        while True:
            selection = last_encoder + self.encoder_diff()
            last_encoder = selection
            selection %= width
            selection = min + selection

            self.__lcd.lcd_display_string(title.center(20), 1)
            self.__lcd.lcd_display_string(f"> {selection}", 3)
            self.__lcd.lcd_display_string("SELECT to choose".center(20), 4)

            if self.select_pressed():
                return selection

            time.sleep(0.1)


    def update(self):
        pass
