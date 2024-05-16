import digitalio as io
import board
import time
import busio
import rotaryio
import adafruit_ssd1306

page = 0
num_pages = 16

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
        # Converts the inputs to an integer with 1 set if the input is high
        return sum([int(b.value) << i for i, b in enumerate(self.buttons)])
    
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
        
        
    
                
leds = Leds(show_binary=True)
encoder = Encoder()
buttons = Buttons()

i2c = busio.I2C(board.GP1, board.GP0)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

display.fill(0)
display.show()
display.text("Hello", 0, 0, 1)
display.text("Hi", 10, 10, 1)
display.show()

height = 0

try:
    while True:
        _, pushed, _ = buttons.get_changes()
        pushed = buttons.edges_to_list(pushed)
        if 8 in pushed:
            page = (page + 1) % num_pages
            leds.show(page)
            pushed.remove(8)
        if 9 in pushed:
            # Encoder pressed
            display.fill_rect(0, 10, 20, 8, 0)
            display.text("Mute", 0, 10, 1)
            display.show()
            pushed.remove(9)
        for i in pushed:
            display.fill_rect(0, 0, 20, 8, 0)
            display.text("{}".format(i), 0, 0, 1)
            display.show()
        
        d = encoder.get_delta()
        if d:
            height += d
            height = min(height, 31)
            height = max(0, height)
            display.fill_rect(100, 0, 32, 28, 0)
            display.fill_rect(100, 0, height, 28, 1)
            display.show()
        
            
except Exception as e:
    i2c.deinit()
    raise e
