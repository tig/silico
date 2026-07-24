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
 * Identity on the link (#78 / #79): boot-print alone is not enough for
 * silico inspect after the greeting scrolls past. The app must also answer
 * the host word "identity" (CR/LF framed) with fw_name=… fw_version=….
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

static void drain_identity_command(void) {
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
        line[n] = '\0';
        char *p = line;
        while (*p && isspace((unsigned char)*p)) {
          p++;
        }
        if (strcmp(p, "identity") == 0) {
          char id[64];
          gcu_identity_line(id, (int)sizeof id);
          printf("%s\n", id);
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
  /* Clear sticky errno from EAGAIN/EWOULDBLOCK after empty non-block read. */
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
    drain_identity_command();
    gcu_tick(&st);
    if (hal && hal->delay_ms) {
      hal->delay_ms(hal, gcu_tick_sleep_ms(&st));
    }
  }
}
