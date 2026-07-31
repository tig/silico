#include "gcu/defaults.h"
#include "gcu/domain.h"
#include "gcu/hal.h"
#include "gcu/version.h"
#include "hal_board.h"

#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

/*
 * Link plumbing only. Parsing and dispatch live in portable domain code
 * (gcu_handle_command) so the command surface is host-testable — this file
 * moves bytes, it does not decide what a command means.
 *
 * Identity on the link (#78 / #79): boot-print alone is not enough for
 * silico inspect after the greeting scrolls past. The app must also answer
 * the host word "identity" (CR/LF framed) with fw_name=… fw_version=….
 * `repl` and `reboot` are required alongside it — a build without the
 * escape hatch cannot be reclaimed without hardware gymnastics.
 *
 * stdin MUST be non-blocking before the forever loop. Blocking getchar()
 * would park app_main and kill the product face (tick/LED) until a host
 * line arrives.
 */
static int g_stdin_nonblock;

static void stdin_set_nonblocking(void) {
  int flags = fcntl(STDIN_FILENO, F_GETFL, 0);
  if (flags < 0) {
    g_stdin_nonblock = 0;
    return;
  }
  if (fcntl(STDIN_FILENO, F_SETFL, flags | O_NONBLOCK) == 0) {
    g_stdin_nonblock = 1;
  } else {
    g_stdin_nonblock = 0;
  }
}

static void drain_link_commands(gcu_state_t *st) {
  static char line[48];
  static int n;
  int c;

  if (!g_stdin_nonblock) {
    return; /* never block the product face */
  }

  /* Drain only ready bytes; empty stdin yields EOF/EAGAIN immediately. */
  while ((c = getchar()) != EOF) {
    if (c == '\r' || c == '\n') {
      if (n > 0) {
        char reply[80];
        line[n] = '\0';
        if (gcu_handle_command(st, line, reply, (int)sizeof reply)) {
          printf("%s\n", reply);
          fflush(stdout);
        }
        n = 0;
      }
      continue;
    }
    if (n < (int)sizeof(line) - 1) {
      line[n++] = (char)c;
    } else {
      n = 0; /* overflow: drop */
    }
  }
  /* Clear sticky stream state after empty non-blocking reads: EOF/error
   * flags latch on FILE* and errno keeps EAGAIN. Without both resets the
   * NEXT drain can see a phantom EOF and never read again (#87). */
  clearerr(stdin);
  if (errno == EAGAIN || errno == EWOULDBLOCK) {
    errno = 0;
  }
}

void app_main(void) {
  char id[64];
  gcu_state_t st;
  /* HAL init must stay reachable from app_main (silico gate checks this).
   * Do not move the forever loop without gcu_make_board_hal + gcu_init (#79). */
  gcu_hal_t *hal = gcu_make_board_hal();

  gcu_identity_line(id, (int)sizeof id);
  printf("%s\n", id);
  fflush(stdout);

  stdin_set_nonblocking();
  if (!g_stdin_nonblock) {
    printf("WARN: stdin not non-blocking; identity knock drain disabled "
           "(product face tick continues)\n");
    fflush(stdout);
  }

  gcu_init(&st, hal);
  for (;;) {
    drain_link_commands(&st);
    if (st.reboot_pending) {
      /* Reply already flushed above; outputs already parked by the domain. */
      st.reboot_pending = 0;
      if (hal && hal->reboot) {
        hal->reboot(hal);
      }
    }
    gcu_tick(&st);
    if (hal && hal->delay_ms) {
      hal->delay_ms(hal, gcu_tick_sleep_ms(&st));
    }
  }
}
