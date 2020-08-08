# pewinput

A python library to emulate input devices such as keyboard, mouse or joystick via the uinput linux kernel module.

GitHub: https://github.com/ssmid/pewinput

## Example

``` Python3
from pewinput import *

keyboard = Device([KEY_T, KEY_E, KEY_S])
for key in [KEY_T, KEY_E, KEY_S, KEY_T]:
    keyboard.click(key)
```

For more details look into example.py.


## Installation

Hopefully in the future:
`pip install pewinput`

For now:
```
git clone https://github.com/ssmid/pewinput
cd pewinput
python3 setup.py install
```


## Contributing

Contributions welcome! Just open up an issue or a pull request.
