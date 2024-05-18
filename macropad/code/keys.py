"""
YOU CAN EDIT THIS FILE!

This is where you tell the macro pad which keys do what.

The macro pad has pages, where each page can have up to 8
buttons (corresponding to the 8 buttons on the macro pad).

These are defined in the "pages" variable at the bottom of
this file. Each page has a name that will be displayed on
the screen, and then a list of buttons.

Each button has a name, which will get displayed on the
screen, and an action which defines what the button does.

So in the example below, "Text Utilities" is the page name,
and "Cut", "Copy" and "Paste" are the button names, and the
things in brackets afterward the page names tell the macro
pad which keyboard keys to send to the computer when the key
is pressed.

>   pages = (
>       (
>           "Text Utilities", (
>               ("Cut", (Keycode.CONTROL, Keycode.X)),
>               ("Copy", (Keycode.CONTROL, Keycode.C)),
>               ("Paste", (Keycode.CONTROL, Keycode.V)),
>           )
>       ),
>   )

The first button defined in the list will be the top left key,
and they'll progress in this order:

1  2  3  4
5  6  7  8

So in the above example, button 1 is Cut, button 2 is Copy and
button 3 is Paste.

_____________________________________________________________
|               !!    IMPORTANT:    !!                      |
|                                                           |
| When making changes, you'll need to be really careful of  |
| using the right number of brackets and commas, otherwise  |
| the program won't know what is a button or a page.        |
|                                                           |
| You'll also need to be really careful of capital letters. |
|___________________________________________________________|


Each key can do one of 5 different things.

1. Single Key
=============

It can act as a single key, for example:

>   ("Shoot", Keycode.ENTER),

This will create a key called "Shoot" that acts exactly like
the Enter key on a keyboard. You can hold the button down as
long as you like and the macro pad will only tell the computer
to release the key when you lift off the button.

Take a look at
https://docs.circuitpython.org/projects/hid/en/latest/api.html#adafruit-hid-keycode-keycode
for the complete list of keys available to you.

2. Several Keys
===============

A key on the macro pad can act as several keyboard keys at
once. For example:

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
a new line (i.e. press enter).

It's really important that the text you want to send is
surrounded by quote marks (i.e. "). Look up "Python strings"
if you want more information.

Note: This assumes your machine is setup with a normal Windows
keyboard. If you're using something else you might get
funny behaviour.

4. Sequence of keys
=================

This one's a bit more compliated to set up, but also more
powerful! It can run a series instructions, so it can send
a series of button presses or text messages sequentially.

For example, towards the top of the code, you might have this:

>   def launch_command_line(keys, text):
>       keys.send(Keycode.WINDOWS, keycode.R)
>       time.sleep(0.1)
>       text.write("cmd")
>       keys.send(Keycode.ENTER)

This creates something called a function. You can call the
function whatever you like, so on the first line, you can
replace "launch_command_line" with something that describes
your macro. But make sure the "def" and the contents of the
brackets stay the same.

All the following lines MUST start with exactly 4 spaces.
This is called indentation.

The indented lines specify a set of instructions to the
macro pad. In the above example, it presses and releases
the WINDOWS and R keys, waits for 0.1 seconds, types
"cmd", and then presses ENTER.

To assign that function to a key, You'd put this:

>   ("cmd", launch_command_line),

in the pages section.

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
   specify fewer, the remaining keys will default to doing
   nothing.

"""

#################################################################
# Don't change these 5 lines! They set everything up for you
#################################################################
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control_code import ConsumerControlCode
import time
if __name__ == "__main__":
    import code


#################################################################
# The lines below allow you to change the function of the push
# button in the rotary encoder. Uncomment (delete the # in front
# of) the one you want to happen.
#################################################################

#rotary_press_function = ConsumerControlCode.MUTE
#rotary_press_function = ConsumerControlCode.PLAY_PAUSE


#################################################################
# Put your custom functions here (see option 4 above for details)
#################################################################

def launch_command_line(keys, text):
    """
    Example function that will launch the command line on Windows machines
    """
    keys.send(Keycode.WINDOWS, Keycode.R)
    time.sleep(0.1)
    text.write("cmd")
    keys.send(Keycode.ENTER)


#################################################################
# This section defines what all they keys do.
# Remember capital letters are important!
#################################################################

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