from machine import Pin
import time
import json


class AnimPlayer:
    HOLD_TIME = 0.003
    
    def __init__(self, anodes, cathodes):
        self.anodes = anodes
        self.cathodes = cathodes
        self.anim = None
        self.frame_num = 0
        self.frame_start_time = time.ticks_ms()
        self.frame_time_ms = 100
        self.num_frames = 0
        
    def load_frames(self, frames):
        self.anim = frames
        self.frame_num = 0
        self.num_frames = len(frames)
        
    def set_framerate(self, framerate):
        self.frame_time_ms = 1000.0 / framerate
        
    # Run one display cycle
    def run_cycle(self):
        frame = self.anim[self.frame_num]
        
        for a_num, a in enumerate(self.anodes):
            # Extracts the current layer LED info
            current_layer = (frame >> (a_num * 9)) & 0x1FF
            
            # Calculate the correct bit positions for the
            # GPIOs that should be on
            outputs_on = current_layer << 4 | (1 << (a_num + 13))
            machine.mem32[GPIO_SET] = outputs_on
            
            # Wait, then clear all LED outputs
            time.sleep(self.HOLD_TIME)
            machine.mem32[GPIO_CLR] = 0xFFF0
        
        if time.ticks_diff(time.ticks_ms(), self.frame_start_time) >= self.frame_time_ms:
            self.frame_num = (self.frame_num + 1) % self.num_frames
            self.frame_start_time = time.ticks_ms()
                    

def btn_press(ev):
    global next_anim, last_press_ms
    now = time.ticks_ms()
    if time.ticks_diff(now, last_press_ms) < DEBOUNCE_MS:
        return  # Ignore anything too soon, rising or falling
    last_press_ms = now
    if ev.value() == 0:  # Only act on falling edge
        next_anim = True
        

def light_one_by_one(delay):
    for a in anodes:
        a.on()
        for c in cathodes:
            c.on()
            time.sleep(delay)
            c.off()
        a.off()
        
def light_layer_by_layer(delay):    
    for c in cathodes:
        c.on()

    for a in anodes:
        a.on()
        time.sleep(delay)
        a.off()
    
    for c in cathodes:
        c.off()
        
################################################
# PIN SETUP
################################################

cathodes = [
    Pin(4, mode=Pin.OUT),
    Pin(5, mode=Pin.OUT),
    Pin(6, mode=Pin.OUT),
    Pin(7, mode=Pin.OUT),
    Pin(8, mode=Pin.OUT),
    Pin(9, mode=Pin.OUT),
    Pin(10, mode=Pin.OUT),
    Pin(11, mode=Pin.OUT),
    Pin(12, mode=Pin.OUT),
]

anodes = [
    Pin(13, mode=Pin.OUT),
    Pin(14, mode=Pin.OUT),
    Pin(15, mode=Pin.OUT),
]

button = Pin(16, mode=Pin.IN, pull=Pin.PULL_UP)
button.irq(handler=btn_press, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)

################################################
# Constants
################################################

SIO_BASE  = 0xd0000000
GPIO_OUT  = SIO_BASE + 0x010  # full output register
GPIO_SET  = SIO_BASE + 0x014  # atomic set   (1 = set that pin HIGH)
GPIO_CLR  = SIO_BASE + 0x018  # atomic clear (1 = set that pin LOW)

DEBOUNCE_MS = 200

################################################
# Animation definition
################################################

frames = [0x00001FF, 0x003FFFF, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFE00, 0x7FC0000, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 
          0x70381C0, 0x7E3F1F8, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x0FC7E3F, 0x01C0E07, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 
          0x4924924, 0x6DB6DB6, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x36DB6DB, 0x1249249, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, ]

animations2 = [
    {
        "name": "push through each direction",
        "frames": [0x00001FF, 0x003FFFF, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFE00, 0x7FC0000, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 
                  0x70381C0, 0x7E3F1F8, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x0FC7E3F, 0x01C0E07, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 
                  0x4924924, 0x6DB6DB6, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x36DB6DB, 0x1249249, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
        "framerate": 15
    },
    {
        "name": "every-other",
        "frames": [0xAAAAAAA, 0x5555555],
        "framerate": 2,
    },
    {
        "name": "spinning-around",
        "frames": [0x2492492, 0x150A854, 0x0E07038, 0x4462311],
        "framerate": 8,
    },
    
]

animations3 = [
    {
        "name": "Test 1",
        "frames": [
            261632,
            511,
            133955584
        ],
        "framerate": 3
    },
    {
        "name": "Test 2",
        "frames": [
            38347922,
            76695844,
            19173961
        ],
        "framerate": 2
    }
]


# Load JSON animations
try:
    with open("animations.json", "r") as f:
        animations = json.load(f)
except:
    animations = [
        {
            "name": "push through each direction",
            "frames": [0x00001FF, 0x003FFFF, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFE00, 0x7FC0000, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 
                      0x70381C0, 0x7E3F1F8, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x0FC7E3F, 0x01C0E07, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 
                      0x4924924, 0x6DB6DB6, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x36DB6DB, 0x1249249, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            "framerate": 15
        },
        {
            "name": "every-other",
            "frames": [0xAAAAAAA, 0x5555555],
            "framerate": 2,
        },
        {
            "name": "spinning-around",
            "frames": [0x2492492, 0x150A854, 0x0E07038, 0x4462311],
            "framerate": 8,
        },
        
    ]
    
with open("animations.json", "r") as f:
    animations = json.load(f)


global next_anim, last_press_ms
next_anim = False
last_press_ms = 0

# Set up animator
player = AnimPlayer(anodes, cathodes)

animation_index = 0

player.load_frames(animations[animation_index]["frames"])
player.set_framerate(animations[animation_index]["framerate"])

while True:
    player.run_cycle()
    if next_anim:
        next_anim = False
        animation_index += 1
        if animation_index >= len(animations):
            animation_index = 0
        player.load_frames(animations[animation_index]["frames"])
        player.set_framerate(animations[animation_index]["framerate"])
    
    
    