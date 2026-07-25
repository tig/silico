/* Time contract: hal now_ms is int64_t milliseconds (#87).
 *
 * On ESP32 (Xtensa ILP32) `long` is 32 bits: millisecond math in `long`
 * overflows in <10 hours of uptime arithmetic and wraps at ~24.8 days.
 * Host `long` is 64-bit, so a host test only catches the trap if it seeds
 * the clock PAST 2^31 — which this test does. Keep the seed; do not
 * "simplify" it to small numbers.
 */
#include "gcu/defaults.h"
#include "gcu/domain.h"
#include "gcu/hal.h"

#include <stdint.h>
#include <stdio.h>

static int led;
static int led_writes;
static int64_t fake_now;

static void set_led(gcu_hal_t *self, int on) {
  (void)self;
  led = on;
  led_writes++;
}

static void delay_ms(gcu_hal_t *self, int ms) {
  (void)self;
  (void)ms;
}

static int64_t now_ms(gcu_hal_t *self) {
  (void)self;
  return fake_now;
}

int main(void) {
  gcu_hal_t hal = {.set_led = set_led, .delay_ms = delay_ms, .now_ms = now_ms};
  gcu_state_t st;
  const int period = GCU_DEFAULTS.tick_sleep_ms;

  /* Seed past 2^31 ms so 32-bit intermediate math would go negative. */
  fake_now = (INT64_C(1) << 31) + 12345;
  gcu_init(&st, &hal);

  /* Same instant: no blink edge yet. */
  led_writes = 0;
  gcu_tick(&st);
  if (led_writes != 0) {
    fprintf(stderr, "blinked with no elapsed time\n");
    return 1;
  }

  /* One period later: exactly one toggle, on. */
  fake_now += period;
  gcu_tick(&st);
  if (led_writes != 1 || led != 1) {
    fprintf(stderr, "expected one on-toggle after %d ms\n", period);
    return 1;
  }

  /* Sub-period ticks must not toggle (wall clock, not tick count). */
  fake_now += period / 2;
  gcu_tick(&st);
  if (led_writes != 1) {
    fprintf(stderr, "toggled before period elapsed\n");
    return 1;
  }

  /* Large jump (past another 2^31 ms) still behaves: one toggle. */
  fake_now += (INT64_C(1) << 31) + period;
  gcu_tick(&st);
  if (led_writes != 2 || led != 0) {
    fprintf(stderr, "64-bit delta mishandled after big clock jump\n");
    return 1;
  }

  /* Fallback: no now_ms hook -> every tick toggles (plate default). */
  {
    gcu_hal_t hal2 = {.set_led = set_led, .delay_ms = delay_ms};
    gcu_state_t st2;
    gcu_init(&st2, &hal2);
    led_writes = 0;
    gcu_tick(&st2);
    gcu_tick(&st2);
    if (led_writes != 2) {
      fprintf(stderr, "tick fallback broken without now_ms\n");
      return 1;
    }
  }

  printf("OK time64\n");
  return 0;
}
