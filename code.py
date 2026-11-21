import time
import board
import busio
import digitalio
import usb_hid
import usb_cdc
import rtc
import adafruit_ssd1306
import microcontroller
import scriptengine
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS




SCREEN_WIDTH = 3840
SCREEN_HEIGHT = 2160

VERSION = 1.19

REPORT_ID = 7
WAKE_DELAY_S = 1200
WAKE_TRIES = 8
AFTER_RESET_S = 3

led = digitalio.DigitalInOut(board.LED)
led.switch_to_output(value=False)

button14 = digitalio.DigitalInOut(board.GP14)
button14.switch_to_input(pull=digitalio.Pull.UP)

i2c = busio.I2C(scl=board.GP5, sda=board.GP4, frequency=100_000)
display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

mouse_device = None
for device in usb_hid.devices:
    if device.usage_page == 0x01 and device.usage == 0x02:
        mouse_device = device
        break

keyboard = Keyboard(usb_hid.devices)

layout = KeyboardLayoutUS(keyboard)

report = bytearray(5)
buttons = 0
time_buffer = bytearray()
time_synced = False
wake_at = None
wake_delay = WAKE_DELAY_S
last_rx = "---"
status = "Gotowy"
running = True


def move_to(x, y):
    global status
    if mouse_device is None:
        status = "Brak myszy"
        return
    x = max(0, min(SCREEN_WIDTH - 1, int(x)))
    y = max(0, min(SCREEN_HEIGHT - 1, int(y)))
    hid_x = round(x * 32767 / (SCREEN_WIDTH - 1))
    hid_y = round(y * 32767 / (SCREEN_HEIGHT - 1))
    report[0] = buttons
    report[1] = hid_x & 0xFF
    report[2] = (hid_x >> 8) & 0xFF
    report[3] = hid_y & 0xFF
    report[4] = (hid_y >> 8) & 0xFF
    mouse_device.send_report(report, report_id=REPORT_ID)
    status = "Ruch wyslany"


def click_left():
    global status
    if mouse_device is None:
        status = "Brak myszy"
        return
    report[0] = 0x01
    report[1] = report[2] = report[3] = report[4] = 0
    mouse_device.send_report(report, report_id=REPORT_ID)
    time.sleep(0.05)
    report[0] = 0
    mouse_device.send_report(report, report_id=REPORT_ID)
    status = "Klik lewy"

def mouse_down():
    global status, buttons
    if mouse_device is None:
        status = "Brak myszy"
        return
    buttons = 1
    report[0] = 0x01
    mouse_device.send_report(report, report_id=REPORT_ID)
    status = "Mysz wcisnieta"

def mouse_up():
    global status
    if mouse_device is None:
        status = "Brak myszy"
        return
    report[0] = 0
    mouse_device.send_report(report, report_id=REPORT_ID)
    status = "Mysz puszczona"

KEY_ALIASES = {"CTRL": "CONTROL", "WIN": "GUI", "ESC": "ESCAPE"}

def type_text(text):
    global status
    try:
        layout.write(text)
        status = "Wpisano tekst"
    except Exception as error:
        status = "Blad TYPE"
        print("Blad TYPE:", error)

def press_keys(names):
    global status
    try:
        codes = []
        for name in names:
            name = KEY_ALIASES.get(name, name)
            codes.append(getattr(Keycode, name))
        keyboard.send(*codes)
        status = "Klawisz " + "+".join(names)
    except Exception as error:
        status = "Blad KEY"
        print("Blad KEY:", error)

def drag(x1, y1, x2, y2, steps=20):
    global status
    move_to(x1, y1)
    time.sleep(0.15)
    mouse_down()
    time.sleep(0.15)
    for i in range(1, steps + 1):
        move_to(x1 + (x2 - x1) * i / steps,
                y1 + (y2 - y1) * i / steps)
        time.sleep(0.01)
    time.sleep(0.15)
    mouse_up()
    status = "Drag OK"

def run_show(text):
    global status
    status = text[:21]
    update_display()

HANDLERS = {
    "move": move_to,
    "click": click_left,
    "down": mouse_down,
    "up": mouse_up,
    "drag": drag,
    "type": type_text,
    "keys": press_keys,
}

def update_display():
    display.fill(0)
    display.text("PICO HID", 0, 0, 1)
    ver = "({})".format(VERSION)
    display.text(ver, 128 - 6 * len(ver), 0, 1)

    if time_synced:
        now = time.localtime()
        display.text("{:02d}:{:02d}:{:02d}".format(
            now.tm_hour, now.tm_min, now.tm_sec), 0, 15, 1)
        display.text("SYNC OK", 66, 15, 1)
    else:
        display.text("--:--:-- BRAK SYNC", 0, 15, 1)

    display.text("Rx: " + last_rx, 0, 28, 1)

    if wake_at is not None:
        left = int(wake_at - time.monotonic()) + 1
        display.text("Wake za {} s".format(max(left, 0)), 0, 40, 1)
    else:
        display.text(status, 0, 40, 1)

    display.text("14: wake", 0, 54, 1)
    display.show()


def wake_host():
    global status
    for i in range(WAKE_TRIES):
        status = "Shift {}/{}".format(i + 1, WAKE_TRIES)
        update_display()
        try:
            keyboard.send(Keycode.SHIFT)
        except Exception as error:
            print("Blad Shift:", error)
        time.sleep(1)
    status = "Wake wyslany"


def handle_command(message):
    global running, status, wake_delay, last_rx
    last_rx = message[:14]

    if message.startswith("MOVE,"):
        try:
            parts = message.split(",")
            move_to(int(parts[1]), int(parts[2]))
        except Exception as error:
            status = "Blad MOVE"
            print("Blad MOVE:", error)
    elif message == "CLICK":
        click_left()


    elif message.startswith("WAKE,"):
        try:
            wake_delay = int(message.split(",")[1])
            status = "Opoznienie {} s".format(wake_delay)
        except Exception:
            status = "Blad WAKE"


    elif message == "QUIT":
        print("Zamykam")
        running = False

    elif message.startswith("RUN,"):
        name = message.split(",")[1].strip()
        scriptengine.run("/scripts/" + name + ".txt", HANDLERS, run_show)

def receive_time():
    global time_buffer, time_synced, status
    port = usb_cdc.data
    if port is None or not port.in_waiting:
        return

    data = port.read(port.in_waiting)
    if not data:
        return

    time_buffer.extend(data)

    while b"\n" in time_buffer:
        line, _, remaining = time_buffer.partition(b"\n")
        time_buffer = bytearray(remaining)

        try:
            message = line.decode("ascii").strip()

            if not message.startswith("TIME,"):
                handle_command(message)
                continue

            values = [int(v) for v in message.split(",")[1:]]
            if len(values) != 6:
                raise ValueError("Oczekiwano 6 liczb")

            year, month, day, hour, minute, second = values
            if not (2000 <= year <= 2099 and 1 <= month <= 12
                    and 1 <= day <= 31 and 0 <= hour <= 23
                    and 0 <= minute <= 59 and 0 <= second <= 59):
                raise ValueError("Niepoprawny zakres daty/czasu")

            rtc.RTC().datetime = time.struct_time(
                (year, month, day, hour, minute, second, -1, -1, -1))
            time_synced = True
            status = "Czas ustawiony"
            port.write(b"OK\n")

        except Exception as error:
            status = "Blad czasu"
            print("Blad czasu:", error)
            port.write(b"ERROR\n")

    if len(time_buffer) > 256:
        time_buffer.clear()


for _ in range(3):
    led.value = True
    time.sleep(0.15)
    led.value = False
    time.sleep(0.15)

print("Pico HID", VERSION, "- komendy: MOVE,x,y | CLICK | WAKE,s | QUIT")

previous14 = False
last_refresh = -1.0

if microcontroller.nvm[0] == 1:
    microcontroller.nvm[0] = 0
    status = "Po resecie"
    update_display()
    time.sleep(AFTER_RESET_S)
    wake_host()

while running:
    receive_time()

    pressed14 = not button14.value
    led.value = pressed14

    if pressed14 and not previous14:
        wake_at = time.monotonic() + wake_delay
        status = "Wake zaplanowany"
    previous14 = pressed14

    if wake_at is not None and time.monotonic() >= wake_at:
        wake_at = None
        status = "Restart Pico"
        update_display()
        microcontroller.nvm[0] = 1
        microcontroller.reset()

    # if wake_at is not None and time.monotonic() >= wake_at:
    #     wake_at = None
    #     status = "Budze PC"
    #     update_display()
    #     wake_host()

    now_t = time.monotonic()
    if now_t - last_refresh >= 0.25:
        update_display()
        last_refresh = now_t

    time.sleep(0.02)