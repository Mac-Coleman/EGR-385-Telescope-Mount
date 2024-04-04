import smbus

bus = smbus.SMBus(1)
keyboard_address = 0x30

def check_input():
    key = bus.read_byte_data(keyboard_address, 0)

    c = None
    if key != 0:
        c = chr(key)

    return c

last_char = None

def debounced_check():
    global last_char

    k = check_input()
    if k == last_char:
        last_char = k
        k = check_input()
        return None

    last_char = k
    return k

def wait_for_input():
    global last_char
    k = check_input()

    while k == None or k == last_char:
        last_char = k
        k = check_input()

    last_char = k

    return k

def input_prompt():

    output_string = ""

    cancel = 0
    while True:
        k = wait_for_input()

        if k == "#":
            break
        if k == "*":
            cancel += 1
            output_string += "."
        else:
            output_string += k

        print(output_string)

        if cancel >= 2:
            return None

    return float(output_string)

while True:
    f = input_prompt()

    if f == None:
        print("Entry canceled.")
    else:
        print("The float: " + str(f))
