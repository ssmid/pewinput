# pewinput

A python library to emulate input devices such as keyboard, mouse or joystick via the uinput linux kernel module.

Motivation was the malfunction of mouse input in python-uinput with newer kernel versions.

GitHub: https://github.com/ssmid/pewinput

## Example

``` Python3
from pewinput import *

keyboard = Device([KEY_H, KEY_E, KEY_L, KEY_O])
for key in [KEY_H, KEY_E, KEY_L, KEY_L, KEY_O]:
    keyboard.click(key)
```
`hello`

For more details look into example.py.


## Installation

`pip install git+https://github.com/ssmid/pewinput`

If that does not work for some reason:
```
git clone https://github.com/ssmid/pewinput
cd pewinput
python3 setup.py install
```


## Contributing

Contributions welcome! Just open up an issue or a pull request.
