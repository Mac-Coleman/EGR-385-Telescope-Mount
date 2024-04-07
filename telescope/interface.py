from telescope.lib.lcddriver import lcd
from telescope.mount import Mount

from telescope import consts
from telescope.lib.angles import DMS, HMS
from telescope.lib.cache_helper import cache_magnetometer_offsets, get_cached_magnetometer_offsets, cache_path

import time
import textwrap
import sys
from copy import deepcopy
from typing import Any, Optional, Union, Tuple, List, Callable
from adafruit_seesaw import seesaw, digitalio, rotaryio
from datetime import datetime, timezone
import magnetismi.magnetismi as magnetic_api

from skyfield.api import Loader, wgs84, Star


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
        self.__wheel_right = digitalio.DigitalIO(self.__wheel, 5)

        self.__wheel_encoder = rotaryio.IncrementalEncoder(self.__wheel)

        self.__mount = Mount(i2c_bus)
        self.__wheel_encoder_last_position = self.__wheel_encoder.position

        self.__latitude_degrees = consts.MOUNT_VERNON_IOWA[0]
        self.__longitude_degrees = consts.MOUNT_VERNON_IOWA[1]
        self.__altitude_meters = consts.MOUNT_VERNON_IOWA[2]

        self.__skyfield_loader = Loader(cache_path() / "skyfield")
        self.__planets = self.__skyfield_loader("de421.bsp")

        self.__wgs84 = wgs84.latlon(self.__latitude_degrees, self.__longitude_degrees, self.__altitude_meters)
        self.__location = self.__planets["earth"] + self.__wgs84

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



        self.level_altitude()

        leveled = self.yes_or_no("Is the telescope level?")

        if not leveled:
            self.error("Error: Control Failure. Debug required.")

        offsets = get_cached_magnetometer_offsets()
        skip_calibrate = False

        if offsets is not None:
            skip_calibrate = self.yes_or_no("Calibration found. Use calib data?")

        if not skip_calibrate:
            offsets = self.calibrate_magnetometer()
            while offsets is None:
                offsets = self.calibrate_magnetometer()
            cache_magnetometer_offsets(offsets[0], offsets[1])

        self.__mount.set_offsets(offsets[0], offsets[1])

        utc_time = self.get_gps_time()
        if utc_time is None:
            utc_time = self.specify_utc_time()

        while utc_time is None or not self.yes_or_no(f"Time found: {utc_time.isoformat()[:-3]} Use?"):
            utc_time = self.specify_utc_time()

        gps_coords = self.get_gps_coords()
        if gps_coords is None:
            gps_coords = self.specify_coordinates()

        question = "Use {}, {}, {}m".format(gps_coords[0], gps_coords[1], gps_coords[2])

        while not self.yes_or_no(question):
            gps_coords = self.specify_coordinates()

        lat = gps_coords[0]
        lon = gps_coords[1]

        self.__latitude_degrees = lat.sign * (lat.deg + lat.min/60 + lat.sec/(60*60))
        self.__longitude_degrees = lon.sign * (lon.deg + lon.min / 60 + lon.sec / (60 * 60))
        self.__altitude_meters = gps_coords[2]

        self.__wgs84 = wgs84.latlon(self.__latitude_degrees, self.__longitude_degrees, self.__altitude_meters)
        self.__location = self.__planets["earth"] + self.__wgs84

        model = magnetic_api.Model(utc_time.year)
        date = magnetic_api.dti.date(utc_time.year, utc_time.month, utc_time.day)
        point = model.at(lat_dd=self.__latitude_degrees, lon_dd=self.__longitude_degrees, alt_ft=gps_coords[2] * consts.METERS_TO_FEET)
        mag_declination = point.dec

        use_calculated_declination = self.yes_or_no(f"Magnetic dec. found: {mag_declination:.2f}{chr(223)}. Use?")

        if not use_calculated_declination:
            md = self.dms_selection("Choose mag. dec...", DMS(angle=mag_declination))
            mag_declination = md.sign * (md.deg + md.min/60.0 + md.sec/(60*60))

        self.__mount.set_mag_declination(mag_declination)

        test_az = self.yes_or_no("Test azimuth / orientation?")
        if test_az:
            self.test_azimuth()

        while True:
            self.choose_main_action()

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

    def specify_coordinates(self) -> Optional[Tuple[DMS, DMS, float]]:

        def_lat = DMS(angle=consts.MOUNT_VERNON_IOWA[0])
        def_lon = DMS(angle=consts.MOUNT_VERNON_IOWA[1])
        def_alt = int(consts.MOUNT_VERNON_IOWA[2])

        default = [
            ["Lat", def_lat, self.dms_selection, ["Choose latitude...", def_lat]],
            ["Lon", def_lon, self.dms_selection, ["Choose longitude...", def_lon]],
            ["Alt", def_alt, self.int_selection, ["Choose altitude...", def_alt, -200, 10000]]
        ]

        keys = self.list_selection("Choose coordinates...", default, 3)
        return keys["Lat"], keys["Lon"], keys["Alt"]


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
                elif isinstance(options[i][1], float):
                    s += str(options[i][0])[:cutoff] + ":"
                    s += f"{options[i][1]:.1f}".rjust(20 - len(s))
                else:
                    s += str(options[i][0])[:cutoff] + ":"
                    s += str(options[i][1]).rjust(20 - len(s))
                self.__lcd.lcd_display_string(s, i-window+2)

            if self.select_pressed() or self.right_pressed():
                if selection == len(options) - 1:
                    values = {}
                    for value in options[:-1]:
                        values[value[0]] = value[1]
                    return values

                options[selection][1] = options[selection][2](*options[selection][3])

    def choose_from_list(self, prompt: str, options: List[List[Union[str, Callable[..., Any], List[Any]]]], exitable):
        # Requires list  of action names, the function to perform that action, and a list of arguments for that function
        self.__lcd.lcd_clear()

        # options = deepcopy(options)
        options = options[:]
        if exitable:
            options.append(["Back", None, []])

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

            self.__lcd.lcd_display_string(prompt.ljust(20), 1)

            for i in range(window, min(window + 3, len(options))):
                s = ">" if i == selection else " "
                if i == len(options) - 1 and exitable:
                    s += options[i][0].center(20 - len(s))
                else:
                    s += str(i) + "."
                    s += options[i][0].rjust(20 - len(s))
                self.__lcd.lcd_display_string(s, i-window+2)

            if self.select_pressed() or self.right_pressed():
                if selection == len(options) - 1 and exitable:
                    return None
                return options[selection][1](*options[selection][2])

    def int_selection(self, title, start, minimum, maximum):
        # Use wheel to adjust number
        self.__lcd.lcd_clear()

        start_index = start - minimum
        last_encoder = start_index

        width = maximum - minimum + 1
        while True:
            selection = last_encoder + self.encoder_diff()
            last_encoder = selection
            selection %= width
            selection = minimum + selection

            self.__lcd.lcd_display_string(title.center(20), 1)
            self.__lcd.lcd_display_string(f"> {selection}", 3)
            self.__lcd.lcd_display_string("SELECT to choose".center(20), 4)

            if self.select_pressed():
                return selection

            time.sleep(0.1)

    def float_selection(self, title, start, minimum, maximum, step):
        self.__lcd.lcd_clear()

        start_index = int(start - minimum/step)
        last_encoder = start_index
        width = (maximum - minimum) / step

        while True:
            selection = last_encoder + self.encoder_diff()
            last_encoder = selection
            selection %= width
            selection = minimum + (selection * step)

            self.__lcd.lcd_display_string(title.center(20), 1)
            self.__lcd.lcd_display_string(f"> {selection:.1f}", 3)
            self.__lcd.lcd_display_string("SELECT to choose".center(20), 4)

            if self.select_pressed():
                return selection

            time.sleep(0.1)

    def dms_selection(self, title, default_dms: DMS, dec=False):
        width = 179
        if dec:
            width = 89

        default = [
            ["Degrees", default_dms.deg, self.int_selection, ["Choose degrees...", default_dms.deg, -width, width]],
            ["Minutes", default_dms.min, self.int_selection, ["Choose minutes...", default_dms.min, 0, 59]],
            ["Seconds", int(default_dms.sec), self.int_selection, ["Choose seconds...", int(default_dms.sec), 0, 59]]
        ]

        keys = self.list_selection("Choose angle...", default, 7)
        dms = None
        try:
            dms = DMS(d=keys["Degrees"], m=keys["Minutes"], s=keys["Seconds"])
        except ValueError as e:
            self.lcd_three_line_message("Error: invalid angle")
        return dms

    def level_altitude(self):
        self.__lcd.lcd_clear()
        self.__lcd.lcd_display_string("Zeroing altitude".center(20), 1)
        self.__lcd.lcd_display_string("Please wait".center(20), 4)

        while not self.__mount.level_altitude():
            self.__lcd.lcd_display_string((f"{self.__mount.get_altitude():.1f}" + chr(223)).center(20), 3)

        self.__lcd.lcd_clear()

        while not self.select_pressed():
            direction = 1 if self.up_pressed() else None
            direction = -1 if self.down_pressed() else direction

            if direction is not None:
                self.__mount.spin_altitude(direction * 300)
            else:
                self.__mount.stop()

            self.__lcd.lcd_display_string("Use UP/DOWN to level".center(20), 1)
            self.__lcd.lcd_display_string("the telescope.".center(20), 2)
            self.__lcd.lcd_display_string((f"{self.__mount.get_altitude():.1f}" + chr(223)).center(20), 3)
            self.__lcd.lcd_display_string("SELECT when ready".center(20), 4)

    def calibrate_magnetometer(self):
        self.lcd_three_line_message("Press SELECT when the telescope has fully rotated.")
        self.__lcd.lcd_clear()
        self.__lcd.lcd_display_string("Calibrating".center(20), 2)

        mag_x, mag_y, mag_z = self.__mount.get_magnetic()
        max_x = min_x = mag_x
        max_y = min_y = mag_y
        max_z = min_z = mag_z

        offset_x = (max_x + min_x) / 2
        offset_y = (max_y + min_y) / 2
        offset_z = (max_z + min_z) / 2

        from telescope.consts import AZ_MAX_SPEED
        for i in range(10, AZ_MAX_SPEED+1, 10):
            self.__mount.spin_azimuth(i)
            mag_x, mag_y, mag_z = self.__mount.get_magnetic()
            min_x = min(mag_x, min_x)
            min_y = min(mag_y, min_y)
            min_z = min(mag_z, min_z)
            max_x = max(mag_x, max_x)
            max_y = max(mag_y, max_y)
            max_z = max(mag_z, max_z)
            time.sleep(0.005)

        while True:
            self.__mount.spin_azimuth(AZ_MAX_SPEED)
            mag_x, mag_y, mag_z = self.__mount.get_magnetic()
            min_x = min(mag_x, min_x)
            min_y = min(mag_y, min_y)
            min_z = min(mag_z, min_z)
            max_x = max(mag_x, max_x)
            max_y = max(mag_y, max_y)
            max_z = max(mag_z, max_z)

            offset_x = (max_x + min_x) / 2
            offset_y = (max_y + min_y) / 2
            offset_z = (max_z + min_z) / 2

            field_x = (max_x - min_x) / 2
            field_y = (max_y - min_y) / 2
            field_z = (max_z - min_z) / 2

            self.__lcd.lcd_display_string("Calibrating...".center(20), 1)
            self.__lcd.lcd_display_string(f"X: {offset_x:.2f}".center(20), 3)
            self.__lcd.lcd_display_string(f"Y: {offset_y:.2f}".center(20), 4)

            if self.select_pressed():
                break

        for i in range(AZ_MAX_SPEED, 10, -10):
            self.__mount.spin_azimuth(i)
            time.sleep(0.005)

        self.__mount.stop()
        use_offset = self.yes_or_no(f"Offset found: X={offset_x:.2f}, Y={offset_y:.2f}. Use?")

        return offset_x, offset_y if use_offset else None

    def test_azimuth(self):
        self.__lcd.lcd_clear()
        self.__lcd.lcd_display_string("Testing orientation".center(20), 2)

        from telescope.consts import AZ_MAX_SPEED

        for i in range(10, AZ_MAX_SPEED+1, 10):
            self.__mount.spin_azimuth(i)
            time.sleep(0.005)

        self.__lcd.lcd_clear()

        while True:
            self.__mount.spin_azimuth(AZ_MAX_SPEED)
            h = self.__mount.get_heading()
            self.__lcd.lcd_display_string("Heading:".center(20), 2)
            self.__lcd.lcd_display_string(f"{h:.1f}{chr(223)}".center(20), 3)
            time.sleep(0.005)

            if self.select_pressed():
                break

        for i in range(AZ_MAX_SPEED, 10, -10):
            self.__mount.spin_azimuth(i)
            time.sleep(0.005)

        self.__mount.stop()

    def track_sun(self):
        from skyfield.api import Star, Loader, wgs84

        p = cache_path() / "skyfield"
        p.mkdir(parents=True, exist_ok=True)

        load = Loader(p)
        planets = load('de421.bsp')
        earth = planets["earth"]

        object = planets["sun"]  # Star(ra_hours=(18, 36, 56.33635), dec_degrees=(38, 47, 01.2802))

        ts = load.timescale()
        location = earth + wgs84.latlon(self.__latitude_degrees, self.__longitude_degrees, self.__altitude_meters)

        update_count = 0
        while True:
            t = ts.now()

            apparent = location.at(t).observe(object).apparent()
            alt, az, dist = apparent.altaz()

            self.__mount.set_setpoint(alt.degrees, az.degrees)
            _, _, _, sv, sp, speed = self.__mount.go_to_setpoint()

            update_count += 1

            if update_count % 50 == 0:
                self.__lcd.lcd_display_string(f"S:{sv:.2f}", 1)
                self.__lcd.lcd_display_string(f"V:{sp:.2f}", 2)
                self.__lcd.lcd_display_string(f"E:{sp - sv:.2f}", 3)
                self.__lcd.lcd_display_string(f"Sp:{speed:.2f}", 4)

    def choose_main_action(self):
        actions = [
            ["Objects", self.all_objects, [False]],
            ["Favorites", self.all_objects, [True]],
            ["Coordinates", None, []],
            ["Manual", self.manual, []],
            ["Settings", self.settings, []]
        ]

        return self.choose_from_list("Choose Action", actions, False)

    def all_objects(self, favorites_only):
        actions = [
            ["Planets", None, [favorites_only]],
            ["Stars", None, [favorites_only]],
            ["Messier", None, [favorites_only]],
            ["Satellites", None, [favorites_only]],
        ]

        title = "Favorites" if favorites_only else "Type"
        return self.choose_from_list(title, actions, True)

    def settings(self):
        actions = [
            ["Accelerometer", None, []],
            ["Magnetometer", None, []],
            ["Location", None, []],
            ["Time", None, []],
            ["Declination", None, []],
        ]

        return self.choose_from_list("Settings", actions, True)

    def manual(self):
        level = 10
        self.encoder_diff()

        while True:

            level += self.encoder_diff()

            if level > 10:
                level = 10
            if level < 1:
                level = 1

            az_speed = consts.AZ_MAX_SPEED * level/10
            al_speed = consts.AL_MAX_SPEED * level/10

            az_dir = 1 if self.right_pressed() else 0
            az_dir = -1 if self.left_pressed() else az_dir

            al_dir = 1 if self.up_pressed() else 0
            al_dir = -1 if self.down_pressed() else al_dir

            self.__mount.spin_azimuth(az_speed * az_dir)
            self.__mount.spin_altitude(al_speed * al_dir)

            self.__lcd.lcd_display_string("Manual" + f"{level}".rjust(14), 1)
            self.__lcd.lcd_display_string(f"Al: {DMS(angle=self.__mount.get_altitude())}", 2)
            self.__lcd.lcd_display_string(f"Az: {DMS(angle=self.__mount.get_heading())}", 3)
            self.__lcd.lcd_display_string("SELECT to quit".center(20), 4)

            if self.select_pressed():
                break



    def update(self):
        pass
