#!/usr/bin/python3

import time

from pewinput import *


# create devices
keyboard = Device([KEY_LEFTSHIFT, KEY_SPACE, KEY_H, KEY_E, KEY_L, KEY_O, KEY_W, KEY_R, KEY_D, KEY_1, KEY_COMMA])
mouse = Mouse()

# type "Hello, World!"
keyboard.click_combination([KEY_LEFTSHIFT, KEY_H])
for key in [KEY_E, KEY_L, KEY_L, KEY_O, KEY_COMMA, KEY_SPACE]:
    keyboard.click(key)

keyboard.click_combination([KEY_LEFTSHIFT, KEY_W])
for key in [KEY_O, KEY_R, KEY_L, KEY_D]:
    # alternatively you can simulate a key press yourself
    keyboard.press(key, flush=False)
    keyboard.release(key, flush=False)
    keyboard.flush()

keyboard.click_combination([KEY_LEFTSHIFT, KEY_1])  # !


# move mouse to the bottom right
for i in range(20):
    mouse.move_relative(5, 5)
    time.sleep(0.02)

# move wheel
for i in range(20):
    mouse.move_wheel(1)
    time.sleep(0.02)

print()

# Optional, but recommended
keyboard.destroy()
mouse.destroy()
