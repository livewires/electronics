"""
LiveWires macropad main code.

Author: Joel Fergusson
Date: 2024-05-18

Unless you want to dig into the Python, don't edit this file.

If you want to change what the buttons do, edit keys.py

For more information, see
https://github.com/livewires/electronics
"""


import digitalio as io
import board
import time
import rotaryio
from adafruit_hid.keycode import Keycode

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from lib.keyboard_layout_win_uk import KeyboardLayout
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

from lib.display_manager import DisplayManager

dm = DisplayManager()
dm.show_splash_screen()

try:
    import keys
except TypeError:
    dm.show_err("Can't import pages\nMissing comma?")
    time.sleep(5)
except NameError:
    dm.show_err("Can't import pages\nCheck spelling incl.\ncapital letters")
    time.sleep(5)
except IndentationError:
    dm.show_err("Can't import pages\nSomething wrong with\nindentation.")
    time.sleep(5)
except SyntaxError:
    dm.show_err("Can't import pages\nSyntax error: some \ninvalid Python.")
    time.sleep(5)
except Exception as e:
    dm.show_err("Can't import pages\nUnexpected error:\n{}".format(type(e).__name__))
    time.sleep(5)
    
dm.show_splash_screen()
    
try:
    rotary_press_function = keys.rotary_press_function
except Exception:
    rotary_press_function = ConsumerControlCode.PLAY_PAUSE


class Leds():
    def __init__(self, show_binary=True):
        self.show_binary = show_binary
        pin_nums = [
            board.GP13,
            board.GP12,
            board.GP11,
            board.GP10,
        ]
        self.pins = [io.DigitalInOut(i) for i in pin_nums]
        for p in self.pins:
            p.direction = io.Direction.OUTPUT
            p.drive_mode = io.DriveMode.PUSH_PULL
            p.value = 0
    
    def show(self, value):
        if not self.show_binary:
            value = 1 << value
        value &= 0xF
        for i, p in enumerate(self.pins):
            p.value = bool(value & (1 << i))
            

class Buttons():
    def __init__(self):
        pin_nums = [
            board.GP6,  # 1
            board.GP7,  # 2
            board.GP8,  # 3
            board.GP9,  # 4
            board.GP17, # 5
            board.GP16, # 6
            board.GP15, # 7
            board.GP14, # 8
            board.GP5,  # Next Page
            board.GP2,  # Encoder push
        ]
        self.buttons = [io.DigitalInOut(i) for i in pin_nums]
        for b in self.buttons:
            b.direction = io.Direction.INPUT
            b.pull = io.Pull.UP
            
        self.last_values = self.get_all()
            
    def get_all(self):
        # Converts the inputs to an integer with 1 set if the button is pressed
        # Note inputs come in logically inverted (a press means the bit is 0!)
        return sum([int(not b.value) << i for i, b in enumerate(self.buttons)])
    
    def get_changes(self):
        ''' Returns a tuple of (all changes bits, rising edges that have occurred,
        falling edges that have occurred)'''
        new_values = self.get_all()
        changes = new_values ^ self.last_values
        r = changes & new_values
        f = changes & ~new_values
        self.last_values = new_values
        return changes, r, f
    
    def __len__(self):
        return len(self.buttons)
    
    def edges_to_list(self, edges):
        return [i for i in range(len(self.buttons)) if (edges & (1 << i))]
    
    
class Encoder():
    def __init__(self):
        self.encoder = rotaryio.IncrementalEncoder(board.GP4, board.GP3)
        self.last_pos = self.encoder.position
        
    def get_delta(self):
        new_pos = self.encoder.position
        delta = new_pos - self.last_pos
        self.last_pos = new_pos
        return delta
    
    
class Key():
    def __init__(self, name, presses, keyboard, layout):
        # Max key name length is 5 chars
        self.name = name[:5]
        self.presses = presses
        self.kbd = keyboard
        self.layout = layout
        
        # Verify presses is sensible
        if not isinstance(presses, (int, str, list, tuple)) \
                and presses is not None \
                and not callable(presses):
            # Get the display manager. This is a bit dirty, should
            # probably use a singleton or something
            global dm
            dm.show_err("Failed to set up\nkey {}".format(self.name))
            time.sleep(3)
            self.presses = None
            
        if isinstance(presses, (list, tuple)):
            for press in presses:
                if not isinstance(press, int):
                    global dm
                    dm.show_err("Failed to set up\nkey {} - bad element\nin list".format(self.name))
                    time.sleep(3)
                    self.presses = None
    
    def press(self):
        if isinstance(self.presses, str):
            self.layout.write(self.presses)
        elif isinstance(self.presses, int):
            self.kbd.press(self.presses)
        elif isinstance(self.presses, (list, tuple)):
            # This assumes any list or tuple is all integers from Keycode
            self.kbd.press(*self.presses)
        elif callable(self.presses):
            try:
                self.presses(self.kbd, self.layout)
            except Exception:
                global dm
                dm.show_err("Failed to run function\nfor key {}".format(self.name))
                # No need for a sleep here, there's nothing that should
                # overwrite the screen immediately.
            
            
    def release(self):
        if isinstance(self.presses, int):
            self.kbd.release(self.presses)
        elif isinstance(self.presses, (list, tuple)):
            # This assumes any list or tuple is all integers from Keycode
            self.kbd.release(*self.presses)
            

class Page():
    def __init__(self, name):
        self.name = name
        self.keys = []
        
    def add_key(self, key):
        if len(self.keys) < 8:
            self.keys.append(key)
    
    def press(self, n):
        try:
            self.keys[n].press()
        except IndexError:
            pass
    
    def release(self, n):
        try:
            self.keys[n].release()
        except IndexError:
            pass
        
    def get_key_names(self):
        names = [""] * 8
        for i, k in enumerate(self.keys):
            names[i] = k.name
        return names
    

class PageManager():
    def __init__(self, pages, keyboard, layout):
        # Load configuration
        self.pages = []
        for page in pages:
            new_page = Page(page[0])
            for key in page[1]:
                new_key = Key(key[0], key[1], keyboard, layout)
                new_page.add_key(new_key)
            self.pages.append(new_page)
            
        self.current_index = 0
        
    def next_page(self):
        self.current_index = (self.current_index + 1) % len(self.pages)
        
    def __len__(self):
        return len(self.pages)
    
    @property
    def current_page(self):
        return self.pages[self.current_index]
    
    def press(self, k):
        self.current_page.press(k)
        
    def release(self, k):
        self.current_page.release(k)
        
        
# Default pages - don't change these. Make changes in keys.py

def launch_command_line(keys, text):
    """
    Example function that will launch the command line on Windows machines
    """
    keys.send(Keycode.WINDOWS, Keycode.R)
    time.sleep(0.1)
    text.write("cmd")
    keys.send(Keycode.ENTER)

default_pages = (
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
        
# Set up external USB connections
dm.set_loading_bar(21)
kbd = Keyboard(usb_hid.devices)
dm.set_loading_bar(42)
layout = KeyboardLayout(kbd)
dm.set_loading_bar(63)
cctl = ConsumerControl(usb_hid.devices)
dm.set_loading_bar(84)

# Load pages
try:
    pages = keys.pages
except Exception as e:
    dm.show_err("User defined keys\nimport failed.\nLoading defaults...")
    time.sleep(5)
    pages = default_pages
    dm.show_splash_screen(84)

pm = PageManager(pages, kbd, layout)
dm.set_loading_bar(105)

more_than_4_pages = len(pm) > 4
leds = Leds(show_binary=more_than_4_pages)

encoder = Encoder()
buttons = Buttons()

leds.show(pm.current_index)
dm.set_loading_bar(128)
time.sleep(0.3)

dm.show_page(pm.current_page)

try:
    while True:
        try:
            _, pushed, released = buttons.get_changes()
            pushed = buttons.edges_to_list(pushed)
            # Ignore releasing the encoder and next page buttons
            released = buttons.edges_to_list(released & 0xFF)
            
            if 8 in pushed:
                # Next page button pressed
                pm.next_page()
                leds.show(pm.current_index)
                dm.show_page(pm.current_page)
                pushed.remove(8)
                
            if 9 in pushed:
                # Encoder pressed
                cctl.send(rotary_press_function)
                pushed.remove(9)
                
            for k in pushed:
                pm.press(k)
                
            for k in released:
                pm.release(k)
            
            # Handle encoder changes
            d = encoder.get_delta()
            while d:
                if d > 0:
                    cctl.send(ConsumerControlCode.VOLUME_INCREMENT)
                    d -= 1
                if d < 0:
                    cctl.send(ConsumerControlCode.VOLUME_DECREMENT)
                    d += 1
        
        # Catch everything except a keyboard interrupt (which is how
        # requests from Thonny come in)
        except KeyboardInterrupt:
            raise
        
        except Exception as e:
            print("Exception occurred, continuing anyway...")
            print(e)
            pass
        
            
except Exception as e:
    i2c.deinit()
    raise e
