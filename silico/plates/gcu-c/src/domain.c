#include "gcu/defaults.h"
#include "gcu/domain.h"
#include "gcu/version.h"

#include <stdio.h>
#include <string.h>

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
  st->last_blink_ms = (hal && hal->now_ms) ? hal->now_ms(hal) : 0;
  st->parked = 0;
  st->reboot_pending = 0;
}

static void toggle_led(gcu_state_t *st) {
  st->led_on = !st->led_on;
  if (st->hal && st->hal->set_led) {
    st->hal->set_led(st->hal, st->led_on);
  }
}

void gcu_tick(gcu_state_t *st) {
  st->tick_count += 1;
  /* After `repl` the host owns the console and the outputs stay parked —
   * do not resume driving the product face until the next boot. */
  if (st->parked) {
    return;
  }
  if (st->hal && st->hal->now_ms) {
    /* Wall-clock blink: robust to variable tick latency. All millisecond
     * math stays in int64_t — `long` is 32-bit on ESP32 (see hal.h). */
    int64_t now = st->hal->now_ms(st->hal);
    if (now - st->last_blink_ms >= (int64_t)st->tick_sleep_ms) {
      st->last_blink_ms = now;
      toggle_led(st);
    }
  } else {
    toggle_led(st); /* no clock: blink per tick */
  }
}

int gcu_tick_sleep_ms(const gcu_state_t *st) { return st->tick_sleep_ms; }

/* ---------------------------------------------------------------- link --- */

static const char *skip_ws(const char *s) {
  while (*s == ' ' || *s == '\t' || *s == '\r' || *s == '\n') {
    s++;
  }
  return s;
}

/* Whole-token match: "identity" hits, "identityX" and "id" do not. */
static int token_is(const char *s, const char *word) {
  size_t n = strlen(word);
  if (strncmp(s, word, n) != 0) {
    return 0;
  }
  return *skip_ws(s + n) == '\0';
}

gcu_cmd_t gcu_parse_command(const char *line) {
  if (!line) {
    return GCU_CMD_NONE;
  }
  const char *p = skip_ws(line);
  if (*p == '\0') {
    return GCU_CMD_NONE;
  }
  if (token_is(p, "identity")) {
    return GCU_CMD_IDENTITY;
  }
  if (token_is(p, "repl")) {
    return GCU_CMD_REPL;
  }
  if (token_is(p, "reboot")) {
    return GCU_CMD_REBOOT;
  }
  return GCU_CMD_UNKNOWN;
}

static void park_outputs(gcu_state_t *st) {
  if (!st || !st->hal) {
    return;
  }
  if (st->hal->set_led) {
    st->hal->set_led(st->hal, 0);
  }
  st->led_on = 0;
  /* Board backend quiets anything else it drives (speaker, strips, motion). */
  if (st->hal->park_outputs) {
    st->hal->park_outputs(st->hal);
  }
}

int gcu_handle_command(gcu_state_t *st, const char *line, char *out,
                       int out_len) {
  if (!st || !out || out_len < 16) {
    return 0;
  }
  switch (gcu_parse_command(line)) {
  case GCU_CMD_IDENTITY:
    gcu_identity_line(out, out_len);
    return 1;
  case GCU_CMD_REPL:
    park_outputs(st);
    st->parked = 1;
    snprintf(out, (size_t)out_len, "ok repl");
    return 1;
  case GCU_CMD_REBOOT:
    park_outputs(st);
    st->parked = 1;
    /* main.c flushes this reply, then calls hal->reboot. */
    st->reboot_pending = 1;
    snprintf(out, (size_t)out_len, "ok reboot");
    return 1;
  case GCU_CMD_UNKNOWN:
    /* Fail closed with a short error; never a multi-line help essay. */
    snprintf(out, (size_t)out_len, "err unknown");
    return 1;
  case GCU_CMD_NONE:
  default:
    return 0;
  }
}
