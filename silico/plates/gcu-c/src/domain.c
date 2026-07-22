#include "gcu/defaults.h"
#include "gcu/domain.h"
#include "gcu/version.h"

#include <stdio.h>

void gcu_identity_line(char *out, int out_len) {
  if (!out || out_len < 8) {
    return;
  }
  snprintf(out, (size_t)out_len, "fw_name=%s fw_version=%s", GCU_FW_NAME,
           GCU_FW_VERSION);
}

void gcu_init(gcu_state_t *st, gcu_hal_t *hal) {
  st->hal = hal;
  st->tick_count = 0;
  st->led_on = 0;
  st->tick_sleep_ms = GCU_DEFAULTS.tick_sleep_ms;
}

void gcu_tick(gcu_state_t *st) {
  st->tick_count += 1;
  st->led_on = !st->led_on;
  if (st->hal && st->hal->set_led) {
    st->hal->set_led(st->hal, st->led_on);
  }
}

int gcu_tick_sleep_ms(const gcu_state_t *st) { return st->tick_sleep_ms; }
