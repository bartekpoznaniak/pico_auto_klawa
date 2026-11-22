import time
import json
import storage
# import supervisor
# supervisor.disable_autoreload()
import board
import busio
import os
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

VERSION = "1.241"

REPORT_ID = 7
WAKE_DELAY_S = 12
WAKE_TRIES = 8
AFTER_RESET_S = 3

led = digitalio.DigitalInOut(board.LED)
led.switch_to_output(value=False)

button14 = digitalio.DigitalInOut(board.GP14)
button14.switch_to_input(pull=digitalio.Pull.UP)

button15 = digitalio.DigitalInOut(board.GP15)
button15.switch_to_input(pull=digitalio.Pull.UP)

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
    global status, buttons
    if mouse_device is None:
        status = "Brak myszy"
        return
    buttons = 0
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

def load_schedule():
    entries = []
    try:
        with open("/schedules/harmonogram.txt", "r") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) < 2:
                    continue
                try:
                    hour, minute = parts[0].split(":")
                    hour = int(hour)
                    minute = int(minute)
                except ValueError:
                    continue
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    entries.append((hour, minute, " ".join(parts[1:])))
    except OSError:
        pass
    return entries



def save_schedule_entry(index, entry):
    print("SAVE:", index, entry)
    path = "/schedules/harmonogram.txt"

    with open(path, "r") as file:
        lines = file.readlines()

    valid_index = 0
    found = False

    for line_index, line in enumerate(lines):
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        parts = stripped.split()

        if len(parts) < 2:
            continue

        try:
            old_hour, old_minute = parts[0].split(":")
            old_hour = int(old_hour)
            old_minute = int(old_minute)
        except ValueError:
            continue

        if not (0 <= old_hour <= 23 and 0 <= old_minute <= 59):
            continue

        if valid_index == index:
            lines[line_index] = "{:02d}:{:02d} {}\n".format(
                entry[0], entry[1], entry[2]
            )
            found = True
            break

        valid_index += 1

    if not found:
        raise ValueError("Brak wpisu")


    temp_path = path + ".tmp"

    with open(temp_path, "w") as file:
        file.write("".join(lines))
        file.flush()
        os.sync()

    with open(path, "r") as check_file:
        print("PO ZAPISIE:", check_file.read())        

    try:
        os.remove(path)
    except OSError:
        pass

    os.rename(temp_path, path)
    os.sync()

   
def prepare_schedule_reset(name):
    payload = json.dumps({"macro": name}).encode("utf-8")
    if len(payload) > len(microcontroller.nvm) - 4:
        raise ValueError("Za dluga nazwa")
    record = bytes((2, 0, len(payload) & 255, len(payload) >> 8)) + payload
    microcontroller.nvm[:len(record)] = record
    microcontroller.reset()


def run_scheduled_macro(name):
    global status
    result = "Blad makra planu"
    try:
        scriptengine.run("/scripts/" + name + ".txt", HANDLERS, run_show)
        result = "Plan wykonany"
    except Exception as error:
        print("Blad makra:", error)
    finally:
        keyboard.release_all()
        mouse_up()
    status = result


def list_scripts():
    try:
        return sorted(
            name[:-4]
            for name in os.listdir("/scripts")
            if name.lower().endswith(".txt")
        )
    except OSError as error:
        print("Blad odczytu /scripts:", error)
        return []

screen = "home"
menu_index = 0
menu_note = ""
service_mode = storage.getmount("/").readonly
menu_items = (("URUCHOM MAKRO", "HARMONOGRAM", "ZAKONCZ SERWIS", "< POWROT")
              if service_mode else ("URUCHOM MAKRO", "HARMONOGRAM", "< POWROT"))

script_names = []
script_index = 0
selected_script = ""

schedule_entries = []
schedule_index = 0
last_schedule_fire = ""
schedule_enabled = False
active_schedule = None
schedule_wake = True
pending_wake = True
edit_hour = 0
edit_minute = 0
edit_active = False
plan_action_index = 0
plan_actions = ("WYLACZ PLAN", "ZMIEN GODZINE", "< POWROT")


def draw_menu():
    display.fill(0)
    display.text(("SERWIS " if service_mode else "MENU ") + VERSION, 0, 0, 1)
    start = max(0, menu_index - 2)
    for offset, label in enumerate(menu_items[start:start + 3]):
        prefix = "> " if start + offset == menu_index else "  "
        display.text(prefix + label, 0, 14 + offset * 11, 1)
    display.text(menu_note or "1: OK 2: dalej", 0, 56, 1)
    display.show()


def draw_scripts():
    display.fill(0)
    display.text("MAKRA", 0, 0, 1)

    if not script_names:
        display.text("BRAK MAKR", 0, 20, 1)
        display.text("1: Powrot", 0, 56, 1)
        display.show()
        return

    for offset in range(3):
        index = script_index + offset
        if index >= len(script_names):
            break

        name = script_names[index]
        prefix = "> " if index == script_index else "  "
        display.text(prefix + name[:18], 0, 14 + offset * 11, 1)

    display.text("1: OK  2: dalej", 0, 56, 1)
    display.show()

def draw_confirm():
    display.fill(0)
    display.text("URUCHOMIC?", 0, 0, 1)
    display.text(selected_script[:18], 0, 20, 1)
    display.text("1: TAK  2: NIE", 0, 56, 1)
    display.show()

def draw_schedule_confirm():
    display.fill(0)
    display.text("WLACZYC PLAN?", 0, 0, 1)
    hour, minute, name = schedule_entries[schedule_index]
    display.text("{:02d}:{:02d} {}".format(hour, minute, name[:12]), 0, 16, 1)
    display.text("Wybudzanie: " + ("TAK" if pending_wake else "NIE"), 0, 32, 1)
    display.text("1: TAK 2: NIE", 0, 56, 1)
    display.show()


def draw_schedule_wake():
    display.fill(0)
    display.text("WYBUDZANIE?", 0, 0, 1)
    display.text("Przed makrem", 0, 20, 1)
    display.text("1: TAK 2: NIE", 0, 56, 1)
    display.show()


def draw_schedule_active():
    display.fill(0)
    display.text("PLAN ON " + ("(W+)" if schedule_wake else "(W-)"), 0, 0, 1)
    hour, minute, name = active_schedule
    display.text("{:02d}:{:02d} {}".format(hour, minute, name[:12]), 0, 12, 1)
    for index, label in enumerate(plan_actions):
        display.text((">" if index == plan_action_index else " ") + label,
                     0, 25 + index * 10, 1)
    display.text("1: OK 2: dalej", 0, 56, 1)
    display.show()


def draw_schedule_edit():
    display.fill(0)
    display.text("USTAW CZAS", 0, 0, 1)
    display.text("{:02d}:{:02d}".format(edit_hour, edit_minute), 0, 18, 1)
    display.text("Godzina" if screen == "edit_hour" else "Minuta", 0, 32, 1)
    display.text("1: + 2: dalej", 0, 56, 1)
    display.show()


def draw_service_exit():
    display.fill(0)
    display.text("ZAKONCZ SERWIS?", 0, 0, 1)
    display.text("Wysun CIRCUITPY", 0, 15, 1)
    display.text("w Windows!", 0, 26, 1)
    display.text("Po resecie: SYNC", 0, 39, 1)
    display.text("1: RESET 2: NIE", 0, 56, 1)
    display.show()


def draw_harmonogram():
    display.fill(0)
    display.text("HARMONOGRAM", 0, 0, 1)

    if not schedule_entries:
        display.text("BRAK WPISOW", 0, 20, 1)
        display.text("1+2: Powrot", 0, 56, 1)
        display.show()
        return

    for offset in range(3):
        index = schedule_index + offset
        if index >= len(schedule_entries):
            break
        hour, minute, name = schedule_entries[index]
        prefix = "> " if index == schedule_index else "  "
        display.text(prefix + "{:02d}:{:02d} {}".format(hour, minute, name[:12]), 0, 14 + offset * 11, 1)

    display.text("1: teraz  2: dalej", 0, 56, 1)
    display.show()

def update_display():
    if screen == "service_exit":
        draw_service_exit()
        return
    if screen in ("edit_hour", "edit_minute"):
        draw_schedule_edit()
        return


    if screen == "menu":
        draw_menu()
        return

    if screen == "scripts":
        draw_scripts()
        return

    if screen == "confirm":
        draw_confirm()
        return
    
    if screen == "schedule_wake":
        draw_schedule_wake()
        return

    if screen == "schedule_confirm":
        draw_schedule_confirm()
        return

    if screen == "schedule_active":
        draw_schedule_active()
        return

    if screen == "harmonogram":
        draw_harmonogram()
        return
    
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

    display.text("SERWIS: zapis z PC" if service_mode else
                 (("PLAN ON " + ("(W+)" if schedule_wake else "(W-)"))
                  if schedule_enabled else "PLAN OFF"), 0, 28, 1)

    if wake_at is not None:
        left = int(wake_at - time.monotonic()) + 1
        display.text("Wake za {} s".format(max(left, 0)), 0, 40, 1)
    else:
        display.text(status, 0, 40, 1)

    if wake_at is not None:
        display.text("1: wake  2: anuluj", 0, 54, 1)
    else:
        display.text("1:wake 1+2:menu", 0, 54, 1)

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
previous15 = False
both_latched = False
buttons_changed_at = time.monotonic()
last_refresh = -1.0

boot_reason = microcontroller.nvm[0]
if boot_reason in (1, 2):
    pending_name = None
    if boot_reason == 2:
        try:
            size = microcontroller.nvm[2] | (microcontroller.nvm[3] << 8)
            if not 0 < size <= len(microcontroller.nvm) - 4:
                raise ValueError("Niepoprawny rekord")
            pending_name = json.loads(bytes(microcontroller.nvm[4:4 + size]).decode("utf-8"))["macro"]
        except Exception as error:
            status = "Blad zadania resetu"
            print("Blad zadania resetu:", error)
    microcontroller.nvm[0] = 0
    if boot_reason == 1 or pending_name is not None:
        status = "Po resecie"
        update_display()
        time.sleep(AFTER_RESET_S)
        wake_host()
        if pending_name is not None:
            status = "Czekam na komputer"
            update_display()
            time.sleep(WAKE_DELAY_S)
            run_scheduled_macro(pending_name)

while running:
    receive_time()



    pressed14 = not button14.value
    pressed15 = not button15.value
    led.value = pressed14 or pressed15

    if (pressed14, pressed15) != (previous14, previous15):
        if time.monotonic() - buttons_changed_at >= 0.05:

            if pressed14 and pressed15:
                both_latched = True
                screen = "menu"
                menu_index = 0
                menu_note = ""

            elif both_latched:
                if not pressed14 and not pressed15:
                    both_latched = False

            else:
                released14 = previous14 and not pressed14
                released15 = previous15 and not pressed15

                if screen == "menu":
                    if released15:
                        menu_index = (menu_index + 1) % len(menu_items)
                        menu_note = ""

                    elif released14:
                        if menu_items[menu_index] == "< POWROT":    
                            screen = "home"
                            menu_note = ""

                        elif menu_items[menu_index] == "ZAKONCZ SERWIS":
                            screen = "service_exit"

                        elif menu_items[menu_index] == "HARMONOGRAM":
                            if service_mode:
                                menu_note = "Najpierw koniec serwis"
                            else:
                                schedule_entries = load_schedule()
                                schedule_index = 0
                                plan_action_index = 0
                                screen = "schedule_active" if schedule_enabled else "harmonogram"

                        elif menu_items[menu_index] == "URUCHOM MAKRO":
                            script_names = list_scripts()
                            script_index = 0
                            screen = "scripts"
                        else:
                            menu_note = "Jeszcze niedostepne"



                elif screen == "scripts":
                    if not script_names:
                        if released14:
                            screen = "menu"
                            menu_note = ""
                    else:
                        if released15:
                            script_index = (script_index + 1) % len(script_names)

                        elif released14:
                            selected_script = script_names[script_index]
                            screen = "confirm"

                elif screen == "harmonogram":
                    if not schedule_entries:
                        if released14 and released15:
                            screen = "menu"
                            menu_note = ""
                    else:
                        if released15:
                            schedule_index = (schedule_index + 1) % len(schedule_entries)

                        elif released14:
                            if not time_synced:
                                status = "Najpierw SYNC z PC"
                                screen = "home"
                            else:
                                edit_hour, edit_minute, _ = schedule_entries[schedule_index]
                                edit_active = False
                                screen = "edit_hour"

                elif screen == "service_exit":
                    if released15:
                        screen = "menu"
                    elif released14:
                        # Service exit never sets the wake flag.
                        wake_at = None
                        schedule_enabled = False
                        microcontroller.nvm[0] = 0
                        keyboard.release_all()
                        status = "Restart bez wake"
                        screen = "home"
                        update_display()
                        time.sleep(0.2)
                        microcontroller.reset()

                elif screen == "schedule_active":
                    if released15:
                        plan_action_index = (plan_action_index + 1) % len(plan_actions)
                    elif released14:
                        if plan_action_index == 0:
                            schedule_enabled = False
                            active_schedule = None
                            status = "Plan wylaczony"
                            screen = "home"
                        elif plan_action_index == 1:
                            schedule_index = schedule_entries.index(active_schedule)
                            edit_hour, edit_minute, _ = active_schedule
                            edit_active = True
                            screen = "edit_hour"
                        else:
                            screen = "menu"

                elif screen == "edit_hour":
                    if released14:
                        edit_hour = (edit_hour + 1) % 24
                    elif released15:
                        screen = "edit_minute"

                elif screen == "edit_minute":
                    if released14:
                        edit_minute = (edit_minute + 1) % 60
                    elif released15:
                        name = schedule_entries[schedule_index][2]
                        new_entry = (edit_hour, edit_minute, name)
                        try:
                            save_schedule_entry(schedule_index, new_entry)
                            schedule_entries[schedule_index] = new_entry
                            if edit_active:
                                active_schedule = new_entry
                                now = time.localtime()
                                last_schedule_fire = "{}-{:02d}-{:02d} {:02d}:{:02d}".format(
                                    now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)
                                screen = "schedule_active"
                            else:
                                screen = "schedule_wake"
                        except Exception as error:
                            status = "Blad zapisu TXT"
                            screen = "home"
                            print("Blad zapisu TXT:", error)

                elif screen == "schedule_wake":
                    if released14 or released15:
                        pending_wake = released14
                        screen = "schedule_confirm"


                elif screen == "schedule_confirm":
                    if released15:
                        screen = "harmonogram"
                    elif released14:
                        if not time_synced:
                            status = "Najpierw SYNC czasu"
                            screen = "home"
                        else:
                            active_schedule = schedule_entries[schedule_index]

                            try:
                                save_schedule_entry(schedule_index, active_schedule)
                            except Exception as error:
                                print("Blad zapisu TXT:", error)
                                status = "Blad zapisu TXT"
                                screen = "home"

                            schedule_wake = pending_wake
                            schedule_enabled = True
                            wake_at = None
                            hour, minute, name = active_schedule
                            now = time.localtime()
                            last_schedule_fire = "{}-{:02d}-{:02d} {:02d}:{:02d}".format(
                                now.tm_year, now.tm_mon, now.tm_mday,
                                now.tm_hour, now.tm_min)
                            status = "Plan ON {:02d}:{:02d}".format(hour, minute)
                            screen = "home"


                elif screen == "confirm":


                    if released14:
                        status = "Uruchamiam " + selected_script
                        screen = "home"
                        scriptengine.run(
                            "/scripts/" + selected_script + ".txt",
                            HANDLERS,
                            run_show,
                        )

                    elif released15:
                        screen = "scripts"

                elif wake_at is not None and released15:
                    wake_at = None
                    status = "Wake anulowany"

                elif released14:
                    wake_at = time.monotonic() + wake_delay
                    status = "Wake zaplanowany"

            previous14 = pressed14
            previous15 = pressed15
            buttons_changed_at = time.monotonic()
    else:
        buttons_changed_at = time.monotonic()

    if schedule_enabled and time_synced and active_schedule is not None:
        now = time.localtime()
        hour, minute, name = active_schedule
        key = "{}-{:02d}-{:02d} {:02d}:{:02d}".format(
            now.tm_year, now.tm_mon, now.tm_mday, hour, minute)
        if (now.tm_hour == hour and now.tm_min == minute
                and last_schedule_fire != key):
            last_schedule_fire = key
            status = "Harmonogram: " + name
            screen = "home"
            update_display()
            schedule_enabled = False
            active_schedule = None
            wake_at = None
            try:
                if schedule_wake:
                    prepare_schedule_reset(name)
                else:
                    run_scheduled_macro(name)
            except Exception as error:
                status = "Blad harmonogramu"
                print("Blad harmonogramu:", error)

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