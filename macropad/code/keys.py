from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control_code import ConsumerControlCode

#rotary_press_function = ConsumerControlCode.MUTE
rotary_press_function = ConsumerControlCode.PLAY_PAUSE

pages = (
    (
        "Page 1", (
            ("F13", Keycode.F13),
            ("F14", Keycode.F14),
            ("F15", Keycode.F15),
            ("Hi", "Hello World"),
            ("undo", (Keycode.CONTROL, Keycode.Z)),
            ("cut", (Keycode.CONTROL, Keycode.X)),
            ("copy", (Keycode.CONTROL, Keycode.C)),
            ("paste", (Keycode.CONTROL, Keycode.V)),
        ),
    ),
    (
        "Gaming", (
            ("", None),
            ("W", "W"),
            ("", None),
            ("", None),
            ("A", "A"),
            ("S", Keycode.S),
            ("D", Keycode.D),
        ),
    ),
    
)