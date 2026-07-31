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
  int parked;            /* `repl` released product ownership of outputs */
  int reboot_pending;    /* `reboot` acked; main resets after flushing */
} gcu_state_t;

/* Link command surface.
 *
 * Parsing and dispatch live HERE, in portable domain code, not in
 * firmware/main.c — otherwise "protocol parsing" cannot be host-tested and
 * the escape hatch is only ever exercised on metal. See host/test_protocol.c.
 * Products extend this enum; keep the shipped surface equal to what the
 * product spec declares. */
typedef enum {
  GCU_CMD_NONE = 0, /* blank line — no reply */
  GCU_CMD_IDENTITY,
  GCU_CMD_REPL,
  GCU_CMD_REBOOT,
  GCU_CMD_UNKNOWN, /* fails closed with a short error */
} gcu_cmd_t;

void gcu_identity_line(char *out, int out_len);
void gcu_init(gcu_state_t *st, gcu_hal_t *hal);
void gcu_tick(gcu_state_t *st);
int gcu_tick_sleep_ms(const gcu_state_t *st);

gcu_cmd_t gcu_parse_command(const char *line);

/* Handle one link line. Returns 1 when *out holds a reply to write, else 0.
 * `repl` and `reboot` park outputs through the HAL before replying. */
int gcu_handle_command(gcu_state_t *st, const char *line, char *out,
                       int out_len);

#endif
