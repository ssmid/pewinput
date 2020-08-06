
from os.path import dirname, join
from ctypes import *

from typing import List, Optional


pew = cdll.LoadLibrary(join(dirname(__file__), 'libpewinput.so'))


class Event:
    """
    An event like a key or mouse button that can be send by a device.
    It DOES NOT provide a corresponding value like up/down or coordinates.
    """

    def __init__(self, event_type: int, code: int):
        self.type = event_type
        self.code = code

    def __repr__(self):
        return f'Event<type: {self.type}, code: {self.code}>'


class Key(Event):
    """
    A key event that can be send by a device. Not really more special than Event.
    """

    def __init__(self, code: int):
        super(Key, self).__init__(EV_KEY, code)

    def __repr__(self):
        return f'Key<type: {self.type}, code: {self.code}>'


class _UInput:
    """
    An interface to the pewinput c library.
    """

    @staticmethod
    def create_device(name: str, events: List[Event]) -> int:
        fd = pew.open_uinput()
        try:
            for event in events:
                if pew.enable_event(fd, event.type, event.code):
                    raise RuntimeError()
            if pew.create_device(fd, name):
                raise RuntimeError()
        except RuntimeError:
            pew.close_uinput(fd)
            raise RuntimeError(f'Could not create device {name}. Are you root?')
        return fd

    @staticmethod
    def send_event(fd: int, event: Event, value: int):
        pew.send_event(fd, event.type, event.code, value)

    @staticmethod
    def flush(fd: int):
        pew.flush(fd)

    @staticmethod
    def destroy_device(fd: int):
        if pew.destroy_device(fd):
            raise RuntimeError(f'Error on destroying device on {fd}')
        pew.close_uinput(fd)


class Device:
    """
    A virtual input device like a keyboard, mouse or controller, depending of the
    registered events.
    DO NOT try to create "super devices" that combine multiple use cases. Things
    like registering relative and absolute axis on one device will likely fail.
    """

    count = 0

    def __init__(self, event_list: List[Event], name: Optional[str] = None):
        self.name = (name or 'pewinput-virtual-dev') + f'{Device.count}'
        self.fd = _UInput.create_device(self.name, event_list)
        Device.count += 1

    def send_event(self, event: Event, value: int, flush: bool = True):
        _UInput.send_event(self.fd, event, value)
        if flush:
            self.flush()

    def press(self, key: Key, flush: bool = True):
        self.send_event(key, 1, flush)

    def release(self, key: Key, flush: bool = True):
        self.send_event(key, 0, flush)

    def click(self, key: Key, flush: bool = True):
        self.send_event(key, 1, False)
        self.send_event(key, 0, flush)

    def click_combination(self, keys: List[Key]):
        for key in keys:
            self.press(key, False)
        self.flush()
        for key in keys:
            self.release(key, False)
        self.flush()

    def flush(self):
        """
        Actually make send events being processed. Already called by other
        functions by default.
        """
        _UInput.flush(self.fd)

    def destroy(self):
        if self.fd == -1:
            return
        try:
            _UInput.destroy_device(self.fd)
        except RuntimeError:
            raise RuntimeError(f'Could not destroy device: {self}')
        self.fd = -1

    def __del__(self):
        self.destroy()


class Mouse(Device):
    """
    A virtual input device with three buttons and x, y and wheel axis.
    """

    def __init__(self, name: str = None):
        if not name:
            name = 'pewinput-virtual-mouse'
        super(Mouse, self).__init__([BTN_LEFT, BTN_MIDDLE, BTN_RIGHT,
                                     REL_X, REL_Y, REL_WHEEL, REL_HWHEEL], name)

    def move_relative(self, x: int, y: int, flush: bool = True):
        self.send_event(REL_X, x, False)
        self.send_event(REL_Y, y, flush)

    def move_wheel(self, value, flush: bool = True):
        self.send_event(REL_WHEEL, value, flush)

    def move_hwheel(self, value, flush: bool = True):
        self.send_event(REL_HWHEEL, value, flush)


INPUT_PROP_POINTER = 0x00
INPUT_PROP_DIRECT = 0x01
INPUT_PROP_BUTTONPAD = 0x02
INPUT_PROP_SEMI_MT = 0x03
INPUT_PROP_TOPBUTTONPAD = 0x04
INPUT_PROP_POINTING_STICK = 0x05
INPUT_PROP_ACCELEROMETER = 0x06

INPUT_PROP_MAX = 0x1f
INPUT_PROP_CNT = (INPUT_PROP_MAX + 1)


# Event types

EV_SYN = 0x00
EV_KEY = 0x01
EV_REL = 0x02
EV_ABS = 0x03
EV_MSC = 0x04
EV_SW = 0x05
EV_LED = 0x11
EV_SND = 0x12
EV_REP = 0x14
EV_FF = 0x15
EV_PWR = 0x16
EV_FF_STATUS = 0x17
EV_MAX = 0x1f
EV_CNT = (EV_MAX+1)


# Synchronization

SYN_REPORT = Event(EV_SYN, 0)
SYN_CONFIG = Event(EV_SYN, 1)
SYN_MT_REPORT = Event(EV_SYN, 2)
SYN_DROPPED = Event(EV_SYN, 3)
SYN_MAX = Event(EV_SYN, 0xf)
SYN_CNT = Event(EV_SYN, (SYN_MAX.code+1))


# Keys

KEY_RESERVED = Key(0)
KEY_ESC = Key(1)
KEY_1 = Key(2)
KEY_2 = Key(3)
KEY_3 = Key(4)
KEY_4 = Key(5)
KEY_5 = Key(6)
KEY_6 = Key(7)
KEY_7 = Key(8)
KEY_8 = Key(9)
KEY_9 = Key(10)
KEY_0 = Key(11)
KEY_MINUS = Key(12)
KEY_EQUAL = Key(13)
KEY_BACKSPACE = Key(14)
KEY_TAB = Key(15)
KEY_Q = Key(16)
KEY_W = Key(17)
KEY_E = Key(18)
KEY_R = Key(19)
KEY_T = Key(20)
KEY_Y = Key(21)
KEY_U = Key(22)
KEY_I = Key(23)
KEY_O = Key(24)
KEY_P = Key(25)
KEY_LEFTBRACE = Key(26)
KEY_RIGHTBRACE = Key(27)
KEY_ENTER = Key(28)
KEY_LEFTCTRL = Key(29)
KEY_A = Key(30)
KEY_S = Key(31)
KEY_D = Key(32)
KEY_F = Key(33)
KEY_G = Key(34)
KEY_H = Key(35)
KEY_J = Key(36)
KEY_K = Key(37)
KEY_L = Key(38)
KEY_SEMICOLON = Key(39)
KEY_APOSTROPHE = Key(40)
KEY_GRAVE = Key(41)
KEY_LEFTSHIFT = Key(42)
KEY_BACKSLASH = Key(43)
KEY_Z = Key(44)
KEY_X = Key(45)
KEY_C = Key(46)
KEY_V = Key(47)
KEY_B = Key(48)
KEY_N = Key(49)
KEY_M = Key(50)
KEY_COMMA = Key(51)
KEY_DOT = Key(52)
KEY_SLASH = Key(53)
KEY_RIGHTSHIFT = Key(54)
KEY_KPASTERISK = Key(55)
KEY_LEFTALT = Key(56)
KEY_SPACE = Key(57)
KEY_CAPSLOCK = Key(58)
KEY_F1 = Key(59)
KEY_F2 = Key(60)
KEY_F3 = Key(61)
KEY_F4 = Key(62)
KEY_F5 = Key(63)
KEY_F6 = Key(64)
KEY_F7 = Key(65)
KEY_F8 = Key(66)
KEY_F9 = Key(67)
KEY_F10 = Key(68)
KEY_NUMLOCK = Key(69)
KEY_SCROLLLOCK = Key(70)
KEY_KP7 = Key(71)
KEY_KP8 = Key(72)
KEY_KP9 = Key(73)
KEY_KPMINUS = Key(74)
KEY_KP4 = Key(75)
KEY_KP5 = Key(76)
KEY_KP6 = Key(77)
KEY_KPPLUS = Key(78)
KEY_KP1 = Key(79)
KEY_KP2 = Key(80)
KEY_KP3 = Key(81)
KEY_KP0 = Key(82)
KEY_KPDOT = Key(83)

KEY_ZENKAKUHANKAKU = Key(85)
KEY_102ND = Key(86)
KEY_F11 = Key(87)
KEY_F12 = Key(88)
KEY_RO = Key(89)
KEY_KATAKANA = Key(90)
KEY_HIRAGANA = Key(91)
KEY_HENKAN = Key(92)
KEY_KATAKANAHIRAGANA = Key(93)
KEY_MUHENKAN = Key(94)
KEY_KPJPCOMMA = Key(95)
KEY_KPENTER = Key(96)
KEY_RIGHTCTRL = Key(97)
KEY_KPSLASH = Key(98)
KEY_SYSRQ = Key(99)
KEY_RIGHTALT = Key(100)
KEY_LINEFEED = Key(101)
KEY_HOME = Key(102)
KEY_UP = Key(103)
KEY_PAGEUP = Key(104)
KEY_LEFT = Key(105)
KEY_RIGHT = Key(106)
KEY_END = Key(107)
KEY_DOWN = Key(108)
KEY_PAGEDOWN = Key(109)
KEY_INSERT = Key(110)
KEY_DELETE = Key(111)
KEY_MACRO = Key(112)
KEY_MUTE = Key(113)
KEY_VOLUMEDOWN = Key(114)
KEY_VOLUMEUP = Key(115)
KEY_POWER = Key(116)
KEY_KPEQUAL = Key(117)
KEY_KPPLUSMINUS = Key(118)
KEY_PAUSE = Key(119)
KEY_SCALE = Key(120)

KEY_KPCOMMA = Key(121)
KEY_HANGEUL = Key(122)
KEY_HANGUEL = Key(KEY_HANGEUL.code)
KEY_HANJA = Key(123)
KEY_YEN = Key(124)
KEY_LEFTMETA = Key(125)
KEY_RIGHTMETA = Key(126)
KEY_COMPOSE = Key(127)

KEY_STOP = Key(128)
KEY_AGAIN = Key(129)
KEY_PROPS = Key(130)
KEY_UNDO = Key(131)
KEY_FRONT = Key(132)
KEY_COPY = Key(133)
KEY_OPEN = Key(134)
KEY_PASTE = Key(135)
KEY_FIND = Key(136)
KEY_CUT = Key(137)
KEY_HELP = Key(138)
KEY_MENU = Key(139)
KEY_CALC = Key(140)
KEY_SETUP = Key(141)
KEY_SLEEP = Key(142)
KEY_WAKEUP = Key(143)
KEY_FILE = Key(144)
KEY_SENDFILE = Key(145)
KEY_DELETEFILE = Key(146)
KEY_XFER = Key(147)
KEY_PROG1 = Key(148)
KEY_PROG2 = Key(149)
KEY_WWW = Key(150)
KEY_MSDOS = Key(151)
KEY_COFFEE = Key(152)
KEY_SCREENLOCK = Key(KEY_COFFEE.code)
KEY_ROTATE_DISPLAY = Key(153)
KEY_DIRECTION = Key(KEY_ROTATE_DISPLAY.code)
KEY_CYCLEWINDOWS = Key(154)
KEY_MAIL = Key(155)
KEY_BOOKMARKS = Key(156)
KEY_COMPUTER = Key(157)
KEY_BACK = Key(158)
KEY_FORWARD = Key(159)
KEY_CLOSECD = Key(160)
KEY_EJECTCD = Key(161)
KEY_EJECTCLOSECD = Key(162)
KEY_NEXTSONG = Key(163)
KEY_PLAYPAUSE = Key(164)
KEY_PREVIOUSSONG = Key(165)
KEY_STOPCD = Key(166)
KEY_RECORD = Key(167)
KEY_REWIND = Key(168)
KEY_PHONE = Key(169)
KEY_ISO = Key(170)
KEY_CONFIG = Key(171)
KEY_HOMEPAGE = Key(172)
KEY_REFRESH = Key(173)
KEY_EXIT = Key(174)
KEY_MOVE = Key(175)
KEY_EDIT = Key(176)
KEY_SCROLLUP = Key(177)
KEY_SCROLLDOWN = Key(178)
KEY_KPLEFTPAREN = Key(179)
KEY_KPRIGHTPAREN = Key(180)
KEY_NEW = Key(181)
KEY_REDO = Key(182)

KEY_F13 = Key(183)
KEY_F14 = Key(184)
KEY_F15 = Key(185)
KEY_F16 = Key(186)
KEY_F17 = Key(187)
KEY_F18 = Key(188)
KEY_F19 = Key(189)
KEY_F20 = Key(190)
KEY_F21 = Key(191)
KEY_F22 = Key(192)
KEY_F23 = Key(193)
KEY_F24 = Key(194)

KEY_PLAYCD = Key(200)
KEY_PAUSECD = Key(201)
KEY_PROG3 = Key(202)
KEY_PROG4 = Key(203)
KEY_DASHBOARD = Key(204)
KEY_SUSPEND = Key(205)
KEY_CLOSE = Key(206)
KEY_PLAY = Key(207)
KEY_FASTFORWARD = Key(208)
KEY_BASSBOOST = Key(209)
KEY_PRINT = Key(210)
KEY_HP = Key(211)
KEY_CAMERA = Key(212)
KEY_SOUND = Key(213)
KEY_QUESTION = Key(214)
KEY_EMAIL = Key(215)
KEY_CHAT = Key(216)
KEY_SEARCH = Key(217)
KEY_CONNECT = Key(218)
KEY_FINANCE = Key(219)
KEY_SPORT = Key(220)
KEY_SHOP = Key(221)
KEY_ALTERASE = Key(222)
KEY_CANCEL = Key(223)
KEY_BRIGHTNESSDOWN = Key(224)
KEY_BRIGHTNESSUP = Key(225)
KEY_MEDIA = Key(226)

KEY_SWITCHVIDEOMODE = Key(227)
KEY_KBDILLUMTOGGLE = Key(228)
KEY_KBDILLUMDOWN = Key(229)
KEY_KBDILLUMUP = Key(230)

KEY_SEND = Key(231)
KEY_REPLY = Key(232)
KEY_FORWARDMAIL = Key(233)
KEY_SAVE = Key(234)
KEY_DOCUMENTS = Key(235)

KEY_BATTERY = Key(236)

KEY_BLUETOOTH = Key(237)
KEY_WLAN = Key(238)
KEY_UWB = Key(239)

KEY_UNKNOWN = Key(240)

KEY_VIDEO_NEXT = Key(241)
KEY_VIDEO_PREV = Key(242)
KEY_BRIGHTNESS_CYCLE = Key(243)
KEY_BRIGHTNESS_AUTO = Key(244)
KEY_BRIGHTNESS_ZERO = Key(KEY_BRIGHTNESS_AUTO.code)
KEY_DISPLAY_OFF = Key(245)

KEY_WWAN = Key(246)
KEY_WIMAX = Key(KEY_WWAN.code)
KEY_RFKILL = Key(247)

KEY_MICMUTE = Key(248)

# Code 255 is reserved for special needs of AT keyboard driver

BTN_MISC = Key(0x100)
BTN_0 = Key(0x100)
BTN_1 = Key(0x101)
BTN_2 = Key(0x102)
BTN_3 = Key(0x103)
BTN_4 = Key(0x104)
BTN_5 = Key(0x105)
BTN_6 = Key(0x106)
BTN_7 = Key(0x107)
BTN_8 = Key(0x108)
BTN_9 = Key(0x109)

BTN_MOUSE = Key(0x110)
BTN_LEFT = Key(0x110)
BTN_RIGHT = Key(0x111)
BTN_MIDDLE = Key(0x112)
BTN_SIDE = Key(0x113)
BTN_EXTRA = Key(0x114)
BTN_FORWARD = Key(0x115)
BTN_BACK = Key(0x116)
BTN_TASK = Key(0x117)

BTN_JOYSTICK = Key(0x120)
BTN_TRIGGER = Key(0x120)
BTN_THUMB = Key(0x121)
BTN_THUMB2 = Key(0x122)
BTN_TOP = Key(0x123)
BTN_TOP2 = Key(0x124)
BTN_PINKIE = Key(0x125)
BTN_BASE = Key(0x126)
BTN_BASE2 = Key(0x127)
BTN_BASE3 = Key(0x128)
BTN_BASE4 = Key(0x129)
BTN_BASE5 = Key(0x12a)
BTN_BASE6 = Key(0x12b)
BTN_DEAD = Key(0x12f)

BTN_GAMEPAD = Key(0x130)
BTN_SOUTH = Key(0x130)
BTN_A = Key(BTN_SOUTH.code)
BTN_EAST = Key(0x131)
BTN_B = Key(BTN_EAST.code)
BTN_C = Key(0x132)
BTN_NORTH = Key(0x133)
BTN_X = Key(BTN_NORTH.code)
BTN_WEST = Key(0x134)
BTN_Y = Key(BTN_WEST.code)
BTN_Z = Key(0x135)
BTN_TL = Key(0x136)
BTN_TR = Key(0x137)
BTN_TL2 = Key(0x138)
BTN_TR2 = Key(0x139)
BTN_SELECT = Key(0x13a)
BTN_START = Key(0x13b)
BTN_MODE = Key(0x13c)
BTN_THUMBL = Key(0x13d)
BTN_THUMBR = Key(0x13e)

BTN_DIGI = Key(0x140)
BTN_TOOL_PEN = Key(0x140)
BTN_TOOL_RUBBER = Key(0x141)
BTN_TOOL_BRUSH = Key(0x142)
BTN_TOOL_PENCIL = Key(0x143)
BTN_TOOL_AIRBRUSH = Key(0x144)
BTN_TOOL_FINGER = Key(0x145)
BTN_TOOL_MOUSE = Key(0x146)
BTN_TOOL_LENS = Key(0x147)
BTN_TOOL_QUINTTAP = Key(0x148)
BTN_STYLUS3 = Key(0x149)
BTN_TOUCH = Key(0x14a)
BTN_STYLUS = Key(0x14b)
BTN_STYLUS2 = Key(0x14c)
BTN_TOOL_DOUBLETAP = Key(0x14d)
BTN_TOOL_TRIPLETAP = Key(0x14e)
BTN_TOOL_QUADTAP = Key(0x14f)

BTN_WHEEL = Key(0x150)
BTN_GEAR_DOWN = Key(0x150)
BTN_GEAR_UP = Key(0x151)

KEY_OK = Key(0x160)
KEY_SELECT = Key(0x161)
KEY_GOTO = Key(0x162)
KEY_CLEAR = Key(0x163)
KEY_POWER2 = Key(0x164)
KEY_OPTION = Key(0x165)
KEY_INFO = Key(0x166)
KEY_TIME = Key(0x167)
KEY_VENDOR = Key(0x168)
KEY_ARCHIVE = Key(0x169)
KEY_PROGRAM = Key(0x16a)
KEY_CHANNEL = Key(0x16b)
KEY_FAVORITES = Key(0x16c)
KEY_EPG = Key(0x16d)
KEY_PVR = Key(0x16e)
KEY_MHP = Key(0x16f)
KEY_LANGUAGE = Key(0x170)
KEY_TITLE = Key(0x171)
KEY_SUBTITLE = Key(0x172)
KEY_ANGLE = Key(0x173)
KEY_FULL_SCREEN = Key(0x174)
KEY_ZOOM = Key(KEY_FULL_SCREEN.code)
KEY_MODE = Key(0x175)
KEY_KEYBOARD = Key(0x176)
KEY_ASPECT_RATIO = Key(0x177)
KEY_SCREEN = Key(KEY_ASPECT_RATIO.code)
KEY_PC = Key(0x178)
KEY_TV = Key(0x179)
KEY_TV2 = Key(0x17a)
KEY_VCR = Key(0x17b)
KEY_VCR2 = Key(0x17c)
KEY_SAT = Key(0x17d)
KEY_SAT2 = Key(0x17e)
KEY_CD = Key(0x17f)
KEY_TAPE = Key(0x180)
KEY_RADIO = Key(0x181)
KEY_TUNER = Key(0x182)
KEY_PLAYER = Key(0x183)
KEY_TEXT = Key(0x184)
KEY_DVD = Key(0x185)
KEY_AUX = Key(0x186)
KEY_MP3 = Key(0x187)
KEY_AUDIO = Key(0x188)
KEY_VIDEO = Key(0x189)
KEY_DIRECTORY = Key(0x18a)
KEY_LIST = Key(0x18b)
KEY_MEMO = Key(0x18c)
KEY_CALENDAR = Key(0x18d)
KEY_RED = Key(0x18e)
KEY_GREEN = Key(0x18f)
KEY_YELLOW = Key(0x190)
KEY_BLUE = Key(0x191)
KEY_CHANNELUP = Key(0x192)
KEY_CHANNELDOWN = Key(0x193)
KEY_FIRST = Key(0x194)
KEY_LAST = Key(0x195)
KEY_AB = Key(0x196)
KEY_NEXT = Key(0x197)
KEY_RESTART = Key(0x198)
KEY_SLOW = Key(0x199)
KEY_SHUFFLE = Key(0x19a)
KEY_BREAK = Key(0x19b)
KEY_PREVIOUS = Key(0x19c)
KEY_DIGITS = Key(0x19d)
KEY_TEEN = Key(0x19e)
KEY_TWEN = Key(0x19f)
KEY_VIDEOPHONE = Key(0x1a0)
KEY_GAMES = Key(0x1a1)
KEY_ZOOMIN = Key(0x1a2)
KEY_ZOOMOUT = Key(0x1a3)
KEY_ZOOMRESET = Key(0x1a4)
KEY_WORDPROCESSOR = Key(0x1a5)
KEY_EDITOR = Key(0x1a6)
KEY_SPREADSHEET = Key(0x1a7)
KEY_GRAPHICSEDITOR = Key(0x1a8)
KEY_PRESENTATION = Key(0x1a9)
KEY_DATABASE = Key(0x1aa)
KEY_NEWS = Key(0x1ab)
KEY_VOICEMAIL = Key(0x1ac)
KEY_ADDRESSBOOK = Key(0x1ad)
KEY_MESSENGER = Key(0x1ae)
KEY_DISPLAYTOGGLE = Key(0x1af)
KEY_BRIGHTNESS_TOGGLE = Key(KEY_DISPLAYTOGGLE.code)
KEY_SPELLCHECK = Key(0x1b0)
KEY_LOGOFF = Key(0x1b1)

KEY_DOLLAR = Key(0x1b2)
KEY_EURO = Key(0x1b3)

KEY_FRAMEBACK = Key(0x1b4)
KEY_FRAMEFORWARD = Key(0x1b5)
KEY_CONTEXT_MENU = Key(0x1b6)
KEY_MEDIA_REPEAT = Key(0x1b7)
KEY_10CHANNELSUP = Key(0x1b8)
KEY_10CHANNELSDOWN = Key(0x1b9)
KEY_IMAGES = Key(0x1ba)

KEY_DEL_EOL = Key(0x1c0)
KEY_DEL_EOS = Key(0x1c1)
KEY_INS_LINE = Key(0x1c2)
KEY_DEL_LINE = Key(0x1c3)

KEY_FN = Key(0x1d0)
KEY_FN_ESC = Key(0x1d1)
KEY_FN_F1 = Key(0x1d2)
KEY_FN_F2 = Key(0x1d3)
KEY_FN_F3 = Key(0x1d4)
KEY_FN_F4 = Key(0x1d5)
KEY_FN_F5 = Key(0x1d6)
KEY_FN_F6 = Key(0x1d7)
KEY_FN_F7 = Key(0x1d8)
KEY_FN_F8 = Key(0x1d9)
KEY_FN_F9 = Key(0x1da)
KEY_FN_F10 = Key(0x1db)
KEY_FN_F11 = Key(0x1dc)
KEY_FN_F12 = Key(0x1dd)
KEY_FN_1 = Key(0x1de)
KEY_FN_2 = Key(0x1df)
KEY_FN_D = Key(0x1e0)
KEY_FN_E = Key(0x1e1)
KEY_FN_F = Key(0x1e2)
KEY_FN_S = Key(0x1e3)
KEY_FN_B = Key(0x1e4)

KEY_BRL_DOT1 = Key(0x1f1)
KEY_BRL_DOT2 = Key(0x1f2)
KEY_BRL_DOT3 = Key(0x1f3)
KEY_BRL_DOT4 = Key(0x1f4)
KEY_BRL_DOT5 = Key(0x1f5)
KEY_BRL_DOT6 = Key(0x1f6)
KEY_BRL_DOT7 = Key(0x1f7)
KEY_BRL_DOT8 = Key(0x1f8)
KEY_BRL_DOT9 = Key(0x1f9)
KEY_BRL_DOT10 = Key(0x1fa)

KEY_NUMERIC_0 = Key(0x200)
KEY_NUMERIC_1 = Key(0x201)
KEY_NUMERIC_2 = Key(0x202)
KEY_NUMERIC_3 = Key(0x203)
KEY_NUMERIC_4 = Key(0x204)
KEY_NUMERIC_5 = Key(0x205)
KEY_NUMERIC_6 = Key(0x206)
KEY_NUMERIC_7 = Key(0x207)
KEY_NUMERIC_8 = Key(0x208)
KEY_NUMERIC_9 = Key(0x209)
KEY_NUMERIC_STAR = Key(0x20a)
KEY_NUMERIC_POUND = Key(0x20b)
KEY_NUMERIC_A = Key(0x20c)
KEY_NUMERIC_B = Key(0x20d)
KEY_NUMERIC_C = Key(0x20e)
KEY_NUMERIC_D = Key(0x20f)

KEY_CAMERA_FOCUS = Key(0x210)
KEY_WPS_BUTTON = Key(0x211)

KEY_TOUCHPAD_TOGGLE = Key(0x212)
KEY_TOUCHPAD_ON = Key(0x213)
KEY_TOUCHPAD_OFF = Key(0x214)

KEY_CAMERA_ZOOMIN = Key(0x215)
KEY_CAMERA_ZOOMOUT = Key(0x216)
KEY_CAMERA_UP = Key(0x217)
KEY_CAMERA_DOWN = Key(0x218)
KEY_CAMERA_LEFT = Key(0x219)
KEY_CAMERA_RIGHT = Key(0x21a)

KEY_ATTENDANT_ON = Key(0x21b)
KEY_ATTENDANT_OFF = Key(0x21c)
KEY_ATTENDANT_TOGGLE = Key(0x21d)
KEY_LIGHTS_TOGGLE = Key(0x21e)

BTN_DPAD_UP = Key(0x220)
BTN_DPAD_DOWN = Key(0x221)
BTN_DPAD_LEFT = Key(0x222)
BTN_DPAD_RIGHT = Key(0x223)

KEY_ALS_TOGGLE = Key(0x230)
KEY_ROTATE_LOCK_TOGGLE = Key(0x231)

KEY_BUTTONCONFIG = Key(0x240)
KEY_TASKMANAGER = Key(0x241)
KEY_JOURNAL = Key(0x242)
KEY_CONTROLPANEL = Key(0x243)
KEY_APPSELECT = Key(0x244)
KEY_SCREENSAVER = Key(0x245)
KEY_VOICECOMMAND = Key(0x246)
KEY_ASSISTANT = Key(0x247)
KEY_KBD_LAYOUT_NEXT = Key(0x248)

KEY_BRIGHTNESS_MIN = Key(0x250)
KEY_BRIGHTNESS_MAX = Key(0x251)

KEY_KBDINPUTASSIST_PREV = Key(0x260)
KEY_KBDINPUTASSIST_NEXT = Key(0x261)
KEY_KBDINPUTASSIST_PREVGROUP = Key(0x262)
KEY_KBDINPUTASSIST_NEXTGROUP = Key(0x263)
KEY_KBDINPUTASSIST_ACCEPT = Key(0x264)
KEY_KBDINPUTASSIST_CANCEL = Key(0x265)

# Diagonal movement keys
KEY_RIGHT_UP = Key(0x266)
KEY_RIGHT_DOWN = Key(0x267)
KEY_LEFT_UP = Key(0x268)
KEY_LEFT_DOWN = Key(0x269)

KEY_ROOT_MENU = Key(0x26a)
KEY_MEDIA_TOP_MENU = Key(0x26b)
KEY_NUMERIC_11 = Key(0x26c)
KEY_NUMERIC_12 = Key(0x26d)

KEY_AUDIO_DESC = Key(0x26e)
KEY_3D_MODE = Key(0x26f)
KEY_NEXT_FAVORITE = Key(0x270)
KEY_STOP_RECORD = Key(0x271)
KEY_PAUSE_RECORD = Key(0x272)
KEY_VOD = Key(0x273)
KEY_UNMUTE = Key(0x274)
KEY_FASTREVERSE = Key(0x275)
KEY_SLOWREVERSE = Key(0x276)

KEY_DATA = Key(0x277)
KEY_ONSCREEN_KEYBOARD = Key(0x278)
# Electronic privacy screen control
KEY_PRIVACY_SCREEN_TOGGLE = Key(0x279)

# Select an area of screen to be copied
KEY_SELECTIVE_SCREENSHOT = Key(0x27a)

KEY_MACRO1 = Key(0x290)
KEY_MACRO2 = Key(0x291)
KEY_MACRO3 = Key(0x292)
KEY_MACRO4 = Key(0x293)
KEY_MACRO5 = Key(0x294)
KEY_MACRO6 = Key(0x295)
KEY_MACRO7 = Key(0x296)
KEY_MACRO8 = Key(0x297)
KEY_MACRO9 = Key(0x298)
KEY_MACRO10 = Key(0x299)
KEY_MACRO11 = Key(0x29a)
KEY_MACRO12 = Key(0x29b)
KEY_MACRO13 = Key(0x29c)
KEY_MACRO14 = Key(0x29d)
KEY_MACRO15 = Key(0x29e)
KEY_MACRO16 = Key(0x29f)
KEY_MACRO17 = Key(0x2a0)
KEY_MACRO18 = Key(0x2a1)
KEY_MACRO19 = Key(0x2a2)
KEY_MACRO20 = Key(0x2a3)
KEY_MACRO21 = Key(0x2a4)
KEY_MACRO22 = Key(0x2a5)
KEY_MACRO23 = Key(0x2a6)
KEY_MACRO24 = Key(0x2a7)
KEY_MACRO25 = Key(0x2a8)
KEY_MACRO26 = Key(0x2a9)
KEY_MACRO27 = Key(0x2aa)
KEY_MACRO28 = Key(0x2ab)
KEY_MACRO29 = Key(0x2ac)
KEY_MACRO30 = Key(0x2ad)

KEY_MACRO_RECORD_START = Key(0x2b0)
KEY_MACRO_RECORD_STOP = Key(0x2b1)
KEY_MACRO_PRESET_CYCLE = Key(0x2b2)
KEY_MACRO_PRESET1 = Key(0x2b3)
KEY_MACRO_PRESET2 = Key(0x2b4)
KEY_MACRO_PRESET3 = Key(0x2b5)

KEY_KBD_LCD_MENU1 = Key(0x2b8)
KEY_KBD_LCD_MENU2 = Key(0x2b9)
KEY_KBD_LCD_MENU3 = Key(0x2ba)
KEY_KBD_LCD_MENU4 = Key(0x2bb)
KEY_KBD_LCD_MENU5 = Key(0x2bc)

BTN_TRIGGER_HAPPY = Key(0x2c0)
BTN_TRIGGER_HAPPY1 = Key(0x2c0)
BTN_TRIGGER_HAPPY2 = Key(0x2c1)
BTN_TRIGGER_HAPPY3 = Key(0x2c2)
BTN_TRIGGER_HAPPY4 = Key(0x2c3)
BTN_TRIGGER_HAPPY5 = Key(0x2c4)
BTN_TRIGGER_HAPPY6 = Key(0x2c5)
BTN_TRIGGER_HAPPY7 = Key(0x2c6)
BTN_TRIGGER_HAPPY8 = Key(0x2c7)
BTN_TRIGGER_HAPPY9 = Key(0x2c8)
BTN_TRIGGER_HAPPY10 = Key(0x2c9)
BTN_TRIGGER_HAPPY11 = Key(0x2ca)
BTN_TRIGGER_HAPPY12 = Key(0x2cb)
BTN_TRIGGER_HAPPY13 = Key(0x2cc)
BTN_TRIGGER_HAPPY14 = Key(0x2cd)
BTN_TRIGGER_HAPPY15 = Key(0x2ce)
BTN_TRIGGER_HAPPY16 = Key(0x2cf)
BTN_TRIGGER_HAPPY17 = Key(0x2d0)
BTN_TRIGGER_HAPPY18 = Key(0x2d1)
BTN_TRIGGER_HAPPY19 = Key(0x2d2)
BTN_TRIGGER_HAPPY20 = Key(0x2d3)
BTN_TRIGGER_HAPPY21 = Key(0x2d4)
BTN_TRIGGER_HAPPY22 = Key(0x2d5)
BTN_TRIGGER_HAPPY23 = Key(0x2d6)
BTN_TRIGGER_HAPPY24 = Key(0x2d7)
BTN_TRIGGER_HAPPY25 = Key(0x2d8)
BTN_TRIGGER_HAPPY26 = Key(0x2d9)
BTN_TRIGGER_HAPPY27 = Key(0x2da)
BTN_TRIGGER_HAPPY28 = Key(0x2db)
BTN_TRIGGER_HAPPY29 = Key(0x2dc)
BTN_TRIGGER_HAPPY30 = Key(0x2dd)
BTN_TRIGGER_HAPPY31 = Key(0x2de)
BTN_TRIGGER_HAPPY32 = Key(0x2df)
BTN_TRIGGER_HAPPY33 = Key(0x2e0)
BTN_TRIGGER_HAPPY34 = Key(0x2e1)
BTN_TRIGGER_HAPPY35 = Key(0x2e2)
BTN_TRIGGER_HAPPY36 = Key(0x2e3)
BTN_TRIGGER_HAPPY37 = Key(0x2e4)
BTN_TRIGGER_HAPPY38 = Key(0x2e5)
BTN_TRIGGER_HAPPY39 = Key(0x2e6)
BTN_TRIGGER_HAPPY40 = Key(0x2e7)

KEY_MIN_INTERESTING = Key(KEY_MUTE.code)
KEY_MAX = Key(0x2ff)
KEY_CNT = Key(KEY_MAX.code+1)


# Relative axes

REL_X = Event(EV_REL, 0x00)
REL_Y = Event(EV_REL, 0x01)
REL_Z = Event(EV_REL, 0x02)
REL_RX = Event(EV_REL, 0x03)
REL_RY = Event(EV_REL, 0x04)
REL_RZ = Event(EV_REL, 0x05)
REL_HWHEEL = Event(EV_REL, 0x06)
REL_DIAL = Event(EV_REL, 0x07)
REL_WHEEL = Event(EV_REL, 0x08)
REL_MISC = Event(EV_REL, 0x09)
REL_RESERVED = Event(EV_REL, 0x0a)
REL_WHEEL_HI_RES = Event(EV_REL, 0x0b)
REL_HWHEEL_HI_RES = Event(EV_REL, 0x0c)
REL_MAX = Event(EV_REL, 0x0f)
REL_CNT = Event(EV_REL, (REL_MAX.code+1))


# Absolute axes

ABS_X = Event(EV_ABS, 0x00)
ABS_Y = Event(EV_ABS, 0x01)
ABS_Z = Event(EV_ABS, 0x02)
ABS_RX = Event(EV_ABS, 0x03)
ABS_RY = Event(EV_ABS, 0x04)
ABS_RZ = Event(EV_ABS, 0x05)
ABS_THROTTLE = Event(EV_ABS, 0x06)
ABS_RUDDER = Event(EV_ABS, 0x07)
ABS_WHEEL = Event(EV_ABS, 0x08)
ABS_GAS = Event(EV_ABS, 0x09)
ABS_BRAKE = Event(EV_ABS, 0x0a)
ABS_HAT0X = Event(EV_ABS, 0x10)
ABS_HAT0Y = Event(EV_ABS, 0x11)
ABS_HAT1X = Event(EV_ABS, 0x12)
ABS_HAT1Y = Event(EV_ABS, 0x13)
ABS_HAT2X = Event(EV_ABS, 0x14)
ABS_HAT2Y = Event(EV_ABS, 0x15)
ABS_HAT3X = Event(EV_ABS, 0x16)
ABS_HAT3Y = Event(EV_ABS, 0x17)
ABS_PRESSURE = Event(EV_ABS, 0x18)
ABS_DISTANCE = Event(EV_ABS, 0x19)
ABS_TILT_X = Event(EV_ABS, 0x1a)
ABS_TILT_Y = Event(EV_ABS, 0x1b)
ABS_TOOL_WIDTH = Event(EV_ABS, 0x1c)

ABS_VOLUME = Event(EV_ABS, 0x20)

ABS_MISC = Event(EV_ABS, 0x28)

ABS_RESERVED = Event(EV_ABS, 0x2e)

ABS_MT_SLOT = Event(EV_ABS, 0x2f)
ABS_MT_TOUCH_MAJOR = Event(EV_ABS, 0x30)
ABS_MT_TOUCH_MINOR = Event(EV_ABS, 0x31)
ABS_MT_WIDTH_MAJOR = Event(EV_ABS, 0x32)
ABS_MT_WIDTH_MINOR = Event(EV_ABS, 0x33)
ABS_MT_ORIENTATION = Event(EV_ABS, 0x34)
ABS_MT_POSITION_X = Event(EV_ABS, 0x35)
ABS_MT_POSITION_Y = Event(EV_ABS, 0x36)
ABS_MT_TOOL_TYPE = Event(EV_ABS, 0x37)
ABS_MT_BLOB_ID = Event(EV_ABS, 0x38)
ABS_MT_TRACKING_ID = Event(EV_ABS, 0x39)
ABS_MT_PRESSURE = Event(EV_ABS, 0x3a)
ABS_MT_DISTANCE = Event(EV_ABS, 0x3b)
ABS_MT_TOOL_X = Event(EV_ABS, 0x3c)
ABS_MT_TOOL_Y = Event(EV_ABS, 0x3d)


ABS_MAX = Event(EV_ABS, 0x3f)
ABS_CNT = Event(EV_ABS, (ABS_MAX.code+1))


# Switch events

SW_LID = Event(EV_SW, 0x00)
SW_TABLET_MODE = Event(EV_SW, 0x01)
SW_HEADPHONE_INSERT = Event(EV_SW, 0x02)
SW_RFKILL_ALL = Event(EV_SW, 0x03)
SW_RADIO = Event(EV_SW, SW_RFKILL_ALL.code)
SW_MICROPHONE_INSERT = Event(EV_SW, 0x04)
SW_DOCK = Event(EV_SW, 0x05)
SW_LINEOUT_INSERT = Event(EV_SW, 0x06)
SW_JACK_PHYSICAL_INSERT = Event(EV_SW, 0x07)
SW_VIDEOOUT_INSERT = Event(EV_SW, 0x08)
SW_CAMERA_LENS_COVER = Event(EV_SW, 0x09)
SW_KEYPAD_SLIDE = Event(EV_SW, 0x0a)
SW_FRONT_PROXIMITY = Event(EV_SW, 0x0b)
SW_ROTATE_LOCK = Event(EV_SW, 0x0c)
SW_LINEIN_INSERT = Event(EV_SW, 0x0d)
SW_MUTE_DEVICE = Event(EV_SW, 0x0e)
SW_PEN_INSERTED = Event(EV_SW, 0x0f)
SW_MACHINE_COVER = Event(EV_SW, 0x10)
SW_MAX = Event(EV_SW, 0x10)
SW_CNT = Event(EV_SW, (SW_MAX.code+1))


# Misc

MSC_SERIAL = Event(EV_MSC, 0x00)
MSC_PULSELED = Event(EV_MSC, 0x01)
MSC_GESTURE = Event(EV_MSC, 0x02)
MSC_RAW = Event(EV_MSC, 0x03)
MSC_SCAN = Event(EV_MSC, 0x04)
MSC_TIMESTAMP = Event(EV_MSC, 0x05)
MSC_MAX = Event(EV_MSC, 0x07)
MSC_CNT = Event(EV_MSC, (MSC_MAX.code+1))


# LEDs

LED_NUML = Event(EV_LED, 0x00)
LED_CAPSL = Event(EV_LED, 0x01)
LED_SCROLLL = Event(EV_LED, 0x02)
LED_COMPOSE = Event(EV_LED, 0x03)
LED_KANA = Event(EV_LED, 0x04)
LED_SLEEP = Event(EV_LED, 0x05)
LED_SUSPEND = Event(EV_LED, 0x06)
LED_MUTE = Event(EV_LED, 0x07)
LED_MISC = Event(EV_LED, 0x08)
LED_MAIL = Event(EV_LED, 0x09)
LED_CHARGING = Event(EV_LED, 0x0a)
LED_MAX = Event(EV_LED, 0x0f)
LED_CNT = Event(EV_LED, (LED_MAX.code+1))


# Autorepeat values

REP_DELAY = Event(EV_REP, 0x00)
REP_PERIOD = Event(EV_REP, 0x01)
REP_MAX = Event(EV_REP, 0x01)
REP_CNT = Event(EV_REP, (REP_MAX.code+1))


# Sounds

SND_CLICK = Event(EV_SND, 0x00)
SND_BELL = Event(EV_SND, 0x01)
SND_TONE = Event(EV_SND, 0x02)
SND_MAX = Event(EV_SND, 0x07)
SND_CNT = Event(EV_SND, (SND_MAX.code+1))
