/* Link command surface — host test (no hardware).
 *
 * Why this file exists: the escape hatch (`repl` / `reboot`) is a product
 * requirement, and an escape hatch that is only ever exercised on metal is
 * the one that turns out to be missing at the worst moment. Parsing and
 * dispatch live in src/domain.c precisely so this test can run on the host.
 *
 * Extend this alongside the product's declared command surface: every command
 * the product spec lists should have a row here, including the ones that must
 * FAIL (unknown input fails closed with a short error, not a help essay).
 */
#include "gcu/defaults.h"
#include "gcu/domain.h"
#include "gcu/hal.h"
#include "gcu/version.h"

#include <stdio.h>
#include <string.h>

static int led_state;
static int parked_calls;
static int reboot_calls;

static void set_led(gcu_hal_t *self, int on) {
  (void)self;
  led_state = on;
}

static void delay_ms(gcu_hal_t *self, int ms) {
  (void)self;
  (void)ms;
}

static void park_outputs(gcu_hal_t *self) {
  (void)self;
  parked_calls++;
}

static void board_reboot(gcu_hal_t *self) {
  (void)self;
  reboot_calls++;
}

static int fail(const char *msg) {
  fprintf(stderr, "FAIL: %s\n", msg);
  return 1;
}

int main(void) {
  gcu_hal_t hal = {
      .set_led = set_led,
      .delay_ms = delay_ms,
      .park_outputs = park_outputs,
      .reboot = board_reboot,
  };
  gcu_state_t st;
  char reply[80];

  /* --- parsing: whole tokens, surrounding whitespace tolerated --- */
  if (gcu_parse_command("identity") != GCU_CMD_IDENTITY) {
    return fail("identity not parsed");
  }
  if (gcu_parse_command("  repl \r\n") != GCU_CMD_REPL) {
    return fail("repl not parsed with surrounding whitespace");
  }
  if (gcu_parse_command("reboot") != GCU_CMD_REBOOT) {
    return fail("reboot not parsed");
  }
  if (gcu_parse_command("") != GCU_CMD_NONE ||
      gcu_parse_command("   ") != GCU_CMD_NONE) {
    return fail("blank line should be NONE");
  }
  if (gcu_parse_command(NULL) != GCU_CMD_NONE) {
    return fail("NULL line should be NONE");
  }
  /* Prefix/substring must not match a command. */
  if (gcu_parse_command("identityX") != GCU_CMD_UNKNOWN ||
      gcu_parse_command("rep") != GCU_CMD_UNKNOWN) {
    return fail("partial token matched a command");
  }

  /* --- identity --- */
  gcu_init(&st, &hal);
  if (!gcu_handle_command(&st, "identity", reply, (int)sizeof reply)) {
    return fail("identity produced no reply");
  }
  if (strstr(reply, "fw_name=") == NULL || strstr(reply, "fw_version=") == NULL) {
    return fail("identity reply missing fw_name/fw_version");
  }
  if (st.parked) {
    return fail("identity must not park outputs");
  }

  /* --- blank line: no reply, no chatter on the link --- */
  if (gcu_handle_command(&st, "   ", reply, (int)sizeof reply)) {
    return fail("blank line should produce no reply");
  }

  /* --- unknown fails closed and short --- */
  if (!gcu_handle_command(&st, "sing", reply, (int)sizeof reply)) {
    return fail("unknown command produced no reply");
  }
  if (strncmp(reply, "err", 3) != 0) {
    return fail("unknown command should reply with a short error");
  }
  if (st.parked) {
    return fail("unknown command must not park outputs");
  }

  /* --- repl parks outputs and releases the console --- */
  gcu_init(&st, &hal);
  led_state = 1;
  parked_calls = 0;
  if (!gcu_handle_command(&st, "repl", reply, (int)sizeof reply)) {
    return fail("repl produced no reply");
  }
  if (!st.parked) {
    return fail("repl did not set parked");
  }
  if (parked_calls != 1) {
    return fail("repl did not call hal park_outputs");
  }
  if (led_state != 0) {
    return fail("repl left the LED driven");
  }
  if (st.reboot_pending) {
    return fail("repl must not request a reboot");
  }
  /* Parked means parked: further ticks do not resume driving the face. */
  led_state = 1;
  gcu_tick(&st);
  gcu_tick(&st);
  if (led_state != 1) {
    return fail("tick drove outputs after repl parked them");
  }

  /* --- reboot parks, acks, and defers the reset to main --- */
  gcu_init(&st, &hal);
  parked_calls = 0;
  reboot_calls = 0;
  if (!gcu_handle_command(&st, "reboot", reply, (int)sizeof reply)) {
    return fail("reboot produced no reply");
  }
  if (parked_calls != 1) {
    return fail("reboot did not park outputs");
  }
  if (!st.reboot_pending) {
    return fail("reboot did not set reboot_pending");
  }
  if (reboot_calls != 0) {
    return fail("domain must not reset before the reply is flushed");
  }

  /* --- undersized reply buffer is refused, not overflowed --- */
  gcu_init(&st, &hal);
  {
    char tiny[4];
    if (gcu_handle_command(&st, "identity", tiny, (int)sizeof tiny)) {
      return fail("undersized buffer should be refused");
    }
  }

  printf("OK protocol identity+repl+reboot+unknown\n");
  return 0;
}
