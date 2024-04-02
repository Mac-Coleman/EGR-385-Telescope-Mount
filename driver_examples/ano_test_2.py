import board
import time
from adafruit_seesaw import seesaw, rotaryio, digitalio

i2c = board.I2C()
seesaw = seesaw.Seesaw(i2c, addr=0x49)
seesaw_product = (seesaw.get_version() >> 16) & 0xFFFF
print("Found product: ", seesaw_product)

if seesaw_product != 5740:
    raise ValueError("Wrong seesaw model!")

seesaw.pin_mode(1, seesaw.INPUT_PULLUP)
seesaw.pin_mode(2, seesaw.INPUT_PULLUP)
seesaw.pin_mode(3, seesaw.INPUT_PULLUP)
seesaw.pin_mode(4, seesaw.INPUT_PULLUP)
seesaw.pin_mode(5, seesaw.INPUT_PULLUP)

select = digitalio.DigitalIO(seesaw, 1)
select_held = False
up = digitalio.DigitalIO(seesaw, 2)
up_held = False
left = digitalio.DigitalIO(seesaw, 3)
left_held = False
down = digitalio.DigitalIO(seesaw, 4)
down_held = False
right = digitalio.DigitalIO(seesaw, 5)
right_held = False

encoder = rotaryio.IncrementalEncoder(seesaw)
last_position = None

buttons = [select, up, left, down, right]
button_names = ["Select", "Up", "Left", "Down", "Right"]
button_states = [select_held, up_held, left_held, down_held, right_held]

while True:
    position = encoder.position
    print(str(select.value).rjust(5), str(up.value).rjust(5), str(left.value).rjust(5), str(down.value).rjust(5), str(right.value).rjust(5))
    time.sleep(0.1)
