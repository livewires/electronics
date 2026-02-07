# LiveWires Analogue Synthesiser


## Specification

 * Total range: 5 octaves (C1 to C6)
 * Keyboard: 1 octave capacitive touch keyboard
 * Wave generator: Sine wave
 * Low Frequency Oscillator (LFO) to control volume
 * Attack and Release envelopes
 * Overdrive for distortion
 * Low Pass Filter (LPF) with cutoff and resonance control
 * 3.5mm jack output for headphones


## Pictures



## How it works

13 capacitive touch keys (plus an additional two control buttons) are read by the pi pico. The pico generates a sine wave and outputs it using Pulse Width Modulation (PWM) to simulate an analogue output (since the pico doesn't come equipped with a DAC onboard). This signal is low-pass-filtered using a 2nd order RC filter, which makes it more closely approximate a sine wave.

An LFO generates a low-frequency (~0.05 - 5Hz) triangle wave. The Pico also outputs a digital signal that indicates whether a key is pressed, which is filtered by the Attack-Release (AR) circuitry. 

The voltage controlled amplifier (VCA) amplifies the sine wave by the control signal, which is the combination of the LFO and AR outputs.

The VCA output is then fed through the Low Pass Filter. 

[![](https://mermaid.ink/img/pako:eNo9jkFvgkAQhf_KZk5tao2wwJY9NEGUmtRW4qEmXTxsZRQSYM26tLXqfy8CcU7z3ptvZk6wUSkCh22hfjaZ1IbMl0lFmpqIebRY9z15fHwm07uH-04HIs5JnG_U-hqcV_Ibz2Qm4tUbifLCoO65WcuNxUcY9E7QAu_KIFlUZxKKYNknYXejE9MO7MS4FZGYx1E_G7XOi5ihTPeZqvDQB0vxiscvJXXafkYCGMBO5ynwrSwOOIASdSmvGk5XIgGTYYkJ8KZNcSvrwiSQVJeG28vqU6kSuNF1Q2pV77LbnnqfSoOTXO60LG-uxipFHaq6MsAZ89slwE_wC9yhQ58xarsO9R2XWrY7gCNw2x8NHdum1GYe9ZjlXwbw154dDZlrWZbDXDryfPvJcy__NUN6OQ?type=png)](https://mermaid.live/edit#pako:eNo9jkFvgkAQhf_KZk5tao2wwJY9NEGUmtRW4qEmXTxsZRQSYM26tLXqfy8CcU7z3ptvZk6wUSkCh22hfjaZ1IbMl0lFmpqIebRY9z15fHwm07uH-04HIs5JnG_U-hqcV_Ibz2Qm4tUbifLCoO65WcuNxUcY9E7QAu_KIFlUZxKKYNknYXejE9MO7MS4FZGYx1E_G7XOi5ihTPeZqvDQB0vxiscvJXXafkYCGMBO5ynwrSwOOIASdSmvGk5XIgGTYYkJ8KZNcSvrwiSQVJeG28vqU6kSuNF1Q2pV77LbnnqfSoOTXO60LG-uxipFHaq6MsAZ89slwE_wC9yhQ58xarsO9R2XWrY7gCNw2x8NHdum1GYe9ZjlXwbw154dDZlrWZbDXDryfPvJcy__NUN6OQ)



## Setting up for the camp?

This should only need to be done by the leader running the sessions on the camp. This is what needs doing in advance:

* PCB needs ordering
* Components need kitting
* Pico needs soldering
* Pico needs software installing

#### PCB 

This is a non-etch project. The PCB is ordered from JLCPCB or a similar service using the gerber files. These can be found in the version's output folder (in [here](synth-v3-pcb/releases/)). Look for `*-gerbers.zip`. 

> [!IMPORTANT]
> These will take a few weeks to arrive so needs doing in plenty of time!

The JLCPCB ordering details are as follows:
* Basic Info
  * Base material: FR4
  * Layers: 2
  * Dimensions: [Automatic based on PCB gerbers]
  * Product type: Industrial/Consumer Electronics
* PCB Specification
  * Different Design: 1
  * Delivery Format: Single PCB
  * PCB Thicknes: 1.6mm
  * PCB Color: Black
  * Silkscreen: White
  * Material type: <doesn't matter, cheapest>
  * Surface finish: "LeadFree HASL" or "ENIG"
* High-Spec Options
  * Outer copper weight: 1oz
  * Via covering: Tented
  * Via plating method: Not specified
  * Min via hole size/diameter: 0.3mm <largest and therefore cheapest minimum at time of writing. Actual via diameter in board design is 0.35mm>
  
All other options set to cheapest option, usually defaults



### Components

Components list is in the BOM. For example, the revision 3.1 BOM can be found at [synth-v3-pcb/releases/lw-synth-v3.1/full-project-bom_rev_3.1.ods](synth-v3-pcb/releases/lw-synth-v3.1/full-project-bom_rev_3.1.ods). 

Knobs can be ordered for this project, but if available, 3D printed ones are easier and cheaper. The files for this can be found in `electronics/components/knobs`. If you are ordering some, be aware that some knobs you can order don't have the correct orientation of the ident in relation to the D of the potentiometer shaft. 

### Soldering the Pico

To save money, we're ordering the Pi Pico un-soldered. This means a leader will have to solder the two 20-pin headers to the Pico. They should protrude from the bottom of the Pico (i.e. the side with no components on), so the solder goes on the top of the board (i.e. the side _with_ the components on). 

#### Making a Jig

See the readme for the macropad project.

### Setting up the Pico's software

The software for the pico is written in C (not micropython, like the macropad). This means you simply need to copy [lw-synth.uf2](lw-synth.uf2) to the Pico's drive. 

