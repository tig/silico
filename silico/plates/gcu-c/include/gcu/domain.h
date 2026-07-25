#ifndef GCU_DOMAIN_H
#define GCU_DOMAIN_H

#include "gcu/hal.h"

#include <stdint.h>

typedef struct {
  gcu_hal_t *hal;
  int tick_count;
  int led_on;
  int tick_sleep_ms;
  int64_t last_blink_ms; /* wall-clock blink edge; unused without now_ms */
} gcu_state_t;

void gcu_identity_line(char *out, int out_len);
void gcu_init(gcu_state_t *st, gcu_hal_t *hal);
void gcu_tick(gcu_state_t *st);
int gcu_tick_sleep_ms(const gcu_state_t *st);

#endif
