import array
import board
import digitalio
import json
import time

import adafruit_pioasm
import rp2pio

################################################
# PIO program — runs at 10 kHz (1 cycle = 0.1 ms)
# Per-layer cycle: pull word → drive pins for 30 cycles (3 ms) → clear pins
# Full 3-layer mux cycle ≈ 102 cycles = 10.2 ms → ~98 Hz refresh
#
# Word format fed by DMA:
#   bits  0-8  → cathode states  (maps to GP4-GP12 via out pins)
#   bits  9-11 → anode enable    (GP13=layer0, GP14=layer1, GP15=layer2)
################################################

PIO_FREQ = 10_000

led_mux_asm = adafruit_pioasm.assemble("""
.program led_mux
.wrap_target
    pull block       ; wait for layer word (DMA keeps FIFO full)
    out  pins, 12    ; drive cathodes (bits 0-8) + anode (bit 9-11)
    nop  [29]        ; hold for 30 cycles = 3 ms
    mov  osr, null   ; load zero into OSR
    out  pins, 12    ; clear all 12 LED pins
.wrap
""")


def frame_to_buf(frame, buf):
    """Expand a 27-bit packed frame into 3 PIO output words in-place."""
    for layer in range(3):
        cathodes = (frame >> (layer * 9)) & 0x1FF
        buf[layer] = cathodes | (1 << (layer + 9))


class AnimPlayer:
    def __init__(self, buf):
        self.buf = buf
        self.anim = None
        self.frame_num = 0
        self.frame_start_time = time.monotonic()
        self.frame_time_s = 0.1
        self.num_frames = 0

    def load_frames(self, frames):
        self.anim = frames
        self.frame_num = 0
        self.num_frames = len(frames)
        frame_to_buf(frames[0], self.buf)

    def set_framerate(self, framerate):
        self.frame_time_s = 1.0 / framerate

    def tick(self):
        if time.monotonic() - self.frame_start_time >= self.frame_time_s:
            self.frame_num = (self.frame_num + 1) % self.num_frames
            self.frame_start_time = time.monotonic()
            frame_to_buf(self.anim[self.frame_num], self.buf)


################################################
# PIO STATE MACHINE — takes over GP4-GP15
################################################

sm = rp2pio.StateMachine(
    led_mux_asm,
    frequency=PIO_FREQ,
    first_out_pin=board.GP4,
    out_pin_count=12,
    out_shift_right=True,
    auto_pull=False,
)

################################################
# BUTTON — stays as regular digitalio on GP16
################################################

button = digitalio.DigitalInOut(board.GP16)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

DEBOUNCE_S = 0.2

################################################
# LOAD ANIMATIONS
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

################################################
# START — DMA loops frame_buf into PIO indefinitely
################################################

frame_buf = array.array('L', [0, 0, 0])
sm.background_write(loop=frame_buf)

next_anim = False
last_press_s = 0.0
prev_button = True

player = AnimPlayer(frame_buf)

animation_index = 0
player.load_frames(animations[animation_index]["frames"])
player.set_framerate(animations[animation_index]["framerate"])

################################################
# MAIN LOOP — PIO handles mux; Python advances frames and polls button
################################################

while True:
    player.tick()

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
