import storage
import board
import digitalio

# Button 2 held during reset/USB connection enables Windows write access.
_mode_button = digitalio.DigitalInOut(board.GP15)
_mode_button.switch_to_input(pull=digitalio.Pull.UP)
_usb_edit_mode = not _mode_button.value
_mode_button.deinit()
storage.remount("/", readonly=_usb_edit_mode)

import usb_cdc
import usb_hid

# Konsola Thonny oraz osobny kanal danych.
usb_cdc.enable(console=True, data=True)

# Raport: przyciski (1 bajt), X (2 bajty), Y (2 bajty).
# X i Y sa absolutne, w zakresie 0..32767.
ABS_MOUSE_DESCRIPTOR = bytes((
    0x05, 0x01,        # Usage Page: Generic Desktop
    0x09, 0x02,        # Usage: Mouse
    0xA1, 0x01,        # Collection: Application
    0x85, 0x07,        # Report ID: 7

    0x09, 0x01,        # Usage: Pointer
    0xA1, 0x00,        # Collection: Physical

    0x05, 0x09,        # Usage Page: Button
    0x19, 0x01,        # Usage Minimum: Button 1
    0x29, 0x03,        # Usage Maximum: Button 3
    0x15, 0x00,        # Logical Minimum: 0
    0x25, 0x01,        # Logical Maximum: 1
    0x75, 0x01,        # Report Size: 1 bit
    0x95, 0x03,        # Report Count: 3
    0x81, 0x02,        # Input: Data, Variable, Absolute

    0x75, 0x05,        # Padding: 5 bits
    0x95, 0x01,
    0x81, 0x03,        # Input: Constant

    0x05, 0x01,        # Usage Page: Generic Desktop
    0x09, 0x30,        # Usage: X
    0x09, 0x31,        # Usage: Y
    0x15, 0x00,        # Logical Minimum: 0
    0x26, 0xFF, 0x7F,  # Logical Maximum: 32767
    0x75, 0x10,        # Report Size: 16 bits
    0x95, 0x02,        # Report Count: 2
    0x81, 0x02,        # Input: Data, Variable, Absolute

    0xC0,              # End Physical Collection
    0xC0,              # End Application Collection
))

absolute_mouse = usb_hid.Device(
    report_descriptor=ABS_MOUSE_DESCRIPTOR,
    usage_page=0x01,
    usage=0x02,
    report_ids=(7,),
    in_report_lengths=(5,),
    out_report_lengths=(0,),
)

usb_hid.enable((
    usb_hid.Device.KEYBOARD,
    absolute_mouse,
))