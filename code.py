import time
import board
import busio
import digitalio
import usb_hid
import microcontroller
import adafruit_ssd1306
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

DELAY_S = 12
TRIES = 8
AFTER_RESET_S = 3
VERSION = 1.105

btn = digitalio.DigitalInOut(board.GP14)
btn.switch_to_input(pull=digitalio.Pull.UP)

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

i2c = busio.I2C(scl=board.GP5, sda=board.GP4, frequency=100000)
display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

kbd = Keyboard(usb_hid.devices)

boots = (microcontroller.nvm[1] + 1) % 256
microcontroller.nvm[1] = boots
start = time.monotonic()

def show(line1, line2=""):
    display.fill(0)
    display.text(line1, 0, 0, 1)
    display.text(line2, 0, 14, 1)
    display.text("Up: {} s".format(int(time.monotonic() - start)), 0, 40, 1)
    display.text("Starty: {}".format(boots), 0, 54, 1)
    #display.text("v" + VERSION, 128 - 6 * (len(VERSION) + 1), 54, 1)

    ver = "v" + str(VERSION)
    display.text(ver, 128 - 6 * len(ver), 54, 1)
    
    display.show()

def send_wake():
    for i in range(TRIES):
        show("Wysylam Shift", "{}/{}".format(i + 1, TRIES))
        try:
            kbd.send(Keycode.SHIFT)
        except Exception:
            pass
        time.sleep(1)
    led.value = True

if microcontroller.nvm[0] == 1:
    microcontroller.nvm[0] = 0
    show("Po resecie", "czekam chwile")
    time.sleep(AFTER_RESET_S)
    send_wake()
    show("Wyslane", "koniec")
else:
    while btn.value:
        show("Czekam na GP14", "Czas: {} s".format(DELAY_S))
        time.sleep(0.2)

    end = time.monotonic() + DELAY_S
    while time.monotonic() < end:
        left = int(end - time.monotonic())
        led.value = not led.value
        show("Odliczam", "Zostalo: {} s".format(left))
        time.sleep(0.5)
    led.value = False

    show("Restart Pico", "")
    microcontroller.nvm[0] = 1
    microcontroller.reset()

while True:
    show("Wyslane", "koniec")
    time.sleep(1)