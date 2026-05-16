import board
import digitalio
import time
import json


class AnimPlayer:
    HOLD_TIME = 0.003

    def __init__(self, anodes, cathodes):
        self.anodes = anodes
        self.cathodes = cathodes
        self.anim = None
        self.frame_num = 0
        self.frame_start_time = time.monotonic()
        self.frame_time_s = 0.1
        self.num_frames = 0

    def load_frames(self, frames):
        self.anim = frames
        self.frame_num = 0
        self.num_frames = len(frames)

    def set_framerate(self, framerate):
        self.frame_time_s = 1.0 / framerate

    def run_cycle(self):
        frame = self.anim[self.frame_num]

        for a_num, a in enumerate(self.anodes):
            current_layer = (frame >> (a_num * 9)) & 0x1FF

            # Set cathodes and anode, wait, then clear
            for c_num, c in enumerate(self.cathodes):
                c.value = bool(current_layer & (1 << c_num))
            a.value = True

            time.sleep(self.HOLD_TIME)

            a.value = False
            for c in self.cathodes:
                c.value = False

        if time.monotonic() - self.frame_start_time >= self.frame_time_s:
            self.frame_num = (self.frame_num + 1) % self.num_frames
            self.frame_start_time = time.monotonic()


def make_output(pin):
    p = digitalio.DigitalInOut(pin)
    p.direction = digitalio.Direction.OUTPUT
    return p


################################################
# PIN SETUP
################################################

cathodes = [
    make_output(board.GP4),
    make_output(board.GP5),
    make_output(board.GP6),
    make_output(board.GP7),
    make_output(board.GP8),
    make_output(board.GP9),
    make_output(board.GP10),
    make_output(board.GP11),
    make_output(board.GP12),
]

anodes = [
    make_output(board.GP13),
    make_output(board.GP14),
    make_output(board.GP15),
]

button = digitalio.DigitalInOut(board.GP16)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

################################################
# Constants
################################################

DEBOUNCE_S = 0.2

################################################
# Load animations
################################################

try:
    with open("animations.json", "r") as f:
        animations = json.load(f)
except OSError:
    animations = [
        {
            "name": "push through each direction",
            "frames": [0x00001FF, 0x003FFFF, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFE00, 0x7FC0000, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                       0x70381C0, 0x7E3F1F8, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x0FC7E3F, 0x01C0E07, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                       0x4924924, 0x6DB6DB6, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x7FFFFFF, 0x36DB6DB, 0x1249249, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            "framerate": 15,
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

next_anim = False
last_press_s = 0.0
prev_button = True  # pull-up: idle HIGH

player = AnimPlayer(anodes, cathodes)

animation_index = 0
player.load_frames(animations[animation_index]["frames"])
player.set_framerate(animations[animation_index]["framerate"])

while True:
    player.run_cycle()

    # Poll button — detect falling edge to replace MicroPython IRQ
    btn = button.value
    now = time.monotonic()
    if not btn and prev_button and (now - last_press_s) >= DEBOUNCE_S:
        last_press_s = now
        next_anim = True
    prev_button = btn

    if next_anim:
        next_anim = False
        animation_index = (animation_index + 1) % len(animations)
        player.load_frames(animations[animation_index]["frames"])
        player.set_framerate(animations[animation_index]["framerate"])
