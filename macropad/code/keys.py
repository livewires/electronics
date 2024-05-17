'''
YOU CAN EDIT THIS FILE!

This is where you tell the macro pad which buttons do what.

The macro pad has pages, where each page can have up to 8 buttons
(corresponding to the 8 buttons on the macro pad).

These are defined in the "pages" variable below. Each page has
a name that will be displayed on the screen, and then a list
of buttons. Each button has a name and an action. So in the
example below, "Text Utilities" is the page name, and "Cut",
"Copy" and "Paste" are the button names.

>   pages = (
>       (
>           "Text Utilities", (
>               ("Cut", (Keycode.CONTROL, Keycode.X)),
>               ("Copy", (Keycode.CONTROL, Keycode.C)),
>               ("Paste", (Keycode.CONTROL, Keycode.V)),
>           )
>       ),
>   )

You'll need to be really careful of using the right number of
brackets and commas, otherwise the program won't know what is
a button or a page.

The first button defined in the list will be the top left key,
and they'll progress in this order:

1  2  3  4
5  6  7  8

Each key can do one of 5 different things.

1. Single Key
=============

It can act as a single key, for example:

>   ("Shoot", Keycode.ENTER),

This will create a key called "Shoot" that acts exactly like
the Enter key on a keyboard. You can hold the button down and
get repeated presses, and when you release the button on the
macropad, it'll stop pressing the Enter key.

Take a look at
https://docs.circuitpython.org/projects/hid/en/latest/api.html#adafruit-hid-keycode-keycode
for the complete list of keys. 

2. Several Keys
===============

It can act as several keys at once. For example:

> ("Undo", (Keycode.CONTROL, Keycode.Z)),

Note that the list of keys are additionally surrounded by
brackets. That's really important.

This uses the same key codes as "1. Single Key", but will
press both those keys and won't release them until you stop
pressing the button

3. Type some text
=================

It can type a load of text for you. For example:

>   ("Sign", "\n\nThanks,\nJoel"),

When pressed, this will type those characters. The \n means
a new line (i.e. press enter)

This assumes your machine is setup with a normal windows
keyboard. If you're using something else you might get
funny behaviour.

4. Sequence of keys
=================

This one's a bit more compliated to set up, but also more
powerful! It can run a function with a series of the three
previous options, so it can send a series of button presses
sequentially. For example:

>   def launch_command_line(kbd, layout):
>       kbd.send(Keycode.WINDOWS, keycode.R)
>       time.sleep(0.1)
>       layout.write("cmd")
>       kbd.send(Keycode.ENTER)

This will create the function to run. It takes two arguments,
the kbd argument used for individual key presses, and the
layout argument used for sending text.

The function then presses and releases the WINDOWS and R keys,
waits for 0.1 seconds, types "cmd", and then presses ENTER.

To assign that function to a key, You'd put this:

>   ("cmd", launch_command_line),

in the page.

5. Do nothing
=============

Sometimes it's helpful to have a key do nothing when pressed.
That would look like this:

>   ("", None),

You can still give it a name if you want.


Limitations
===========

There are some limitations:

 * Key names can only be up to 5 characters in length
 
 * You can have up to 16 pages (beyond 4 pages the LEDs on
   the board will switch into binary mode)
   
 * You can only have up to 8 buttons per page. If you
   specify fewer, the keys will default to doing nothing.
   

'''

# Don't change these lines!
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control_code import ConsumerControlCode
import time

"""
This allows you to change the function of the push button in the
rotary encoder. Uncomment (delete the # in front of) the one you
want to happen.
"""
#rotary_press_function = ConsumerControlCode.MUTE
#rotary_press_function = ConsumerControlCode.PLAY_PAUSE


def launch_command_line(kbd, layout):
    """
    Example function that will launch the command line on Windows machines
    """
    kbd.send(Keycode.WINDOWS, keycode.R)
    time.sleep(0.1)
    layout.write("cmd")
    kbd.send(Keycode.ENTER)
    

pages = (
    (
        "Text Utilities", (
            ("S All", (Keycode.CONTROL, Keycode.A)),
            ("SelLn", (Keycode.HOME, Keycode.SHIFT, Keycode.END)),
            ("cmd", launch_command_line),
            ("Sign", "\n\nThanks,\nJoel"),
            ("Undo", (Keycode.CONTROL, Keycode.Z)),
            ("Cut", (Keycode.CONTROL, Keycode.X)),
            ("Copy", (Keycode.CONTROL, Keycode.C)),
            ("Paste", (Keycode.CONTROL, Keycode.V)),
        )
    ),
    (
        "Gaming", (
            ("Shoot", Keycode.ENTER),
            ("  ^", Keycode.W),
            ("Jump", Keycode.SPACE),
            ("Chng", Keycode.I),
            ("  <", Keycode.A),
            ("  v", Keycode.S),
            ("  >", Keycode.D),
            ("Rload", Keycode.R),
        ),
    ),
    (
        "Function Keys", (
            ("F13", Keycode.F13),
            ("F14", Keycode.F14),
            ("F15", Keycode.F15),
            ("F16", Keycode.F16),
            ("F17", Keycode.F17),
            ("F18", Keycode.F18),
            ("F19", Keycode.F19),
            ("F20", Keycode.F20),
        ),
    ),
    
)