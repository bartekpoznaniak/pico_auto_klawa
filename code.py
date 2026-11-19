import time
import board
import digitalio
import usb_hid
import usb_cdc
import rtc

SCREEN_WIDTH = 3840
SCREEN_HEIGHT = 2160

TARGET_X = 1920
TARGET_Y = 1080

REPORT_ID = 7

led = digitalio.DigitalInOut(board.LED)
led.switch_to_output(value=False)

button14 = digitalio.DigitalInOut(board.GP14)
button14.switch_to_input(pull=digitalio.Pull.UP)

button15 = digitalio.DigitalInOut(board.GP15)
button15.switch_to_input(pull=digitalio.Pull.UP)

mouse_device = None

for device in usb_hid.devices:
    if device.usage_page == 0x01 and device.usage == 0x02:
        mouse_device = device
        break

if mouse_device is None:
    raise RuntimeError(
        "Brak myszy HID. Sprawdz boot.py i odlacz/podlacz USB."
    )

report = bytearray(5)
time_buffer = bytearray()


def move_to(x, y):
    x = max(0, min(SCREEN_WIDTH - 1, int(x)))
    y = max(0, min(SCREEN_HEIGHT - 1, int(y)))

    hid_x = round(x * 32767 / (SCREEN_WIDTH - 1))
    hid_y = round(y * 32767 / (SCREEN_HEIGHT - 1))

    report[0] = 0  # Wszystkie przyciski myszy zwolnione.
    report[1] = hid_x & 0xFF
    report[2] = (hid_x >> 8) & 0xFF
    report[3] = hid_y & 0xFF
    report[4] = (hid_y >> 8) & 0xFF

    mouse_device.send_report(report, report_id=REPORT_ID)
    print("Pozycja docelowa: X =", x, "Y =", y)


def receive_time():
    global time_buffer

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
                continue

            values = [
                int(value)
                for value in message.split(",")[1:]
            ]

            if len(values) != 6:
                raise ValueError("Oczekiwano 6 liczb")

            year, month, day, hour, minute, second = values

            rtc.RTC().datetime = time.struct_time((
                year, month, day,
                hour, minute, second,
                -1, -1, -1
            ))

            print("Ustawiono czas:", time.localtime())
            port.write(b"OK\n")

        except Exception as error:
            print("Blad czasu:", error)
            port.write(b"ERROR\n")

    if len(time_buffer) > 256:
        time_buffer.clear()


for _ in range(3):
    led.value = True
    time.sleep(0.15)
    led.value = False
    time.sleep(0.15)

print("Mysz absolutna gotowa")
print("GP14: lewy gorny rog (0, 0)")
print("GP15: srodek ekranu (1920, 1080)")
print("Odbieranie czasu USB aktywne")

previous14 = False
previous15 = False

while True:
    receive_time()

    pressed14 = not button14.value
    pressed15 = not button15.value

    led.value = pressed14 or pressed15

    if pressed14 and not previous14:
        print("GP14: test punktu 100, 100")
        move_to(10, 10)
    # if pressed14 and not previous14:
    #     move_to(0, 0)

    if pressed15 and not previous15:
        move_to(TARGET_X, TARGET_Y)

    previous14 = pressed14
    previous15 = pressed15

    time.sleep(0.03)







# import usb_cdc
# import rtc
# import time
# import board
# import digitalio
# import usb_hid

# from adafruit_hid.mouse import Mouse

# # Cel liczony od lewego górnego rogu.
# # Na razie są to jednostki ruchu myszy, NIE piksele.
# TARGET_X = 500
# TARGET_Y = 300

# led = digitalio.DigitalInOut(board.LED)
# led.switch_to_output(value=False)

# button15 = digitalio.DigitalInOut(board.GP15)
# button15.switch_to_input(pull=digitalio.Pull.UP)

# button14 = digitalio.DigitalInOut(board.GP14)
# button14.switch_to_input(pull=digitalio.Pull.UP)

# mouse = Mouse(usb_hid.devices)


# def home():
#     print("Bazowanie: lewy gorny rog")

#     for _ in range(100):
#         mouse.move(x=-100, y=-100)
#         time.sleep(0.01)

#     time.sleep(0.3)
#     print("Bazowanie zakonczone")


# def move_from_home(x, y):
#     # Małe porcje ruchu, każda w zakresie raportu myszy.
#     while x != 0 or y != 0:
#         dx = max(-20, min(20, x))
#         dy = max(-20, min(20, y))

#         mouse.move(x=dx, y=dy)

#         x -= dx
#         y -= dy
#         time.sleep(0.01)


# def go_to(x, y):
#     home()
#     print("Dojazd do celu:", x, y)
#     move_from_home(x, y)
#     print("Gotowe")


# for _ in range(3):
#     led.value = True
#     time.sleep(0.15)
#     led.value = False
#     time.sleep(0.15)

# print("GP14: bazowanie")
# print("GP15: bazowanie + dojazd do celu")


# time_buffer = bytearray()


# def receive_time():
#     global time_buffer

#     port = usb_cdc.data
#     if port is None or not port.in_waiting:
#         return

#     data = port.read(port.in_waiting)
#     if not data:
#         return

#     time_buffer.extend(data)

#     while b"\n" in time_buffer:
#         line, _, time_buffer = time_buffer.partition(b"\n")
#         time_buffer = bytearray(time_buffer)

#         try:
#             message = line.decode("ascii").strip()

#             if message.startswith("TIME,"):
#                 values = [
#                     int(value)
#                     for value in message.split(",")[1:]
#                 ]

#                 if len(values) != 6:
#                     raise ValueError("Oczekiwano 6 liczb")

#                 year, month, day, hour, minute, second = values

#                 rtc.RTC().datetime = time.struct_time((
#                     year, month, day,
#                     hour, minute, second,
#                     -1, -1, -1
#                 ))

#                 print("Ustawiono czas:", time.localtime())
#                 port.write(b"OK\n")

#         except Exception as error:
#             print("Blad ustawiania czasu:", error)
#             port.write(b"ERROR\n")

#     if len(time_buffer) > 256:
#         time_buffer.clear()
# while True:
#     receive_time()
#     if not button14.value:
#         led.value = True
#         try:
#             home()
#         finally:
#             led.value = False

#         while not button14.value:
#             time.sleep(0.02)

#         time.sleep(0.05)

#     if not button15.value:
#         led.value = True
#         try:
#             go_to(TARGET_X, TARGET_Y)
#         finally:
#             led.value = False

#         while not button15.value:
#             time.sleep(0.02)

#         time.sleep(0.05)

#     time.sleep(0.01)