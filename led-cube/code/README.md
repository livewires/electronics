# Loading the code onto a Pico

## 1. Flash CircuitPython

Hold the **BOOTSEL** button on the Pico, plug it into USB, then release BOOTSEL.  
The Pico will appear as a USB drive called **RPI-RP2**.

Copy the firmware onto that drive:

```
adafruit-circuitpython-raspberry_pi_pico-en_GB-10.2.1.uf2  →  RPI-RP2
```

The Pico will reboot automatically and reappear as **CIRCUITPY**.

## 2. Copy the code

Copy the contents of the `circuitpython/` folder to the root of the CIRCUITPY drive:

```
circuitpython/
├── code.py           →  CIRCUITPY/code.py
├── animations.json   →  CIRCUITPY/animations.json
└── lib/
    └── adafruit_pioasm.mpy  →  CIRCUITPY/lib/adafruit_pioasm.mpy
```

The Pico will run `code.py` automatically as soon as the files are in place.

## How it works

The cube has 27 LEDs arranged in a 3×3×3 grid. Rather than wiring each LED individually, they share connections by layer — only one layer is switched on at a time, but they cycle through fast enough (~98 times per second) that all three appear lit at once.

This cycling is handled by the Pico's PIO hardware, which runs independently in the background so Python doesn't have to worry about the timing. Python's only job is to advance through the animation frames at the right speed and update which LEDs should be on.

Animations are loaded from `animations.json`. Each animation has a list of frames and a framerate. Pressing the button on GP16 skips to the next animation.
