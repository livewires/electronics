import digitalio as io
import board
import time
import rotaryio
from collections import OrderedDict
from adafruit_hid.keycode import Keycode


import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

from display_manager import DisplayManager
from keys import pages, rotary_press_function

dm = DisplayManager()
dm.show_splash_screen()

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
            board.GP6,
            board.GP7,
            board.GP8,
            board.GP9,
            board.GP17,
            board.GP16,
            board.GP15,
            board.GP14,
            board.GP5,
            board.GP2,
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
    
    def press(self):
        if isinstance(self.presses, str):
            self.layout.write(self.presses)
        elif isinstance(self.presses, int):
            self.kbd.press(self.presses)
        elif isinstance(self.presses, (list, tuple)):
            # This assumes any list or tuple is all integers from Keycode
            self.kbd.press(*self.presses)
            
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
        
        
dm.set_loading_bar(21)
kbd = Keyboard(usb_hid.devices)
dm.set_loading_bar(42)
layout = KeyboardLayoutUS(kbd)
dm.set_loading_bar(63)
cctl = ConsumerControl(usb_hid.devices)
dm.set_loading_bar(84)

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
        _, pushed, released = buttons.get_changes()
        pushed = buttons.edges_to_list(pushed)
        released = buttons.edges_to_list(released & 0xFF)
        
        if 8 in pushed:
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
        
        d = encoder.get_delta()
        while d:
            if d > 0:
                print("Volume up")
                cctl.send(ConsumerControlCode.VOLUME_INCREMENT)
                d -= 1
            if d < 0:
                
                print("Volume down")
                cctl.send(ConsumerControlCode.VOLUME_DECREMENT)
                d += 1
        
            
except Exception as e:
    i2c.deinit()
    raise e
