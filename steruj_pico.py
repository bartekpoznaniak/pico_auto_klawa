import serial
import time

PORT = "COM13"
BAUDRATE = 115200

ser = serial.Serial(PORT, BAUDRATE, timeout=1)
time.sleep(2)

print("Polaczono z Pico.")
print("Komendy: MOVE,x,y | CLICK | QUIT")

while True:
    command = input("> ").strip()

    if command == "":
        continue

    ser.write((command + "\n").encode("ascii"))

    if command == "QUIT":
        break

    time.sleep(0.2)

    while ser.in_waiting:
        print(ser.readline().decode("ascii", errors="ignore").strip())

ser.close()