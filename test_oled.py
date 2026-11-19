import time
import board
import busio
import adafruit_ssd1306

i2c = busio.I2C(
    scl=board.GP5,
    sda=board.GP4,
    frequency=100_000
)

display = adafruit_ssd1306.SSD1306_I2C(
    128, 64,
    i2c,
    addr=0x3C
)

display.fill(0)
display.show()

print("Test ekranu: prostokat i migajacy kwadrat")

# Ramka.
display.hline(0, 0, 128, 1)
display.hline(0, 63, 128, 1)
display.vline(0, 0, 64, 1)
display.vline(127, 0, 64, 1)

state = False

while True:
    state = not state
    display.fill_rect(54, 22, 20, 20, int(state))
    display.show()
    time.sleep(0.5)
