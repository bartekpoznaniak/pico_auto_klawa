import time
import board
import busio

time.sleep(1)

i2c = busio.I2C(
    scl=board.GP5,
    sda=board.GP4,
    frequency=100_000
)

while not i2c.try_lock():
    time.sleep(0.01)

try:
    for _ in range(3):
        print("Adresy:", [hex(a) for a in i2c.scan()])
        time.sleep(0.5)
finally:
    i2c.unlock()
    i2c.deinit()