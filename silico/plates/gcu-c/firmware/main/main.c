#include "gcu/defaults.h"
#include "gcu/domain.h"
#include "gcu/hal.h"
#include "gcu/version.h"
#include "hal_board.h"

#include <ctype.h>
#include <stdio.h>
#include <string.h>

/*
 * Identity on the link (#78 / #79): boot-print alone is not enough for
 * silico inspect after the greeting scrolls past. The app must also answer
 * the host word "identity" (CR/LF framed) with fw_name=… fw_version=….
 */
static void drain_identity_command(void) {
  static char line[48];
  static int n;
  int c;
  while ((c = getchar()) != EOF) {
    if (c == '\r' || c == '\n') {
      if (n > 0) {
        line[n] = '\0';
        /* trim */
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
}

void app_main(void) {
  char id[64];
  gcu_state_t st;
  gcu_hal_t *hal = gcu_make_board_hal();

  gcu_identity_line(id, (int)sizeof id);
  printf("%s\n", id);
  fflush(stdout);

  gcu_init(&st, hal);
  for (;;) {
    /* Non-blocking when the console VFS is set non-blocking by the IDF
     * monitor path; on blocking consoles this still works after a host
     * line (inspect) arrives — prefer product apps that keep the door open. */
    drain_identity_command();
    gcu_tick(&st);
    if (hal && hal->delay_ms) {
      hal->delay_ms(hal, gcu_tick_sleep_ms(&st));
    }
  }
}
