#ifndef GCU_HAL_H
#define GCU_HAL_H

/* Portable HAL contract — no device headers here. */

#include <stdint.h>

typedef struct gcu_hal gcu_hal_t;

struct gcu_hal {
  void (*set_led)(gcu_hal_t *self, int on);
  void (*delay_ms)(gcu_hal_t *self, int ms);
  /* Monotonic wall clock in milliseconds since boot, or NULL if the board
   * has none. MUST be int64_t: on ESP32 (ILP32) `long` is 32 bits, so
   * millisecond math in `long` overflows in <10 h and wraps at ~24.8 days.
   * Host `long` is 64-bit and hides the trap — see host/test_time.c. */
  int64_t (*now_ms)(gcu_hal_t *self);
  /* Escape hatch (optional hooks; NULL is tolerated).
   *
   * park_outputs: quiet every product output this board drives — speaker to
   * a parked level, LEDs/strips off, actuators safe. Called for `repl` and
   * `reboot` so the operator never gets a redeploy that is still singing.
   * Extend this on the product backend as outputs are added; the domain
   * cannot know what your board drives.
   *
   * reboot: hard reset (e.g. esp_restart). The domain never calls this
   * directly — it sets gcu_state_t.reboot_pending so the link reply can be
   * flushed first. See firmware/main/main.c. */
  void (*park_outputs)(gcu_hal_t *self);
  void (*reboot)(gcu_hal_t *self);
};

#endif
