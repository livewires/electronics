/**
 * Copyright (c) 2020 Raspberry Pi (Trading) Ltd.
 *
 * SPDX-License-Identifier: BSD-3-Clause
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

int dma_chan;
uint pwm_slice_num;


uint32_t phase_increment_per_sample;

#define WAVE_PIN 16

#define CAP_PIN 15

uint16_t samples[2048];


void dma_irh() {
    dma_hw->ch[dma_chan].al1_read_addr = (uint32_t) sineLookupTable;
    dma_hw->ints0 = (0x1 << dma_chan);
    dma_channel_start(dma_chan);
}

void set_freq(float freq) {
    /* times by 128 for added precision when cast to integer */
    uint64_t fp = (uint32_t) (freq * 128);
    /* times by 512 for number of samples in sine table */
    phase_increment_per_sample = (fp << 9) / 40690;
}

void on_pwm_wrap() {
    static uint32_t sample_num = 0;
    static uint64_t phase = 0;
    sample_num += 1;

    // Clear the interrupt flag that brought us here
    pwm_clear_irq(pwm_slice_num);

    phase += phase_increment_per_sample;

    pwm_set_chan_level(pwm_slice_num, PWM_CHAN_A, sineLookupTable[(phase >> 7) & 0x1FF]);
}

int main() {

    gpio_set_function(WAVE_PIN, GPIO_FUNC_PWM);

    set_freq(100);


    pwm_slice_num = pwm_gpio_to_slice_num(WAVE_PIN);

    pwm_clear_irq(pwm_slice_num);
    pwm_set_irq_enabled(pwm_slice_num, true);
    irq_set_exclusive_handler(PWM_DEFAULT_IRQ_NUM(), on_pwm_wrap);
    irq_set_enabled(PWM_DEFAULT_IRQ_NUM(), true);

    // Get some sensible defaults for the slice configuration. By default, the
    // counter is allowed to wrap over its maximum range (0 to 2**16-1)
    pwm_config config = pwm_get_default_config();
    // Set divider, reduces counter clock to sysclock/this value
    // Divide 125MHz by 3 and you get 41.6MHz
    pwm_config_set_clkdiv(&config, 3.f);
    // Load the configuration into our PWM slice, and set it running.
    // 41.6MHz / 1024 = 40.7kHz effective sample rate
    pwm_config_set_wrap(&config, 1023);
    // Uncomment this to start GPIO working again
    pwm_init(pwm_slice_num, &config, true);


    gpio_init(PICO_DEFAULT_LED_PIN);
    gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);

    gpio_init(CAP_PIN);
    gpio_set_pulls(CAP_PIN, false, false);
    gpio_set_dir(CAP_PIN, GPIO_OUT);
    gpio_put(CAP_PIN, true);
    gpio_set_dir(CAP_PIN, GPIO_IN);

    float start_freq = 55;
    float end_freq = 440;
    float target_frequency;

    while (1) {
        for (int step = 0; step < 200; step ++)
        {
            target_frequency = start_freq + (end_freq - start_freq) * ((float) step / 200);
            set_freq(target_frequency);


            gpio_set_dir(CAP_PIN, GPIO_OUT);
            sleep_us(10);
            gpio_set_dir(CAP_PIN, GPIO_IN);
            sleep_us(20);
            gpio_put(PICO_DEFAULT_LED_PIN, gpio_get(CAP_PIN));
            sleep_ms(10);
        }

        target_frequency = end_freq;
        end_freq = start_freq;
        start_freq = target_frequency;
    }








    // dma_chan = dma_claim_unused_channel(true);

    // dma_channel_config pwm_dma_chan_config = dma_channel_get_default_config(dma_chan);
    // channel_config_set_transfer_data_size(&pwm_dma_chan_config, DMA_SIZE_16);
    // channel_config_set_read_increment(&pwm_dma_chan_config, true);
    // channel_config_set_write_increment(&pwm_dma_chan_config, false);
    // channel_config_set_dreq(&pwm_dma_chan_config, DREQ_PWM_WRAP0 + pwm_slice_num);

    // dma_channel_configure(
    //     dma_chan,
    //     &pwm_dma_chan_config,
    //     &pwm_hw->slice[pwm_slice_num].cc,
    //     sineLookupTable,
    //     SINE_NUM_SAMPLES,
    //     false
    // );

    // dma_channel_set_irq0_enabled(dma_chan, true);
    // irq_set_exclusive_handler(DMA_IRQ_0, dma_irh);
    // irq_set_enabled(DMA_IRQ_0, true);

    // dma_channel_start(dma_chan);



    // Everything after this point happens in the PWM interrupt handler, so we
    // can twiddle our thumbs
    while (1) {
        for (int octave = 1; octave < 8; octave++) {

        }
    }


}