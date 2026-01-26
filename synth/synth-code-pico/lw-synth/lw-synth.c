/**
 * Copyright (c) 2020 Raspberry Pi (Trading) Ltd.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */

// Fade an LED between low and high brightness. An interrupt handler updates
// the PWM slice's output level each time the counter wraps.

#include "pico/stdlib.h"
#include <stdio.h>
#include "pico/time.h"
#include "hardware/irq.h"
#include "hardware/pwm.h"
#include "hardware/dma.h"
#include "sine_table.h"

/********************************************************
 * System configuration
 ********************************************************/


/********************************************************
 * Pin defines
 ********************************************************/

 #define WAVE_PIN 28
 #define NOTE_ON_PIN 27

 #define CAP_PIN 22

 /* LEDs are pins 3 to 7 */
 #define LEDS_ALL (0x000000F8)

 /* Explain the below */

 #define CAP_PINS_30us ( \
     (0x1 << 10) | \
     (0x1 << 12) | \
     (0x1 << 16) | \
     (0x1 << 18) | \
     (0x1 << 15) | \
     (0x1 << 14))

 #define CAP_PINS_40us ( \
     (0x1 << 20))

 #define CAP_PINS_50us ( \
     (0x1 << 19) | \
     (0x1 << 17) | \
     (0x1 << 11))

 #define CAP_PINS_60us ( \
     (0x1 << 13) | \
     (0x1 <<  9) | \
     (0x1 << 21) | \
     (0x1 <<  8))

 #define CAP_PINS_70us ( \
     (0x1 << 22))

 #define CAP_PINS_ALL (CAP_PINS_30us | CAP_PINS_40us | CAP_PINS_50us | CAP_PINS_60us | CAP_PINS_70us)

 #define OCTAVE_UP (1u << 14)
 #define OCTAVE_DN (1u << 13)


 /********************************************************
  * Macros
  ********************************************************/

#define NOTE_ON() gpio_put(NOTE_ON_PIN, 0)
#define NOTE_OFF() gpio_put(NOTE_ON_PIN, 1)


/********************************************************
 * Constants and peripherals
 ********************************************************/

/* Library of note frequencies - quicker than calculating them each time! */
float note_freqs[] = {
    // C1 to B1
    32.703, 34.648, 36.708, 38.891, 41.203, 43.654, 46.249, 48.999, 51.913, 55.000, 58.270, 61.735,
    // C2 to B2
    65.406, 69.296, 73.416, 77.782, 82.407, 87.307, 92.499, 97.999, 103.826, 110.000, 116.541, 123.471,
    // C3 to B3
    130.813, 138.591, 146.832, 155.563, 164.814, 174.614, 184.997, 195.998, 207.652, 220.000, 233.082, 246.942,
    // C4 to B4
    261.626, 277.183, 293.665, 311.127, 329.628, 349.228, 369.994, 391.995, 415.305, 440.000, 466.164, 493.883,
    // C5 to B5
    523.251, 554.365, 587.330, 622.254, 659.255, 698.456, 739.989, 783.991, 830.609, 880.000, 932.328, 987.767,
    // C6
    1046.502
};

/* PWM peripheral */
uint pwm_slice_num;


/********************************************************
 * System state variables
 ********************************************************/

/* The single C-to-C octave on the keyboard is currently representing which octave? */
static int current_octave = 2;

/* How quickly should the target note be reached? 1.0 means change instantly (i.e. no glide),
 * smaller fractions will increase the glide time. The actual glide time is a function of
 * glide_factor and the cycle time. */
static float glide_factor = 1.0f;

/* We calculate the next sample's value by tracking the phase on the output wave. Each time we need
 * a new sample, the phase is increased by sample_time/frequency. This is scaled so that we can
 * do all the calculations in integer maths.
 */
uint32_t phase_increment_per_sample;


/********************************************************
 * Helper functions
 ********************************************************/

/* Returns the index of the most significant high bit. -1 if no bits are high */
int msb_index(uint32_t x) {
    if (x == 0) {
        // no bits set
        return -1;
    }

    int index = 0;
    // shift right until x == 0
    while (x >>= 1) {
        index++;
    }
    return index;
}


/********************************************************
 * LED pins
 ********************************************************/

/* Set up the LED outputs */
void leds_init() {
    gpio_init_mask(LEDS_ALL);
    gpio_set_dir_out_masked(LEDS_ALL);
}

/* Sets LEDs to on or off. Left-most LED is bit zero */
void leds_set(uint8_t s) {
    /* LEDs start at pin index 3, outputs are logically inverted, i.e. setting to zero turns
     * the LED on */
    uint32_t values = (~s << 3) & LEDS_ALL;
    gpio_put_masked(LEDS_ALL, values);
}


/********************************************************
 * Capacitive touch buttons
 ********************************************************/

/* Initialise capacitive touch button inputs */
void buttons_init() {
    // Initialize all CAP pins
    gpio_init_mask(CAP_PINS_ALL);

    // Disable pulls (must be done per-pin)
    for (uint gpio = 0; gpio < 30; gpio++) {
        if (CAP_PINS_ALL & (1u << gpio)) {
            gpio_set_pulls(gpio, false, false);
        }
    }

    // Set all CAP pins as outputs
    gpio_set_dir_out_masked(CAP_PINS_ALL);

    // Drive all CAP pins HIGH
    gpio_set_mask(CAP_PINS_ALL);

    // Set all CAP pins back to inputs (hi-Z)
    gpio_set_dir_in_masked(CAP_PINS_ALL);
}

/* Read the state of all the capacitive touch buttons. Each bit is high if the button is pressed.
 *
 * Bit 0 is low C, bit 1 is C# etc. Bit 13 is Octave Down button, bit 14 is Octave Up button */
uint32_t buttons_read() {
    uint32_t buttons = 0;

    // Set all the pins as outputs. Should already be set to high by buttons_init().
    gpio_set_dir_out_masked(CAP_PINS_ALL);
    sleep_us(10);
    /* Set all pins back to input, i.e. high impedance. They each have a 1M resistor to ground, so
     * the fall time of the pin will change as the capacitance on the pin changes. Because each pin
     * has a different track length and shape, the threshold for a pin being touched varies by pin,
     * hence checking different pins at different times. */
    gpio_set_dir_in_masked(CAP_PINS_ALL);
    sleep_us(30);
    buttons |= ~gpio_get_all() & CAP_PINS_30us;
    sleep_us(10);
    buttons |= ~gpio_get_all() & CAP_PINS_40us;
    sleep_us(10);
    buttons |= ~gpio_get_all() & CAP_PINS_50us;
    sleep_us(10);
    buttons |= ~gpio_get_all() & CAP_PINS_60us;
    sleep_us(10);
    buttons |= ~gpio_get_all() & CAP_PINS_70us;

    /* Map input values (raw pin numbers) to sensible order */

    buttons = ~buttons;
    uint32_t out = 0;

    // 1️⃣ Output bits 0..5 = inputs 8..13, reversed
    uint8_t bits_8_13 = (buttons >> 8) & 0x3F;     // extract 6 bits
    uint8_t rev_bits = 0;
    for (int i = 0; i < 6; i++) {
        rev_bits |= ((bits_8_13 >> i) & 1) << (5 - i);
    }
    out |= ((uint32_t)rev_bits) << 0;

    // 2️⃣ Output bits 6..12 = inputs 16..22
    out |= ((buttons >> 16) & 0x7F) << 6;

    // 3️⃣ Output bits 13..14 = inputs 14 & 15
    out |= ((buttons >> 14) & 0x03) << 13;

    return out;
}


/********************************************************
 * PWM wave output
 ********************************************************/

/* Sets the frequency of the output wave */
void wave_set_freq(float freq) {
    /* times by 128 for added precision when cast to integer */
    uint64_t fp = (uint32_t) (freq * 128);
    /* times by 512 for number of samples in sine table */
    phase_increment_per_sample = (fp << 9) / 40690;
}

/* This function runs each time the PWM cycle goes round, i.e. it runs on every single sample, so
 * it needs to be as light as possible. */
void on_pwm_wrap() {
    static uint64_t phase = 0;

    // Clear the interrupt flag that brought us here
    pwm_clear_irq(pwm_slice_num);

    phase += phase_increment_per_sample;

    pwm_set_chan_level(pwm_slice_num, PWM_CHAN_A, sineLookupTable[(phase >> 7) & 0x1FF]);
}

/* Initialise the wave output pins etc. */
void wave_init(void) {
    gpio_set_function(WAVE_PIN, GPIO_FUNC_PWM);
    gpio_init(NOTE_ON_PIN);
    gpio_set_dir(NOTE_ON_PIN, GPIO_OUT);
    gpio_put(NOTE_ON_PIN, 1);

    wave_set_freq(440);

    pwm_slice_num = pwm_gpio_to_slice_num(WAVE_PIN);
    pwm_clear_irq(pwm_slice_num);
    pwm_set_irq_enabled(pwm_slice_num, true);
    irq_set_exclusive_handler(PWM_DEFAULT_IRQ_NUM(), on_pwm_wrap);
    irq_set_enabled(PWM_DEFAULT_IRQ_NUM(), true);

    /* Set up PWM peripheral for the following:
     *   - Duty cycle of ~25µs (~40kHz) which effectively becomes system's sampling freq
     *   - Output resolution of 1024, must match resolution of sine table
     */

    // Get some sensible defaults for the slice configuration. By default, the
    // counter is allowed to wrap over its maximum range (0 to 2**16-1)
    pwm_config config = pwm_get_default_config();
    // Set divider, reduces counter clock to sysclock/this value
    // Divide 125MHz by 3 and you get 41.6MHz
    pwm_config_set_clkdiv(&config, 3.f);
    // Load the configuration into our PWM slice, and set it running.
    // 41.6MHz / 1024 = 40.7kHz effective sample rate
    pwm_config_set_wrap(&config, 1023);
    pwm_init(pwm_slice_num, &config, true);
}


/********************************************************
 * Business logic
 ********************************************************/

void process_octave_buttons(uint32_t inputs, uint32_t time_now_ms) {
    static uint32_t last_time_event_occurred = -50;
    static uint32_t last_button_state = 0;

    /* Extract octave buttons and look for rising edges */
    uint32_t button_state = inputs & 0x6000;
    uint32_t rising_edges = button_state & ~last_button_state;
    // update for next loop
    last_button_state = button_state;

    /* Don't take any action if we took an action in the last 50ms - crude debouncing */
    if (time_now_ms - last_time_event_occurred < 50) {
        return;
    }

    if (rising_edges & OCTAVE_UP) {
        current_octave++;
        last_time_event_occurred = time_now_ms;
    }

    if (rising_edges & OCTAVE_DN) {
        current_octave--;
        last_time_event_occurred = time_now_ms;
    }

    if (current_octave < 0) {
        current_octave = 0;
    }

    if (current_octave > 4) {
        current_octave = 4;
    }
}

int main() {
    leds_init();
    buttons_init();
    wave_init();

    uint32_t time_ctr = 0;

    float target_freq = 0;
    float current_freq = 0;

    while (1) {
        uint32_t ins = buttons_read();
        int note_index = msb_index(ins & 0x1FFF);

        /* If both octave buttons are pressed, we're in glide factor mode */
        if ((ins &  (OCTAVE_UP | OCTAVE_DN)) == (OCTAVE_UP | OCTAVE_DN)) {
            NOTE_OFF();

            /* If a note is being pressed, change the glide factor. Otherwise, do nothing */
            /* LEDs are all on if no key is pressed, otherwise, turn them all off */
            if (note_index != -1 ) {
                leds_set(0);
                glide_factor = 1.0f / ((note_index * 10) + 1);
            } else {
                leds_set(0x1F);
            }
        } else {
            /* Normal note mode. Process octave buttons, then process main keyboard keys */
            process_octave_buttons(ins, time_ctr);

            leds_set(0x1 << current_octave);

            if (note_index < 0) {
                NOTE_OFF();
            } else {
                int full_note_index = (current_octave * 12) + note_index;
                target_freq = note_freqs[full_note_index];
                NOTE_ON();
            }

            current_freq += (target_freq - current_freq) * glide_factor;

            wave_set_freq(current_freq);
        }

        sleep_ms(1);
        time_ctr += 1;
    }
}